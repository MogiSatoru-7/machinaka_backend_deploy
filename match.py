# match.py
from fastapi import APIRouter, HTTPException
from sentence_transformers import SentenceTransformer
from azure.cosmos import CosmosClient
import mysql.connector
import base64
import tempfile
import faiss
import numpy as np
import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

match_router = APIRouter()

# CosmosDB接続設定
def get_cosmos_client():
    try:
        endpoint = os.getenv("COSMOSDB_ENDPOINT")
        key = os.getenv("COSMOSDB_KEY")
        database_name = "SkillsDB"
        container_name = "SkillContainer"

        client = CosmosClient(endpoint, key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        print("CosmosDB接続成功")
        return container
    except Exception as e:
        print(f"CosmosDB接続エラー: {e}")
        raise e

# MySQLからプロジェクト説明を取得
def fetch_project_description():
    mysql_config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }

    try:
        with mysql.connector.connect(**mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT project_description FROM projects WHERE project_id = 1")
                project_description = cursor.fetchone()[0]
                print(f"MySQLから取得したプロジェクト説明: {project_description}")
                return project_description
    except mysql.connector.Error as err:
        print(f"MySQL エラー: {err}")
        raise Exception(f"MySQL エラー: {err}")

# FAISSインデックスを取得
def get_skill_faiss_index(skill_id):
    try:
        cosmos_container = get_cosmos_client()
        skill_data = cosmos_container.read_item(skill_id, partition_key="/skill")
        print(f"CosmosDBから取得したスキルデータ: {skill_data}")

        decoded_data = base64.b64decode(skill_data["encoded_data"])

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(decoded_data)
            temp_file_path = temp_file.name

        print(f"FAISSインデックスを読み込み: {temp_file_path}")
        return faiss.read_index(temp_file_path)
    except Exception as e:
        print(f"FAISSインデックス読み込みエラー: {e}")
        raise e

# マッチング処理
def match_project_to_skills(project_vector, skill_ids):
    best_match = None
    best_score = float('inf')

    for skill_id in skill_ids:
        try:
            print(f"スキルID: {skill_id} のFAISSインデックスを検索")
            skill_index = get_skill_faiss_index(skill_id)
            distances, indices = skill_index.search(np.array([project_vector]), k=1)
            score = distances[0][0]
            print(f"スキルID: {skill_id} のスコア: {score}")

            if score < best_score:
                best_score = score
                best_match = skill_id
        except Exception as e:
            print(f"スキルID {skill_id} の処理でエラー: {e}")
            continue

    print(f"最適なマッチング: {best_match}, スコア: {best_score}")
    return best_match, best_score

# マッチングエンドポイント
@match_router.get("/match")
async def find_matching_users():
    try:
        # MySQLからプロジェクトの説明を取得
        project_description = fetch_project_description()

        # SentenceTransformerでベクトル化
        model = SentenceTransformer("all-MiniLM-L6-v2")
        project_vector = model.encode(project_description).astype('float32')
        print(f"生成されたプロジェクトベクトル: {project_vector}")

        # マッチング処理
        skill_ids = ["skills_index_1", "skills_index_2", "skills_index_3"]
        best_match, best_score = match_project_to_skills(project_vector, skill_ids)

        # 結果の返却
        if best_match:
            print("マッチング成功")
            return {"best_match_skill_id": best_match, "score": float(best_score)}
        else:
            print("マッチするスキルが見つかりませんでした")
            return {"message": "マッチするスキルが見つかりませんでした。"}
    except Exception as e:
        print(f"マッチング処理エラー: {e}")
        raise HTTPException(status_code=500, detail=f"マッチング処理エラー: {str(e)}")
