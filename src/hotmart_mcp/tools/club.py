"""Auto-generated Hotmart API tools — club."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["get_modules", "get_module_pages", "get_students", "get_student_progress"]


async def get_modules(
    subdomain: str,
    is_extra: Optional[bool] = None,
    select: Optional[str] = None,
) -> str:
    """Get Modules
    
    Retorna os módulos da área de membros.
    
    Args:
        subdomain: Subdomínio da área de membros
        is_extra: Filtrar módulos extras
        select: Seleção de campos customizados na resposta"""
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


async def get_module_pages(
    module_id: str,
    subdomain: str,
    select: Optional[str] = None,
) -> str:
    """Get Pages
    
    Retorna as páginas (aulas) de um módulo.
    
    Args:
        module_id: ID do módulo
        subdomain: Subdomínio da área de membros
        select: Seleção de campos customizados na resposta"""
    endpoint = f"/club/api/v1/modules/{module_id}/pages"
    params = {}
    if subdomain is not None:
        params["subdomain"] = subdomain
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def get_students(
    subdomain: str,
    email: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Get Students
    
    Retorna os alunos da área de membros.
    
    Args:
        subdomain: Subdomínio da área de membros
        email: E-mail do aluno
        select: Seleção de campos customizados na resposta"""
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


async def get_student_progress(
    user_id: str,
    subdomain: str,
    select: Optional[str] = None,
) -> str:
    """Get Student Progress
    
    Retorna o progresso de um aluno nas aulas.
    
    Args:
        user_id: ID do aluno
        subdomain: Subdomínio da área de membros
        select: Seleção de campos customizados na resposta"""
    endpoint = f"/club/api/v1/users/{user_id}/lessons"
    params = {}
    if subdomain is not None:
        params["subdomain"] = subdomain
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)
