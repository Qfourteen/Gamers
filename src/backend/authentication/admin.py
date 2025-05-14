from fastapi import APIRouter, status, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import math
import os

from src.backend.models.user import User

from src.backend.schemas.authentication import UserResponse, AdminUserAction

from . import (
    get_user, get_current_user, check_admin_permissions, COOKIE_NAME
)

# 템플릿 디렉토리 설정
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "templates")
templates = Jinja2Templates(directory=templates_dir)

admin_router = APIRouter(prefix="/admin")

@admin_router.post("/users/disable", response_model=UserResponse)
async def admin_disable_user(
        action: AdminUserAction,
        request: Request
):
    """
    관리자가 다른 사용자의 계정을 비활성화합니다.

    Args:
        action: 비활성화할 사용자 이름과 이유
        request: HTTP 요청 객체

    Returns:
        비활성화된 사용자 정보

    Raises:
        HTTPException: 관리자가 아니거나, 사용자를 찾을 수 없거나, 이미 비활성화된 경우
    """
    current_user = await get_current_user(request)

    # 관리자 권한 확인
    await check_admin_permissions(current_user)

    # 비활성화할 사용자 조회
    target_user = await get_user(action.username)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 이미 비활성화된 계정인지 확인
    if target_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already disabled"
        )

    # 계정 비활성화
    target_user.disabled = True
    target_user.disabled_reason = action.reason or f"Account disabled by admin: {current_user.username}"
    target_user.disabled_at = datetime.now(timezone.utc)
    target_user.disabled_by = current_user.username
    await target_user.save()

    return UserResponse(
        username=target_user.username,
        disabled=target_user.disabled,
        is_admin=target_user.is_admin,
        disabled_reason=target_user.disabled_reason,
        disabled_at=target_user.disabled_at
    )


@admin_router.post("/users/enable", response_model=UserResponse)
async def admin_enable_user(
        action: AdminUserAction,
        request: Request
):
    """
    관리자가 다른 사용자의 비활성화된 계정을 활성화합니다.

    Args:
        action: 활성화할 사용자 이름
        request: HTTP 요청 객체

    Returns:
        활성화된 사용자 정보

    Raises:
        HTTPException: 관리자가 아니거나, 사용자를 찾을 수 없거나, 이미 활성화된 경우
    """
    current_user = await get_current_user(request)

    # 관리자 권한 확인
    await check_admin_permissions(current_user)

    # 활성화할 사용자 조회
    target_user = await get_user(action.username)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 활성화된 계정인지 확인
    if not target_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already active"
        )

    # 계정 활성화
    target_user.disabled = False
    target_user.disabled_reason = None
    target_user.disabled_at = None
    target_user.disabled_by = None
    await target_user.save()

    return UserResponse(
        username=target_user.username,
        disabled=target_user.disabled,
        is_admin=target_user.is_admin,
        disabled_reason=target_user.disabled_reason,
        disabled_at=target_user.disabled_at
    )


@admin_router.post("/users/promote", response_model=UserResponse)
async def promote_to_admin(
        action: AdminUserAction,
        request: Request
):
    """
    관리자가 일반 사용자에게 관리자 권한을 부여합니다.

    Args:
        action: 관리자로 승격할 사용자 이름
        request: HTTP 요청 객체

    Returns:
        관리자로 승격된 사용자 정보

    Raises:
        HTTPException: 관리자가 아니거나, 사용자를 찾을 수 없거나, 이미 관리자인 경우
    """
    current_user = await get_current_user(request)

    # 관리자 권한 확인
    await check_admin_permissions(current_user)

    # 승격할 사용자 조회
    target_user = await get_user(action.username)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 이미 관리자인지 확인
    if target_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )

    # 관리자로 승격
    target_user.is_admin = True
    await target_user.save()

    return UserResponse(
        username=target_user.username,
        disabled=target_user.disabled,
        is_admin=target_user.is_admin,
        disabled_reason=target_user.disabled_reason,
        disabled_at=target_user.disabled_at
    )


@admin_router.post("/users/demote", response_model=UserResponse)
async def demote_from_admin(
        action: AdminUserAction,
        request: Request
):
    """
    관리자가 다른 관리자에게서 관리자 권한을 제거합니다.

    Args:
        action: 권한을 제거할 관리자 이름
        request: HTTP 요청 객체

    Returns:
        권한이 제거된 사용자 정보

    Raises:
        HTTPException: 관리자가 아니거나, 사용자를 찾을 수 없거나, 관리자가 아닌 경우
    """
    current_user = await get_current_user(request)

    # 관리자 권한 확인
    await check_admin_permissions(current_user)

    # 자기 자신의, 권한을 제거하려는 경우 방지
    if action.username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself"
        )

    # 대상 사용자 조회
    target_user = await get_user(action.username)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 관리자가 아닌지 확인
    if not target_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )

    # 관리자 권한 제거
    target_user.is_admin = False
    await target_user.save()

    return UserResponse(
        username=target_user.username,
        disabled=target_user.disabled,
        is_admin=target_user.is_admin,
        disabled_reason=target_user.disabled_reason,
        disabled_at=target_user.disabled_at
    )


