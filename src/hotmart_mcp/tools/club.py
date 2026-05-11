"""Auto-generated Hotmart API tools — club."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["hotmart_modules_list", "hotmart_module_pages_list", "hotmart_students_list", "hotmart_student_progress_get"]


async def hotmart_modules_list(
    subdomain: str,
    is_extra: Optional[bool] = None,
    select: Optional[str] = None,
) -> str:
    """Get Modules. Lists module containers only. To get pages inside a module, use `hotmart_module_pages_list` with the module_id.
    
    Args:
        subdomain: Members area subdomain (the slug from `hotmart.com/club/<slug>` URL)
        is_extra: Filtrar módulos extras
        select: Custom field selection in response"""
    endpoint = "/club/api/v1/modules"
    params = {}
    if subdomain is not None:
        params["subdomain"] = subdomain
    if is_extra is not None:
        params["is_extra"] = is_extra
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_module_pages_list(
    module_id: str,
    subdomain: str,
    select: Optional[str] = None,
) -> str:
    """Get Pages. Example: hotmart_module_pages_list(module_id='…'). Requires module_id from `hotmart_modules_list` first.
    
    Args:
        module_id: Module ID
        subdomain: Members area subdomain (the slug from `hotmart.com/club/<slug>` URL)
        select: Custom field selection in response"""
    endpoint = f"/club/api/v1/modules/{module_id}/pages"
    params = {}
    if subdomain is not None:
        params["subdomain"] = subdomain
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_students_list(
    subdomain: str,
    email: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Get Students.
    
    Args:
        subdomain: Members area subdomain (the slug from `hotmart.com/club/<slug>` URL)
        email: Email do aluno
        select: Custom field selection in response"""
    endpoint = "/club/api/v1/users"
    params = {}
    if subdomain is not None:
        params["subdomain"] = subdomain
    if email is not None:
        params["email"] = email
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_student_progress_get(
    user_id: str,
    subdomain: str,
    select: Optional[str] = None,
) -> str:
    """Get Student Progress. Example: hotmart_student_progress_get(user_id='…').
    
    Args:
        user_id: ID do aluno
        subdomain: Members area subdomain (the slug from `hotmart.com/club/<slug>` URL)
        select: Custom field selection in response"""
    endpoint = f"/club/api/v1/users/{user_id}/lessons"
    params = {}
    if subdomain is not None:
        params["subdomain"] = subdomain
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)
