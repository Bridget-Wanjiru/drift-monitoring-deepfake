"""
Core Transaction Operation Validation Suite
"""
import sys
import random
from pathlib import Path

# Set up clean top-level pathing paths
root_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / 'src'))

from src.db_service import DatabaseService

print("=" * 70)
print(" Starting Pipeline Transaction Validation Stage")
print("=" * 70)

try:
    service = DatabaseService()
    unique_marker = random.randint(1000, 9999)
    
    # 1. Test Client Generation
    print("\n1. Running token authorization credentials registration check...")
    client = service.register_client(
        client_name=f"Node_Node_Evaluator_{unique_marker}",
        webhook_url="https://jhub.africa.example/webhooks/drift"
    )
    
    if client["status"] == "success":
        print(f"    Auth Success: Client registered with Primary ID [{client['client_id']}]")
        target_client_id = client['client_id']
    else:
        print(f"    Auth Failure: {client['message']}")
        sys.exit(1)

    # 2. Test Metric Logging
    print("\n2. Running mathematical tracking logging parameters verification...")
    metric_commit = service.save_drift_metric(
        batch_sample_size=150,
        psi_score=0.0142,
        ks_statistic=0.021,
        system_health="HEALTHY"
    )
    
    if metric_commit:
        print("    Transaction Success: Drift metrics committed to Neon safely.")
    else:
        print("    Transaction Failure: Could not commit calculation metric frames.")
        sys.exit(1)

    service.close()
    
    print(" Transaction Entire Logs Verified Natively Compliant")
    

except Exception as e:
    print(f" Abrupt tracking execution crash detected: {e}")
    sys.exit(1)