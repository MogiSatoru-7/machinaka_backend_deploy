#database.py

#sqlalchemyを使用した場合
import os
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# 環境変数からデータベース接続情報を取得
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_ssl_ca = os.getenv("DB_ssl_ca")

if not all([DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DB_ssl_ca]):
    raise EnvironmentError("One or more required environment variables are missing!")

# MySQLデータベースへの接続URL
# データベース接続URL（Azure 用）
# DATABASE_URLにSSLオプションを追加
DATABASE_URL = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# SSL 設定を追加してエンジンを作成
engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": {"ca": DB_ssl_ca}},
    echo=True  # SQLログを有効にする
)

# SessionLocal クラスを作成し、データベース接続のセッションを管理
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# データベースのベースクラス
Base = declarative_base()

# データベース接続のテスト
def test_connection():
    """
    データベース接続のテストを行い、成功した場合は接続先データベース名を表示。
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0] if result.rowcount > 0 else "No database selected"
            print(f"Connected to database: {db_name}")
    except Exception as e:
        print("Database connection test failed:", e)
        raise e

def init_db():
    """
    データベースのテーブルを作成。
    """
    print("Creating all tables based on models...")
    # Base.metadata.create_allを実行してテーブルを作成します
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

# FastAPI 用のデータベース接続依存関係
def get_db():
    """
    FastAPIの依存関係として使用。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# スクリプトやテスト用のデータベースセッション取得
def get_session():
    """
    スクリプトやテストで使用。
    """
    session = SessionLocal()
    try:
        return session
    except Exception as e:
        session.close()
        raise e



# #こっちの方が完全らしい。一応残しておく
# import os
# import traceback
# from sqlalchemy import create_engine, text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv

# # .envファイルの読み込み
# load_dotenv()

# # 環境変数の取得と検証
# required_env_vars = ["DB_USERNAME", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME", "DB_ssl_ca"]
# missing_vars = [var for var in required_env_vars if not os.getenv(var)]
# if missing_vars:
#     raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

# DB_USERNAME = os.getenv("DB_USERNAME")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST")
# DB_PORT = os.getenv("DB_PORT")
# DB_NAME = os.getenv("DB_NAME")
# DB_ssl_ca = os.getenv("DB_ssl_ca")

# # MySQLデータベースへの接続URL
# DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# # SSL オプションの設定
# connect_args = {}
# if DB_ssl_ca:
#     connect_args["ssl"] = {"ca": DB_ssl_ca}

# # エンジン作成
# engine = create_engine(DATABASE_URL, connect_args=connect_args)

# # SessionLocal クラスを作成し、データベース接続のセッションを管理
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # データベースのベースクラス
# Base = declarative_base()

# # データベース接続のテスト
# def test_connection():
#     """Test the database connection."""
#     try:
#         with engine.connect() as conn:
#             result = conn.execute(text("SELECT DATABASE()"))
#             db_name = result.fetchone()[0] if result.rowcount > 0 else "No database selected"
#             print(f"Connected to database: {db_name}")
#     except Exception as e:
#         print("Database connection test failed:", e)
#         raise

# # テーブルの初期化
# def init_db():
#     """Initialize the database by creating all tables."""
#     Base.metadata.create_all(bind=engine)

# # データベース接続の依存関係
# def get_db():
#     """Provide a database session."""
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
