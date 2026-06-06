"""
Database Service Layer
Handles transactional operations against Neon Cloud PostgreSQL tables.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from src.db_config import SessionLocal

class DatabaseService:
    def __init__(self):
        # Open a dedicated session connection pool line
        self.db = SessionLocal()

    def register_client(self, client_name: str, webhook_url: str) -> Dict[str, Any]:
        """Registers a new external API client node with a secure authentication token."""
        generated_api_key = f"sk_live_{uuid.uuid4().hex}"
        
        query = text("""
            INSERT INTO api_clients (client_name, api_key, webhook_url)
            VALUES (:name, :key, :webhook)
            RETURNING id, client_name, api_key;
        """)
        
        try:
            result = self.db.execute(
                query, 
                {"name": client_name, "key": generated_api_key, "webhook": webhook_url}
            ).fetchone()
            self.db.commit()
            
            if result:
                return {
                    "status": "success",
                    "client_id": result[0],
                    "client_name": result[1],
                    "api_key": result[2]
                }
            return {"status": "error", "message": "Failed to retrieve database insertion tuple."}
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": str(e)}

    def verify_api_key(self, api_key: str) -> Optional[int]:
        """Validates incoming authorization headers against database client keys."""
        query = text("SELECT id FROM api_clients WHERE api_key = :key AND is_active = TRUE;")
        result = self.db.execute(query, {"key": api_key}).fetchone()
        return result[0] if result else None

    def create_video_entry(self, video_id: str, client_id: int, filename: str) -> str:
        """Indexes an incoming upload stream asset into the operational pipeline."""
        query = text("""
            INSERT INTO videos (id, client_id, filename, status)
            VALUES (:id, :client_id, :filename, 'uploaded')
            RETURNING id;
        """)
        result = self.db.execute(
            query, 
            {"id": video_id, "client_id": client_id, "filename": filename}
        ).fetchone()
        self.db.commit()
        return result[0]

    def save_analysis_result(self, video_id: str, temporal_kinematics: Dict[str, Any], 
                             final_prediction: str, confidence_score: float, 
                             meta_features: List[float]) -> bool:
        """Saves multidimensional analytical outputs from deep learning model inferences."""
        query = text("""
            INSERT INTO ml_analysis_results 
            (video_id, temporal_kinematics, final_prediction, confidence_score, meta_features)
            VALUES (:v_id, :kinetics, :pred, :conf, :meta)
            ON CONFLICT (video_id) DO UPDATE SET
                temporal_kinematics = EXCLUDED.temporal_kinematics,
                final_prediction = EXCLUDED.final_prediction,
                confidence_score = EXCLUDED.confidence_score,
                meta_features = EXCLUDED.meta_features;
        """)
        try:
            self.db.execute(query, {
                "v_id": video_id,
                "kinetics": json.dumps(temporal_kinematics),
                "pred": final_prediction,
                "conf": confidence_score,
                "meta": json.dumps(meta_features)
            })
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f" Failed to save analysis array output vectors: {e}")
            return False

    def fetch_latest_meta_features(self, batch_size=1000):
        """
        Pulls the latest 16D meta-features from the ml_analysis_results table
        using your read-only drift monitor credentials.
        """
        import numpy as np
        
        # SQL query to grab the 16D arrays and their processing timestamps
        query = """
            SELECT video_id, meta_features 
            FROM ml_analysis_results 
            ORDER BY result_id DESC 
            LIMIT %s;
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (batch_size,))
                rows = cursor.fetchall()
                
            if not rows:
                print(" Database scan complete: No live feature records found yet.")
                return None
                
            # Extract the 16D arrays from the database rows
            # Assumes meta_features is stored as a PostgreSQL array (FLOAT[])
            features_list = [row[1] for row in rows]
            
            # Convert the list of arrays into a clean 2D NumPy array (Shape: N x 16)
            features_matrix = np.array(features_list)
            
            print(f"  Successfully pulled {features_matrix.shape[0]} samples from Neon cloud.")
            return features_matrix
            
        except Exception as e:
            print(f"  Failed to fetch meta-features from cloud table: {e}")
            return None
    
    def save_drift_metric(self, batch_sample_size: int, psi_score: float, 
                          ks_statistic: float, system_health: str) -> bool:
        """Logs processed analytical statistical metrics computed from population metrics models."""
        query = text("""
            INSERT INTO drift_metrics (batch_sample_size, psi_score, ks_statistic, system_health)
            VALUES (:size, :psi, :ks, :health);
        """)
        try:
            self.db.execute(query, {
                "size": batch_sample_size,
                "psi": psi_score,
                "ks": ks_statistic,
                "health": system_health
            })
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f" Failed to write processed calculations layer row properties: {e}")
            return False

    def close(self):
        """Safely clean up structural thread connections back out to the engine loop pool."""
        self.db.close()