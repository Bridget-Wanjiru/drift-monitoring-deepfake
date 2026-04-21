"""
Data Verification Script
Validates all feature data files
"""

import numpy as np
from pathlib import Path
import yaml


def verify_file(filepath, expected_features=16):
    """Verify a single .npy file"""
    print(f"\nChecking {filepath}...")
    
    if not Path(filepath).exists():
        print(f"  Error: File not found")
        return False
    
    try:
        data = np.load(filepath)
    except Exception as e:
        print(f"  Error: Failed to load - {e}")
        return False
    
    # Check shape
    if len(data.shape) == 2:
        if data.shape[1] != expected_features:
            print(f"  Error: Wrong shape {data.shape}, expected (*, {expected_features})")
            return False
        print(f"  Shape: {data.shape}")
        print(f"  Mean: {data.mean():.4f}, Std: {data.std():.4f}")
    else:
        print(f"  Error: Invalid shape {data.shape}")
        return False
    
    # Check for NaN/Inf
    if np.isnan(data).any():
        print(f"  Error: Contains NaN values")
        return False
    
    if np.isinf(data).any():
        print(f"  Error: Contains Inf values")
        return False
    
    print(f"  Status: Valid")
    return True


def main():
    print("Data Verification")
      
    # Load config
    with open('config/datasets.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    all_valid = True
    
    # Verify reference data
    print("\n1. Reference Data:")
    if 'reference' in config:
        ref = config['reference']
        if not verify_file(ref['features_path'], expected_features=16):
            all_valid = False
    
    # Verify simulation batches
    print("\n2. Simulation Batches:")
    if 'simulation_batches' in config:
        for batch in config['simulation_batches']:
            batch_id = batch.get('batch_id')
            print(f"\n  Batch: {batch_id}")
            if not verify_file(batch['features_path'], expected_features=16):
                all_valid = False
    
    
    if all_valid:
        print("Result: All data files are Valid")
    else:
        print("Result: Some files are Invalid or Missing")
   


if __name__ == "__main__":
    main()