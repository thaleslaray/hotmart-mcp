from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx


class ApiError(Exception):
    def __init__(self, status_code: int, message: str, response: dict | None = None):
        self.status_code = status_code
        self.message = message
        self.response = response or {}
        super().__init__(f"[{status_code}] {message}")


class AuthError(ApiError):
    pass


class RateLimitError(ApiError):
    def __init__(self, retry_after: float | None = None, **kwargs: Any):
        self.retry_after = retry_after
        super().__init__(**kwargs)


class HotmartClient:
    BASE_URL = "https://developers.hotmart.com"
    TOKEN_URL = "https://api-sec-vlc.hotmart.com/security/oauth/token"
    RATE_LIMIT = 500
    MAX_RETRIES = 3

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        basic_auth: str | None = None,
        base_url: str | None = None,
    ):
        self._client_id = client_id or os.environ["HOTMART_CLIENT_ID"]
        self._client_secret = client_secret or os.environ["HOTMART_CLIENT_SECRET"]
        self._basic_auth = basic_auth or os.environ["HOTMART_BASIC_AUTH"]
        self._base_url = (base_url or self.BASE_URL).rstrip("/")

        self._access_token: str | None = None
        self._token_expires_at: float = 0
        self._token_lock = asyncio.Lock()
        self._http: httpx.AsyncClient | None = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=httpx.Timeout(30.0),
            )
        return self._http

    async def close(self) -> None:
        if self._http and not self._http.is_closed:
            await self._http.aclose()
            self._http = None

    async def __aenter__(self) -> HotmartClient:
        return self

    async def __aexit__(self, *_exc: Any) -> None:
        await self.close()

    async def _ensure_token(self) -> str:
        if self._access_token and time.monotonic() < self._token_expires_at:
            return self._access_token

        async with self._token_lock:
            if self._access_token and time.monotonic() < self._token_expires_at:
                return self._access_token

            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as auth_client:
                resp = await auth_client.post(
                    self.TOKEN_URL,
                    data={"grant_type": "client_credentials"},
                    headers={
                        "Authorization": f"Basic {self._basic_auth}",
                    },
                )

            if resp.status_code in (401, 403):
                raise AuthError(
                    status_code=resp.status_code,
                    message="Failed to acquire access token",
                    response=resp.json() if resp.content else None,
                )

            if resp.status_code != 200:
                raise ApiError(
                    status_code=resp.status_code,
                    message="Token request failed",
                    response=resp.json() if resp.content else None,
                )

            data = resp.json()
            self._access_token = data["access_token"]
            expires_in = data.get("expires_in", 172799)
            self._token_expires_at = time.monotonic() + (expires_in * 0.8)
            return self._access_token  # type: ignore[return-value]

    async def _build_headers(self) -> dict[str, str]:
        token = await self._ensure_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code < 400:
            return

        body = resp.json() if resp.content else {}

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            raise RateLimitError(
                retry_after=float(retry_after) if retry_after else None,
                status_code=429,
                message="Rate limit exceeded",
                response=body,
            )

        if resp.status_code in (401, 403):
            self._access_token = None
            self._token_expires_at = 0
            raise AuthError(
                status_code=resp.status_code,
                message=body.get("message", "Authentication failed"),
                response=body,
            )

        raise ApiError(
            status_code=resp.status_code,
            message=body.get("message", f"HTTP {resp.status_code}"),
            response=body,
        )

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        select: list[str] | None = None,
    ) -> dict[str, Any]:
        if params is None:
            params = {}
        if select:
            params["select"] = ",".join(select)

        backoff = 1.0
        resp: httpx.Response | None = None

        for attempt in range(self.MAX_RETRIES):
            headers = await self._build_headers()
            http = await self._get_http()

            resp = await http.request(
                method=method.upper(),
                url=path,
                params=params or None,
                json=json,
                headers=headers,
            )

            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else backoff
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(wait)
                    backoff *= 2
                    continue
                self._raise_for_status(resp)

            if resp.status_code == 401 and attempt == 0:
                self._access_token = None
                self._token_expires_at = 0
                continue

            break

        assert resp is not None, "No response received after retries"
        self._raise_for_status(resp)

        if resp.status_code == 204 or not resp.content:
            return {}

        return resp.json()

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        select: list[str] | None = None,
    ) -> dict[str, Any]:
        return await self._request("GET", path, params=params, select=select)

    async def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._request("POST", path, params=params, json=json)

    async def put(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._request("PUT", path, params=params, json=json)

    async def patch(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._request("PATCH", path, params=params, json=json)

    async def delete(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self._request("DELETE", path, params=params)

    async def get_all_pages(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        select: list[str] | None = None,
        items_key: str = "items",
    ) -> list[dict[str, Any]]:
        params = dict(params) if params else {}
        all_items: list[dict[str, Any]] = []

        while True:
            data = await self.get(path, params=params, select=select)
            items = data.get(items_key, [])
            all_items.extend(items)

            next_token = (data.get("page_info") or {}).get("next_page_token")
            if not next_token:
                break

            params["page_token"] = next_token

        return all_items
