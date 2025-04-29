from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime, timezone

from src.backend.models.user import User
from src.backend.utility import is_valid_nickname
from src.backend.env import SECURE_COOKIE

from . import (
    UserResponse, UserCreate, AccountAction,
    COOKIE_NAME, TOKEN_EXPIRE_SECONDS,
    get_user, authenticate_user, create_access_token, get_current_user,
    hash_password, verify_token
)

# HTTP 기본 인증 설정
security = HTTPBasic()
basic_router = APIRouter()

@basic_router.post("/login")
async def login(credentials: HTTPBasicCredentials = Depends(security), response: Response = None):
    """
    사용자 이름과 비밀번호를 사용하여 로그인하고 인증 쿠키를 설정합니다.
    
    Args:
        credentials: HTTP Basic 인증 정보(사용자 이름과 비밀번호)
        response: FastAPI 응답 객체
        
    Returns:
        성공 메시지 및 사용자 정보
        
    Raises:
        HTTPException: 인증 정보가 올바르지 않은 경우
    """
    user = await authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # 토큰 생성
    access_token = create_access_token(
        data={"sub": user.username}
    )
    
    # 쿠키 설정
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,  # JavaScript에서 접근 불가
        max_age=TOKEN_EXPIRE_SECONDS,
        samesite="lax",  # CSRF 방지
        secure=SECURE_COOKIE  # 개발 환경에서는 HTTP 허용, 프로덕션은 True로 설정
    )
    
    return {
        "message": "Login successful",
        "user": UserResponse(
            username=user.username, 
            disabled=user.disabled,
            is_admin=user.is_admin,
            disabled_reason=user.disabled_reason,
            disabled_at=user.disabled_at
        )
    }


@basic_router.post("/logout")
async def logout(response: Response):
    """
    로그아웃 처리를 위해 인증 쿠키를 삭제합니다.
    
    Args:
        response: FastAPI 응답 객체
        
    Returns:
        로그아웃 성공 메시지
    """
    response.delete_cookie(key=COOKIE_NAME)
    return {"message": "Logout successful"}


@basic_router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """
    새 사용자를 등록합니다.
    
    Args:
        user_data: 등록할 사용자 정보
        
    Returns:
        생성된 사용자 정보
        
    Raises:
        HTTPException: 이미 동일한 사용자 이름이 존재하는 경우
    """
    # 사용할 수 있는 username인지 확인
    is_valid = is_valid_nickname(user_data.username)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid username"
        )

    # 기존 사용자 확인
    existing_user = await get_user(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # 새 사용자 생성
    hashed_password = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        hashed_password=hashed_password
    )
    await user.save()
    return UserResponse(
        username=user.username,
        disabled=user.disabled,
        is_admin=user.is_admin,
        disabled_reason=user.disabled_reason,
        disabled_at=user.disabled_at
    )


@basic_router.get("/users/me", response_model=UserResponse)
async def read_users_me(request: Request):
    """
    현재 인증된 사용자의 정보를 조회합니다.
    
    Args:
        request: HTTP 요청 객체
        
    Returns:
        현재 인증된 사용자 정보
        
    Raises:
        HTTPException: 인증이 유효하지 않거나, 사용자가 비활성 상태인 경우
    """
    current_user = await get_current_user(request)
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Account is disabled. Reason: {current_user.disabled_reason}"
        )
    return UserResponse(
        username=current_user.username,
        disabled=current_user.disabled,
        is_admin=current_user.is_admin,
        disabled_reason=current_user.disabled_reason,
        disabled_at=current_user.disabled_at
    )


@basic_router.post("/users/deactivate", response_model=UserResponse)
async def deactivate_account(
    action: AccountAction,
    request: Request
):
    """
    자신의 계정을 비활성화합니다. (소프트 삭제)
    
    Args:
        action: 비활성화 이유 (선택)
        request: HTTP 요청 객체
        
    Returns:
        비활성화된 사용자 정보
    """
    current_user = await get_current_user(request)
    
    # 이미 비활성화된 계정인지 확인
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already disabled"
        )
    
    # 계정 비활성화
    current_user.disabled = True
    current_user.disabled_reason = action.reason or "User requested account deactivation"
    current_user.disabled_at = datetime.now(timezone.utc)
    current_user.disabled_by = current_user.username  # 자신에 의한 비활성화
    await current_user.save()
    
    # 로그아웃 처리 (쿠키 삭제)
    response = Response()
    response.delete_cookie(key=COOKIE_NAME)
    
    return UserResponse(
        username=current_user.username,
        disabled=current_user.disabled,
        is_admin=current_user.is_admin,
        disabled_reason=current_user.disabled_reason,
        disabled_at=current_user.disabled_at
    )


@basic_router.post("/users/reactivate", response_model=UserResponse)
async def reactivate_account(request: Request):
    """
    자신의 비활성화된 계정을 다시 활성화합니다.
    
    Args:
        request: HTTP 요청 객체
        
    Returns:
        활성화된 사용자 정보
    """
    # 계정 비활성화 여부 체크를 건너뛰고 사용자 조회
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    data = verify_token(token)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
        )
    
    username = data.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = await get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # 비활성화된 계정이 아니면 에러
    if not user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already active"
        )
    
    # 계정 활성화
    user.disabled = False
    user.disabled_reason = None
    user.disabled_at = None
    user.disabled_by = None
    await user.save()
    
    return UserResponse(
        username=user.username,
        disabled=user.disabled,
        is_admin=user.is_admin,
        disabled_reason=user.disabled_reason,
        disabled_at=user.disabled_at
    )
