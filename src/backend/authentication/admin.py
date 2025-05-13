from fastapi import APIRouter, status, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from src.backend.models.user import User

from src.backend.schemas.authentication import UserResponse, AdminUserAction

from . import (
    get_user, get_current_user, check_admin_permissions
)

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
