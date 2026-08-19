from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.schemas.auth_schema import LoginRequest, RefreshTokenRequest, RefreshTokenResponse, TokenResponse, UserResponse, UserCreate
from app.auth.jwt import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token
from app.database import get_db
from app.models.user import User
from app.auth.password import verify_password, get_password_hash

router = APIRouter(prefix='/api/auth', tags=['auth'])


def get_current_user_from_token(request: Request, db: Session = Depends(get_db)) -> User:
    """Extract and validate user from Bearer token in Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header[7:]
    subject = decode_access_token(token)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == int(subject)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post('/register', response_model=TokenResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and return access and refresh tokens.
    """
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password from the request
    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access and refresh tokens
    access_token = create_access_token(subject=str(db_user.id))
    refresh_token = create_refresh_token(subject=str(db_user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='bearer',
        user=UserResponse.from_orm(db_user)
    )


@router.post('/login', response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with JSON body and return access and refresh tokens.
    """
    db_user = db.query(User).filter(User.email == credentials.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(db_user.id))
    refresh_token = create_refresh_token(subject=str(db_user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='bearer',
        user=UserResponse.from_orm(db_user)
    )


@router.get('/me', response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user_from_token)):
    """
    Get current authenticated user info from access token.
    """
    return UserResponse.from_orm(current_user)


@router.post('/refresh', response_model=RefreshTokenResponse)
def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """
    subject = decode_refresh_token(request.refresh_token)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate new access and refresh tokens (token rotation)
    new_access_token = create_access_token(subject=subject)
    new_refresh_token = create_refresh_token(subject=subject)

    return RefreshTokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type='bearer'
    )