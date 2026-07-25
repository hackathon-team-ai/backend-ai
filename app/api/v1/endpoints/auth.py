from datetime import timedelta
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.config import settings
from app.core import security, exceptions
from app.database.mongodb import get_database
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, PasswordReset, UserInDB

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# In-memory users fallback database if MongoDB is not running
IN_MEMORY_USERS = {}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = security.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise exceptions.CredentialsException()
    
    user_id = payload.get("sub")
    db = get_database()
    
    if db is not None:
        try:
            user = await db.users.find_one({"_id": user_id})
            if user:
                user["id"] = str(user["_id"])
                return user
        except Exception:
            pass

    if user_id in IN_MEMORY_USERS:
        return IN_MEMORY_USERS[user_id]

    raise exceptions.UserNotFoundException()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    db = get_database()
    hashed_pwd = security.get_password_hash(user_in.password)
    user_id = str(uuid.uuid4())

    user_dict = {
        "_id": user_id,
        "id": user_id,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "phone_number": user_in.phone_number,
        "role": user_in.role,
        "state": user_in.state,
        "district": user_in.district,
        "soil_type": user_in.soil_type,
        "farm_size_acres": user_in.farm_size_acres,
        "preferred_language": user_in.preferred_language,
        "hashed_password": hashed_pwd,
        "is_active": True,
        "created_at": security.datetime.now(security.timezone.utc),
        "updated_at": security.datetime.now(security.timezone.utc)
    }

    if db is not None:
        try:
            existing = await db.users.find_one({"email": user_in.email})
            if existing:
                raise exceptions.UserAlreadyExistsException()
            await db.users.insert_one(user_dict)
        except Exception as e:
            if "already exists" in str(e).lower():
                raise exceptions.UserAlreadyExistsException()
            IN_MEMORY_USERS[user_id] = user_dict
    else:
        IN_MEMORY_USERS[user_id] = user_dict

    access_token = security.create_access_token(user_id)
    refresh_token = security.create_refresh_token(user_id)
    user_resp = UserResponse(**user_dict)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_resp
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    user = None

    if db is not None:
        try:
            user = await db.users.find_one({"email": form_data.username})
        except Exception:
            pass

    if not user:
        for u_id, u_data in IN_MEMORY_USERS.items():
            if u_data["email"] == form_data.username:
                user = u_data
                break

    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = str(user["_id"]) if "_id" in user else user["id"]
    access_token = security.create_access_token(user_id)
    refresh_token = security.create_refresh_token(user_id)
    
    user["id"] = user_id
    user_resp = UserResponse(**user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_resp
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@router.post("/forgot-password")
async def forgot_password(data: PasswordReset):
    # Simulated password reset success
    return {"message": f"Password reset instructions sent to {data.email}."}
