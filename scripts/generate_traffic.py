"""
Traffic Simulation Script
Simulates weeks of Classifier (Microservice 4) outputs
"""

import numpy as np
import json
import uuid
from pathlib import Path


def generate_classifier_payloads(num_videos, is_drifting=False):
    """
    Generate fake Classifier outputs (16-dim features + metadata)
    This simulates what Microservice 4 will send to your API
    """
    payloads = []
    
    # 1. The Math Toggle (Healthy vs. Drifting)
    if not is_drifting:
        # Healthy math: Mean is 0.0, Classifier is highly confident (80% to 99%)
        mean_val = 0.0
        conf_low, conf_high = 0.80, 0.99
    else:
        # Drifted math: Mean shifts to 2.5 (A new deepfake generator!), Classifier gets confused
        mean_val = 2.5
        conf_low, conf_high = 0.45, 0.65
    
    # 2. Generate the fake data for N videos
    for _ in range(num_videos):
        # Generate the 16-dim Temporal/Spatial embedding
        fake_features = np.random.normal(loc=mean_val, scale=1.0, size=16)
        
        # Generate the probability score
        fake_confidence = np.random.uniform(conf_low, conf_high)
        
        # Build the exact JSON contract (Classifier API output format)
        payload = {
            "video_id": f"uuid-{str(uuid.uuid4())[:8]}",
            "prediction": np.random.choice(["fake", "real"]),
            "confidence": round(fake_confidence, 4),
            "features": np.round(fake_features, 4).tolist()
        }
        payloads.append(payload)
    
    return payloads


def extract_features_to_npy(payloads, filename):
    """
    Extract just the 16-dim features from JSON and save as .npy
    This is what your drift detector needs for PSI/KS calculations
    """
    features = np.array([p['features'] for p in payloads], dtype=np.float32)
    np.save(filename, features)
    print(f"    → Extracted features to {filename} (shape: {features.shape})")


# SIMULATION: Weeks of Classifier Traffic


print("CLASSIFIER TRAFFIC SIMULATION")
print("Simulating Microservice 4 outputs over 3 weeks")


# Create directories
Path("data/simulation").mkdir(parents=True, exist_ok=True)
Path("data/reference").mkdir(parents=True, exist_ok=True)

# --- WEEK 0: Training Baseline (What the model was trained on) ---
print("\nWeek 0: Training Baseline (1800 videos)")

print("This represents the original training data distribution")

baseline_train = generate_classifier_payloads(1800, is_drifting=False)

with open('data/simulation/week0_training_baseline.json', 'w') as f:
    json.dump(baseline_train, f, indent=2)
print(" JSON: data/simulation/week0_training_baseline.json (1800 records)")

extract_features_to_npy(baseline_train, 'data/reference/train_features.npy')


# --- WEEK 1: Healthy Traffic (No drift) ---
print("\nWeek 1: Healthy Traffic (1000 videos)")

print("Normal internet traffic - model is working well")

week1_healthy = generate_classifier_payloads(1000, is_drifting=False)

with open('data/simulation/week1_healthy_traffic.json', 'w') as f:
    json.dump(week1_healthy, f, indent=2)
print(" JSON: data/simulation/week1_healthy_traffic.json (1000 records)")

extract_features_to_npy(week1_healthy, 'data/simulation/week1_features.npy')


# --- WEEK 2: Moderate Drift (New deepfake tool gaining popularity) ---
print("\nWEEK 2: Moderate Drift (1000 videos)")

print("A new deepfake generator is starting to appear")

# Mix: 70% healthy, 30% drifted
week2_healthy = generate_classifier_payloads(700, is_drifting=False)
week2_drifted = generate_classifier_payloads(300, is_drifting=True)
week2_mixed = week2_healthy + week2_drifted

with open('data/simulation/week2_moderate_drift.json', 'w') as f:
    json.dump(week2_mixed, f, indent=2)
print(" JSON: data/simulation/week2_moderate_drift.json (1000 records)")

extract_features_to_npy(week2_mixed, 'data/simulation/week2_features.npy')


# --- WEEK 3: HIGH DRIFT (New tool dominates) ---
print("\nWEEK 3: High Drift (1000 videos)")

print("The new deepfake tool is now dominant ")

# Mix: 20% healthy, 80% drifted
week3_healthy = generate_classifier_payloads(200, is_drifting=False)
week3_drifted = generate_classifier_payloads(800, is_drifting=True)
week3_critical = week3_healthy + week3_drifted

with open('data/simulation/week3_high_drift.json', 'w') as f:
    json.dump(week3_critical, f, indent=2)
print(" JSON: data/simulation/week3_high_drift.json (1000 records)")

extract_features_to_npy(week3_critical, 'data/simulation/week3_features.npy')


print("Simulation complete")


print("\nJSON Files (Classifier outputs):")
print("  Week 0: data/simulation/week0_training_baseline.json (1800 records)")
print("  Week 1: data/simulation/week1_healthy_traffic.json (1000 records)")
print("  Week 2: data/simulation/week2_moderate_drift.json (1000 records)")
print("  Week 3: data/simulation/week3_high_drift.json (1000 records)")

print("\nNoy files (For drift detector):")
print("  Reference: data/reference/train_features.npy (1800, 16)")
print("  Week 1: data/simulation/week1_features.npy (1000, 16)")
print("  Week 2: data/simulation/week2_features.npy (1000, 16)")
print("  Week 3: data/simulation/week3_features.npy (1000, 16)")

print("\nExpected Drift Levels:")
print("  Week 1 → PSI: ~0.10 (GREEN - No drift)")
print("  Week 2 → PSI: ~0.28 (YELLOW - Moderate drift)")
print("  Week 3 → PSI: ~0.45 (RED - High drift)")
