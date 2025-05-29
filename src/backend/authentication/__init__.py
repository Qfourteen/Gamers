from datetime import datetime, timezone
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Request, HTTPException, status

from src.backend.models.user import User
from src.backend.env import SECRET_KEY

COOKIE_NAME = "auth_token"  # 인증 쿠키 이름
TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 30 # 30일

# 패스워드 해싱 및 인증 설정
ph = PasswordHasher()
serializer = URLSafeTimedSerializer(SECRET_KEY)


def hash_password(password: str) -> str:
    """
    주어진 평문 비밀번호를 Argon2 알고리즘을 사용하여 해싱합니다.

    Args:
        password: 해싱할 평문 비밀번호

    Returns:
        해싱된 비밀번호 문자열
    """
    return ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해싱된 비밀번호를 비교하여 일치 여부를 확인합니다.

    Args:
        password: 확인할 평문 비밀번호
        hashed_password: 비교할 해싱된 비밀번호

    Returns:
        비밀번호가 일치하면 True, 그렇지 않으면 False
    """
    try:
        ph.verify(hashed_password, password)
        return True
    except VerifyMismatchError:
        return False


async def get_user(username: str) -> Optional[User]:
    """
    사용자 이름으로 데이터베이스에서 사용자를 조회합니다.

    Args:
        username: 조회할 사용자 이름

    Returns:
        사용자가 존재하면 User 객체, 존재하지 않으면 None
    """
    return await User.find_one(User.username == username)


async def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    사용자 이름과 비밀번호를 사용하여 사용자를 인증합니다.

    Args:
        username: 인증할 사용자 이름
        password: 인증할 비밀번호

    Returns:
        인증에 성공하면 User 객체, 실패하면 None
    """
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    # 로그인 시간 업데이트
    user.last_login = datetime.now(timezone.utc)
    await user.save()
    return user


def create_access_token(data: dict) -> str:
    """
    주어진 데이터로 액세스 토큰을 생성합니다.

    Args:
        data: 토큰에 포함할 데이터 딕셔너리

    Returns:
        생성된 액세스 토큰 문자열
    """
    return serializer.dumps(data)


def verify_token(token: str) -> Optional[dict]:
    """
    액세스 토큰의 유효성을 검증하고 토큰에서 데이터를 추출합니다.

    Args:
        token: 검증할 액세스 토큰

    Returns:
        토큰이 유효하면 토큰에 포함된 데이터 딕셔너리, 유효하지 않으면 None
    """
    try:
        data = serializer.loads(token, max_age=TOKEN_EXPIRE_SECONDS)
        return data
    except SignatureExpired:
        # 토큰이 만료됨
        return None
    except BadSignature:
        # 토큰이 유효하지 않음
        return None


async def get_current_user(request: Request) -> User:
    """
    쿠키에서 현재 인증된 사용자를 가져옵니다.

    Args:
        request: HTTP 요청 객체

    Returns:
        현재 인증된 사용자 객체

    Raises:
        HTTPException: 인증이 유효하지 않거나 사용자를 찾을 수 없는 경우
    """
    # 쿠키가 없으면
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # 쿠키가 올바른지
    data = verify_token(token)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
        )

    # 쿠키에 username이 있는지
    username = data.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # 그 username이 DB에 있는지
    user = await get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def check_admin_permissions(user: User):
    """
    사용자가 관리자 권한을 가지고 있는지 확인합니다.

    Args:
        user: 확인할 사용자

    Raises:
        HTTPException: 사용자가 관리자가 아닌 경우
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