class UserListItem(BaseModel):
    """사용자 목록 항목"""
    username: str
    disabled: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
    disabled_at: Optional[datetime]
    disabled_reason: Optional[str]
    disabled_by: Optional[str]


class UserFilter(BaseModel):
    """사용자 필터링 옵션"""
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None
    username_contains: Optional[str] = None
    limit: int = 50
    skip: int = 0


@admin_router.post("/users/list", response_model=list[UserListItem])
async def list_users(
        request: Request,
        filter_options: UserFilter = UserFilter(),
):
    """
    관리자용 사용자 목록 조회 API

    Args:
        filter_options: 필터링 옵션 (비활성화 여부, 관리자 여부, 사용자 이름 포함 문자열)
        request: HTTP 요청 객체

    Returns:
        필터링된 사용자 목록

    Raises:
        HTTPException: 관리자가 아닌 경우
    """
    current_user = await get_current_user(request)

    # 관리자 권한 확인
    await check_admin_permissions(current_user)

    # 기본 쿼리
    query = {}

    # 필터 적용
    if filter_options.disabled is not None:
        query["disabled"] = filter_options.disabled

    if filter_options.is_admin is not None:
        query["is_admin"] = filter_options.is_admin

    if filter_options.username_contains:
        # username에 특정 문자열 포함 검색
        query["username"] = {"$regex": filter_options.username_contains, "$options": "i"}

    # 사용자 목록 조회
    users = await User.find(query).sort(-User.created_at).skip(filter_options.skip).limit(
        filter_options.limit).to_list()

    # 응답 형식으로 변환
    result = []
    for user in users:
        result.append(UserListItem(
            username=user.username,
            disabled=user.disabled,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login,
            disabled_at=user.disabled_at,
            disabled_reason=user.disabled_reason,
            disabled_by=user.disabled_by
        ))

    return result


# 관리자 웹 대시보드 라우트
@admin_router.get("/", response_class=HTMLResponse)
async def admin_root(request: Request):
    """
    관리자 루트 페이지를 대시보드로 리다이렉트합니다.
    """
    return RedirectResponse(url="/admin/dashboard", status_code=303)


async def get_current_admin_user(request: Request):
    """
    현재 인증된 관리자 사용자를 가져옵니다.
    일반 사용자인 경우 로그인 페이지로 리다이렉트합니다.
    """
    try:
        user = await get_current_user(request)
        await check_admin_permissions(user)
        return user
    except HTTPException:
        return None


@admin_router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: Optional[User] = Depends(get_current_admin_user)):
    """
    관리자 대시보드 메인 페이지를 제공합니다.
    """
    if not current_user:
        return RedirectResponse(url="/", status_code=303)
    
    # 통계 데이터 조회
    total_users = await User.count()
    admin_users = await User.find(User.is_admin == True).count()
    disabled_users = await User.find(User.disabled == True).count()
    
    # 최근 가입한 사용자 목록 조회
    recent_users = await User.find().sort(-User.created_at).limit(10).to_list()
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "dashboard",
            "stats": {
                "total_users": total_users,
                "admin_users": admin_users,
                "disabled_users": disabled_users,
            },
            "recent_users": recent_users,
            "messages": []
        }
    )


@admin_router.get("/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    username_contains: Optional[str] = None,
    is_admin: Optional[str] = None,
    disabled: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_current_admin_user)
):
    """
    관리자 사용자 관리 페이지를 제공합니다.
    """
    if not current_user:
        return RedirectResponse(url="/", status_code=303)
    
    # 문자열 파라미터를 불리언으로 변환
    is_admin_bool = None
    if is_admin:
        is_admin_bool = is_admin.lower() == 'true'
    
    disabled_bool = None
    if disabled:
        disabled_bool = disabled.lower() == 'true'
    
    # 필터 옵션 설정
    filter_options = UserFilter(
        username_contains=username_contains,
        is_admin=is_admin_bool,
        disabled=disabled_bool,
        limit=limit,
        skip=(page - 1) * limit
    )
    
    # 쿼리 구성
    query = {}
    if filter_options.disabled is not None:
        query["disabled"] = filter_options.disabled
    
    if filter_options.is_admin is not None:
        query["is_admin"] = filter_options.is_admin
    
    if filter_options.username_contains:
        query["username"] = {"$regex": filter_options.username_contains, "$options": "i"}
    
    # 페이지네이션을 위한 총 사용자 수 조회
    total_count = await User.find(query).count()
    total_pages = math.ceil(total_count / limit)
    
    # 사용자 목록 조회
    users = await User.find(query).sort(-User.created_at).skip(filter_options.skip).limit(
        filter_options.limit).to_list()
    
    # 페이지네이션 정보 구성 - 비어있지 않은 유효한 파라미터만 URL에 포함
    query_params = []
    if username_contains:
        query_params.append(f"username_contains={username_contains}")
    if is_admin:
        query_params.append(f"is_admin={is_admin}")
    if disabled:
        query_params.append(f"disabled={disabled}")
    
    # 쿼리 파라미터가 있으면 ?를 추가하고 &로 연결
    base_url = "/admin/users"
    if query_params:
        base_url += "?" + "&".join(query_params) + "&"
    else:
        base_url += "?"
    
    # 페이지 범위 계산 (현재 페이지 주변 5개 페이지 표시)
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    
    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page_url": f"{base_url}page={page-1}&limit={limit}" if page > 1 else None,
        "next_page_url": f"{base_url}page={page+1}&limit={limit}" if page < total_pages else None,
        "first_page_url": f"{base_url}page=1&limit={limit}",
        "last_page_url": f"{base_url}page={total_pages}&limit={limit}",
        "pages_range": range(start_page, end_page + 1),
        "page_url": lambda p: f"{base_url}page={p}&limit={limit}"
    }
    
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "users",
            "filter_options": filter_options,
            "users": users,
            "pagination": pagination,
            "messages": []
        }
    )


