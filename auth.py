# auth.py
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import User
from dotenv import load_dotenv
import os

# パスワードのハッシュ化設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# 環境変数の読み込み
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ユーザーログイン用のモデル
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# トークン作成関数
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# トークン検証関数
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="トークンが無効です。")
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません。")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="トークンが無効です。")

# ログインエンドポイント
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが間違っています。")

    token_data = {"user_id": db_user.user_id, "email": db_user.email}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer", "user_name": db_user.user_name}


# ログインエンドポイント（DB仕様前）
# async def login(user: UserLogin):
#     if user.email == mock_user["email"] and pwd_context.verify(user.password, mock_user["password"]):
#         return {"message": "ログイン成功"}
#     raise HTTPException(status_code=401, detail="パスワードまたはメールアドレスが無効です。")
