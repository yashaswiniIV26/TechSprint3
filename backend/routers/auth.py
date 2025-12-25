from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid

from config import settings
from models.schemas import Token, UserLogin, StudentCreate, TokenData

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# In-memory user store (replace with database in production)
users_db = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        student_id: str = payload.get("sub")
        if student_id is None:
            raise credentials_exception
        token_data = TokenData(student_id=student_id)
    except JWTError:
        raise credentials_exception
    
    user = users_db.get(token_data.student_id)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=dict)
async def register(user: StudentCreate):
    """Register a new student"""
    
    # Check if email already exists
    for uid, u in users_db.items():
        if u.get("email") == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create user
    student_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    
    users_db[student_id] = {
        "student_id": student_id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "college": user.college,
        "degree": user.degree,
        "graduation_year": user.graduation_year,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return {
        "message": "User registered successfully",
        "student_id": student_id
    }


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    
    # Find user by email
    user = None
    for uid, u in users_db.items():
        if u.get("email") == form_data.username:
            user = u
            break
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["student_id"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login_json(credentials: UserLogin):
    """Login with JSON body"""
    
    # Find user by email
    user = None
    for uid, u in users_db.items():
        if u.get("email") == credentials.email:
            user = u
            break
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["student_id"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    user_data = {k: v for k, v in current_user.items() if k != "hashed_password"}
    return user_data