# API 엔드포인트 프리픽스 변경 (웹 페이지와의 구분을 위해)
# 관리자 웹 인터페이스(/admin/...)와 API 엔드포인트(/api/admin/...)를 구분하기 위한 추가 라우터
api_router = APIRouter(prefix="/api/admin")


# 기존 API 엔드포인트를 새 라우터로 이동
# 아래 wrapper 함수들은 관리자 웹 인터페이스의 모달 폼에서 사용되며,
# templates/admin/users.html과 templates/admin/dashboard.html에서 JavaScript를 통해 호출됨
@api_router.post("/users/disable", response_model=UserResponse)
async def api_admin_disable_user(
        action: AdminUserAction,
        request: Request
):
    """
    사용자 비활성화 API 엔드포인트 (/api/admin/users/disable)
    templates/admin/users.html (195줄)과 templates/admin/dashboard.html (144줄)에서 호출됨
    
    Args:
        action: 비활성화할 사용자 이름과 이유
        request: HTTP 요청 객체
    
    Returns:
        원래 함수(admin_disable_user)의 결과를 그대로 반환
    """
    return await admin_disable_user(action, request)


@api_router.post("/users/enable", response_model=UserResponse)
async def api_admin_enable_user(
        action: AdminUserAction,
        request: Request
):
    """
    사용자 활성화 API 엔드포인트 (/api/admin/users/enable)
    templates/admin/users.html (205줄)과 templates/admin/dashboard.html (154줄)에서 호출됨
    
    Args:
        action: 활성화할 사용자 이름
        request: HTTP 요청 객체
    
    Returns:
        원래 함수(admin_enable_user)의 결과를 그대로 반환
    """
    return await admin_enable_user(action, request)


@api_router.post("/users/promote", response_model=UserResponse)
async def api_admin_promote_user(
        action: AdminUserAction,
        request: Request
):
    """
    사용자 관리자 승격 API 엔드포인트 (/api/admin/users/promote)
    templates/admin/users.html (215줄)과 templates/admin/dashboard.html (164줄)에서 호출됨
    
    Args:
        action: 관리자로 승격할 사용자 이름
        request: HTTP 요청 객체
    
    Returns:
        원래 함수(promote_to_admin)의 결과를 그대로 반환
    """
    return await promote_to_admin(action, request)


@api_router.post("/users/demote", response_model=UserResponse)
async def api_admin_demote_user(
        action: AdminUserAction,
        request: Request
):
    """
    관리자 권한 제거 API 엔드포인트 (/api/admin/users/demote)
    templates/admin/users.html (225줄)과 templates/admin/dashboard.html (174줄)에서 호출됨
    
    Args:
        action: 권한을 제거할 관리자 이름
        request: HTTP 요청 객체
    
    Returns:
        원래 함수(demote_from_admin)의 결과를 그대로 반환
    """
    return await demote_from_admin(action, request)


@api_router.post("/users/list", response_model=list[UserListItem])
async def api_admin_list_users(
        request: Request,
        filter_options: UserFilter = UserFilter(),
):
    """
    사용자 목록 조회 API 엔드포인트 (/api/admin/users/list)
    관리자 인터페이스에서 AJAX를 통해 사용자 목록을 동적으로 로드할 때 사용됨
    
    Args:
        filter_options: 필터링 옵션 (비활성화 여부, 관리자 여부, 사용자 이름 포함 문자열)
        request: HTTP 요청 객체
    
    Returns:
        원래 함수(list_users)의 결과를 그대로 반환
    """
    return await list_users(request, filter_options)
