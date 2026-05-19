"""
Live Traffic Simulator
Simulates Classifier (Microservice 4) sending features to your API in real-time
Tests the complete workflow: Classifier → Your API → Drift Detection
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime


API_URL = "http://localhost:5001"


def load_traffic_data(json_file):
    """Load simulated Classifier outputs from JSON file"""
    with open(json_file, 'r') as f:
        return json.load(f)


def send_to_api(payload):
    """Send single video's features to drift monitoring API"""
    try:
        response = requests.post(
            f"{API_URL}/api/drift/collect-features",
            json=payload,
            timeout=5
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"    API Error: {e}")
        return None


def get_system_status():
    """Get current reliability status from API"""
    try:
        response = requests.get(f"{API_URL}/api/system-reliability", timeout=5)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  API Error: {e}")
        return None


def simulate_week(week_name, json_file, delay=0.001):
    """
    Simulate one week of traffic
    
    Args:
        week_name: Week identifier (e.g., "Week 1")
        json_file: JSON file with Classifier outputs
        delay: Seconds between requests (default: 0.001 for fast simulation)
    """
    
    print(f"Simulating {week_name}")
        
    # Load traffic data
    traffic_data = load_traffic_data(json_file)
    total_videos = len(traffic_data)
    
    print(f"Loaded {total_videos} videos from {Path(json_file).name}")
    print(f"Sending to API at {API_URL}/api/drift/collect-features")
    
    
    # Send each video to API
    batch_calculated = False
    for i, payload in enumerate(traffic_data, 1):
        if 'timestamp' not in payload:
            from datetime import datetime
            payload['timestamp'] = datetime.now().isoformat()

        response = send_to_api(payload)
        
        if response and isinstance(response, dict) and 'batch_progress' in response:
            progress = response['batch_progress']
                    
            # Print progress every 100 videos
            if i % 100 == 0 or progress['drift_calculated']:
                print(f"  Progress: {progress['current_count']}/{progress['batch_size']} "
                      f"({progress['percentage']:.1f}%)")
            
            # Check if drift was calculated
            if progress['drift_calculated'] and not batch_calculated:
                batch_calculated = True
                print(f"\n Batch Complete - Drift Calculated!")
                if 'drift_metrics' in response:
                    metrics = response['drift_metrics']
                    print(f"    PSI: {metrics['psi']:.4f}")
                    print(f"    Drift Status: {metrics['drift_status']}")
                    print(f"    Reliability: {metrics['reliability']}")
                print()
            
            else:
                # If the API returned an error (like 422 or 500)
                print(f"  Error at video {i}: {response}")
                break
        
        # Small delay to simulate real-time (optional)
        if delay > 0:
            time.sleep(delay)
    
    # Get final status
    
    print(f"Week Complete: Sent {total_videos} videos")
    
    status = get_system_status()
    if status:
        print(f"\nCurrent System Status:")
        print(f"  Reliability: {status['reliability']}")
        print(f"  PSI: {status['psi']}")
        print(f"  Badge: {status['badge_text']}")
        print(f"  Batches Analyzed: {status['total_batches_analyzed']}")


def main():
    """Run complete traffic simulation"""
    
   
    print("Live Traffic Simulation")
    print("Simulating Classifier sending features to Drift Monitor API")
    
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f" API is running at {API_URL}")
    except requests.exceptions.RequestException:
        print(f"  ERROR: API is not running at {API_URL}")
        print(f"  Start the API first: python api/app.py")
        return
    
    # Simulate Week 1: Healthy Traffic
    simulate_week(
        "WEEK 1: Healthy Traffic (No Drift)",
        "data/simulation/week1_healthy_traffic.json",  # Updated name
        delay=0.001
    )

    input("\nPress Enter to continue to Week 3 (or Ctrl+C to stop)...")

    # Simulate Week 3: Drifted Traffic
    simulate_week(
        "WEEK 3: Drifted Traffic (High Drift)",
        "data/simulation/week3_high_drift.json",       # Updated name
        delay=0.001
)
       
    print("Simulation Complete")
    
    print("\nCheck results:")
    print("  1. Browser: http://localhost:5001/admin/drift-dashboard")
    print("  2. CSV Log: outputs/results/drift_history.csv")
    print("  3. API Status: http://localhost:5001/api/system-reliability")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Simulation stopped by user")