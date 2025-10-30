from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import crud
import schemas

# JWT配置
SECRET_KEY = "melody-commons-secret-key-2025-09-01-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        print(f"Unknown hash format for password verification")
        return False
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def hash_password(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token_string(token: str) -> str:
    """验证token字符串"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no username"
            )
        return username
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: JWT error"
        )


def get_user_by_token(username: str, db: Session) -> schemas.User:
    """通过token获取用户"""
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """验证令牌"""
    token = credentials.credentials
    return verify_token_string(token)


def get_current_user(
        username: str = Depends(verify_token),
        db: Session = Depends(get_db)
) -> schemas.User:
    """获取当前用户"""
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def get_current_user_from_request(request: Request, db: Session) -> schemas.User:
    """从请求中获取当前用户"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    token = auth_header.split(" ")[1]
    username = verify_token_string(token)
    return get_user_by_token(username, db)


def get_current_user_optional(request: Request, db: Session) -> Optional[schemas.User]:
    """从请求中获取当前用户（可选，不抛出异常）"""
    try:
        return get_current_user_from_request(request, db)
    except:
        return None


def validate_token_from_query(token: str, db: Session) -> schemas.User:
    """从查询参数验证token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required"
        )

    try:
        username = verify_token_string(token)
        user = get_user_by_token(username, db)
        return user
    except Exception as e:
        print(f"Token validation from query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token"
        )
