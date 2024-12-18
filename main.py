# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import User
from database import test_connection, engine
from auth import login, get_current_user  # auth.pyからインポート
# 各ルーターをインポート
from routers import offices, users, projects, skills, industries, job_titles

app = FastAPI()

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンのみ許可してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース接続テストをスタートアップイベントに設定
@app.on_event("startup")
def startup_event():
    test_connection()

@app.get("/test-db-connection")
def test_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0] if result.rowcount > 0 else "No database selected"
            return {"message": "Connected to database", "database": db_name}
    except Exception as e:
        return {"error": str(e)}

# 認証関連エンドポイント
app.post("/login")(login)  # auth.pyのlogin関数を使用

# 認証されたエンドポイントの例
@app.get("/profile")
async def read_profile(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.user_id, "user_name": current_user.user_name, "email": current_user.email}

# 各ルーターを登録
app.include_router(offices.router, prefix="/api", tags=["offices"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(skills.router, prefix="/api", tags=["skills"])
app.include_router(industries.router, prefix="/api", tags=["industries"])
app.include_router(job_titles.router, prefix="/api", tags=["job_titles"])

# ルートエンドポイント
@app.get("/")
def read_root():
    return {"message": "Welcome to the Machinaka App API"}