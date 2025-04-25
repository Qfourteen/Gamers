from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from ..models.user import User

# 보안 키 및 설정
from ..env import SECRET_KEY
TOKEN_EXPIRE_SECONDS = 18000  # 5시간
COOKIE_NAME = "auth_token"  # 인증 쿠키 이름

# 패스워드 해싱 및 인증 설정
ph = PasswordHasher()
security = HTTPBasic()
serializer = URLSafeTimedSerializer(SECRET_KEY)

basic_router = APIRouter()

class UserResponse(BaseModel):
    username: str
    disabled: bool = False

class UserCreate(BaseModel):
    username: str
    password: str

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
    user.last_login = datetime.utcnow()
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
            headers={"WWW-Authenticate": "Basic"},
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
        secure=False  # 개발 환경에서는 HTTP 허용, 프로덕션은 True로 설정
    )
    
    return {
        "message": "Login successful",
        "user": UserResponse(username=user.username, disabled=user.disabled)
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
        disabled=user.disabled
    )

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
    
    return user

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
        raise HTTPException(status_code=400, detail="Inactive user")
    return UserResponse(
        username=current_user.username,
        disabled=current_user.disabled
    )