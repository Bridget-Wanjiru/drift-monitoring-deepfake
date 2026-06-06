import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Replace with the connection string from your Neon/Supabase dashboard
DB_URL = "postgresql://neondb_owner:npg_5UzZuNYQDcM7@ep-old-darkness-aqw11x23-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_connection():
    return psycopg2.connect(DB_URL)

def save_ml_results(video_uuid, features_16d, prediction, confidence, kinematics):
    """
    Saves the final 16D array and verdict to Postgres.
    This enforces your Step 5 'Database Lock-In'.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Update video status
            cur.execute("UPDATE videos SET status = 'completed' WHERE id = %s", (video_uuid,))
            
            # 2. Insert mathematical results
            sql = """
            INSERT INTO ml_analysis_results 
            (video_id, meta_features, final_prediction, confidence_score, temporal_kinematics)
            VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                video_uuid, 
                json.dumps(features_16d), 
                prediction, 
                confidence, 
                json.dumps(kinematics)
            ))
        conn.commit()
        print(f"✓ Results for {video_uuid} successfully stored.")
    except Exception as e:
        print(f"✗ Database Error: {e}")
        conn.rollback()
    finally:
        conn.close()
