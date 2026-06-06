"""
Monitoring Framework - Batch Collection & Orchestration
Collects 16-dim features, updates Neon cloud tables, and refreshes the dashboard UI.
"""

import numpy as np
from pathlib import Path
from datetime import datetime
import csv
from src.drift_detector import DriftDetector
from src.db_service import DatabaseService          # Added cloud data connection layer
from src.dashboard_generator import save_dashboard   # Added UI automation link


class MonitoringFramework:
    """
    Orchestrates drift monitoring workflow:
    1. Collect features from Classifier API (one at a time)
    2. Buffer in memory until batch_size reached (1000)
    3. Calculate drift (PSI + KS test)
    4. Log results to Neon Cloud & local CSV
    5. Trigger live dashboard compilation
    """
    
    def __init__(self, reference_path, config_path='config/thresholds.yaml', batch_size=1000):
        """Initialize monitoring framework and connection pools"""
        self.detector = DriftDetector(reference_path, config_path)
        
        # Batch configuration
        self.batch_size = batch_size
        self.feature_buffer = []  # In-memory buffer for incoming features
        self.batch_count = 0
        
        # Current drift status
        self.current_psi = None
        self.current_drift_status = None
        self.current_reliability = "CHECKING"  # Until first batch processed
        self.last_calculation_time = None
        
        # History tracking
        self.drift_history = []
        self.history_file = Path("outputs/results/drift_history.csv")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV file with headers
        if not self.history_file.exists():
            with open(self.history_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'batch_id', 'timestamp', 'n_samples',
                    'psi', 'ks_statistic', 'ks_pvalue', 'ks_significant',
                    'drift_status', 'reliability'
                ])
        
        print(f"Monitoring Framework Initialized")
        print(f"  Batch size: {self.batch_size}")
        print(f"  Status: {self.current_reliability}")
        print(f"  Logging to: {self.history_file} & Neon Cloud Cluster")
    
    def add_features(self, features, video_id=None, prediction=None, confidence=None):
        """Add single feature vector to batch buffer"""
        features = np.array(features).flatten()
        
        if len(features) != self.detector.n_features:
            raise ValueError(
                f"Expected {self.detector.n_features} features, got {len(features)}"
            )
        
        self.feature_buffer.append(features)
        current_count = len(self.feature_buffer)
        
        drift_calculated = False
        drift_results = None
        
        if current_count >= self.batch_size:
            drift_results = self._calculate_batch_drift()
            drift_calculated = True
            
            self.feature_buffer = []
            self.batch_count += 1
        
        response = {
            'status': 'success',
            'batch_progress': {
                'current_count': len(self.feature_buffer),
                'batch_size': self.batch_size,
                'percentage': (len(self.feature_buffer) / self.batch_size) * 100,
                'drift_calculated': drift_calculated
            }
        }
        
        if drift_calculated and drift_results:
            response['drift_metrics'] = drift_results
        
        return response
    
    def _calculate_batch_drift(self):
        """Calculate drift and save to cloud backend and UI layers"""
        batch_array = np.array(self.feature_buffer)
        
        print(f"\nCalculating drift for batch {self.batch_count + 1}")
        print(f"  Batch size: {batch_array.shape[0]} samples")
        
        results = self.detector.detect_drift(batch_array)
        
        # Explicitly assign variables matching the mathematical tracker casing rules
        self.current_psi = results['psi']
        self.current_drift_status = results['drift_status']
        self.current_reliability = results['reliability'] # Stores "HIGH", "MODERATE", or "CAUTION"
        self.last_calculation_time = datetime.now()
        
        # 1. Write telemetry data to Local CSV History
        self._log_to_history(results)
        
        # 2. Write telemetry data to Neon PostgreSQL Cloud Cluster
        try:
            db_service = DatabaseService()
            # Map internal reliability values safely to Neon's SQL check constraint
            db_health_map = {"HIGH": "HEALTHY", "MODERATE": "CAUTION", "CAUTION": "CRITICAL"}
            db_health_status = db_health_map.get(str(results['reliability']).upper(), "HEALTHY")

            db_service.save_drift_metric(
                batch_sample_size=int(results['n_current_samples']),
                psi_score=float(results['psi']),
                ks_statistic=float(results['ks_statistic']),
                system_health=db_health_status
            )
            db_service.close()
            print("  Telemetry parameters saved to Neon Cloud Cluster.")
        except Exception as e:
            print(f"  Cloud telemetry persistence error: {e}")
            
        # 3. Compile your new dark neon styled dashboard template automatically
        try:
            save_dashboard()
        except Exception as e:
            print(f"  Dashboard generation error: {e}")
        
        self.drift_history.append({
            'batch_id': self.batch_count + 1,
            'timestamp': self.last_calculation_time,
            'results': results
        })
        
        return {
            'psi': results['psi'],
            'ks_statistic': results['ks_statistic'],
            'ks_pvalue': results['ks_pvalue'],
            'drift_status': results['drift_status'],
            'reliability': results['reliability']
        }
    
    def _log_to_history(self, results):
        """Log drift results to CSV file"""
        with open(self.history_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                self.batch_count + 1,
                datetime.now().isoformat(),
                results['n_current_samples'],
                f"{results['psi']:.4f}",
                f"{results['ks_statistic']:.4f}",
                f"{results['ks_pvalue']:.4f}",
                results['ks_significant'],
                results['drift_status'],
                results['reliability']
            ])
    
    def get_reliability_status(self):
        """Get current reliability status with fixed case-insensitive parsing"""
        # FIXED: Enforced capitalization matching rules (.upper()) to map status checks perfectly
        status_key = str(self.current_reliability).upper()
        
        if status_key == "HIGH":
            badge_color = "green"
            badge_text = "System Operating Normally"
            show_message = False
            user_message = ""
        
        elif status_key == "MODERATE":
            badge_color = "yellow"
            badge_text = "Caution: Unusual Patterns Detected"
            show_message = True
            user_message = (
                "Our system is encountering videos with characteristics different "
                "from our training data. Results may show higher uncertainty. "
                "For critical decisions, we recommend seeking additional verification."
            )
        
        elif status_key == "CAUTION":
            badge_color = "red"
            badge_text = "Warning: System Reliability Compromised"
            show_message = True
            user_message = (
                "IMPORTANT: Our system is encountering significantly different deepfake "
                "types than those in our training data. Detection accuracy may be reduced. "
                "We strongly recommend manual verification by a media forensics expert."
            )
        
        else:  # CHECKING / INITIALIZING
            badge_color = "gray"
            badge_text = "System Initializing"
            show_message = True
            user_message = (
                f"Our monitoring system is collecting initial data. "
                f"Results are available, but reliability assessment is pending. "
                f"Videos processed: {len(self.feature_buffer)} / {self.batch_size}"
            )
        
        return {
            'reliability': self.current_reliability,
            'psi': self.current_psi,
            'badge_color': badge_color,
            'badge_text': badge_text,
            'show_user_message': show_message,
            'user_message': user_message,
            'last_check': self.last_calculation_time.isoformat() if self.last_calculation_time else None,
            'videos_in_current_batch': len(self.feature_buffer),
            'total_batches_analyzed': self.batch_count
        }
    
    def process_batch_file(self, batch_path, batch_name="batch"):
        """Process an entire batch from .npy file (for testing)"""
        print(f"\nProcessing batch from file: {batch_path}")
        
        batch_data = np.load(batch_path)
        print(f"  Loaded {batch_data.shape[0]} samples")
        
        results = self.detector.detect_drift(batch_data)
        
        self.current_psi = results['psi']
        self.current_drift_status = results['drift_status']
        self.current_reliability = results['reliability']
        self.last_calculation_time = datetime.now()
        
        self._log_to_history(results)
        
        # Save validation updates to Cloud storage database layer natively
        try:
            db_service = DatabaseService()
           # Map internal reliability values safely to Neon's SQL check constraint
            db_health_map = {"HIGH": "HEALTHY", "MODERATE": "CAUTION", "CAUTION": "CRITICAL"}
            db_health_status = db_health_map.get(str(results['reliability']).upper(), "HEALTHY")

            db_service.save_drift_metric(
                batch_sample_size=int(results['n_current_samples']),
                psi_score=float(results['psi']),
                ks_statistic=float(results['ks_statistic']),
                system_health=db_health_status
            )
            db_service.close()
            print("  Batch file metrics committed to Neon Cloud.")
        except Exception as e:
            print(f"  Batch file cloud connection logging error: {e}")

        # Regenerate your dark UI template presentation view
        try:
            save_dashboard()
        except Exception as e:
            print(f"  UI presentation file save crash error: {e}")
        
        self.drift_history.append({
            'batch_id': batch_name,
            'timestamp': self.last_calculation_time,
            'results': results
        })
        
        print(f"\nResults for {batch_name}:")
        print(f"  PSI: {results['psi']:.4f}")
        print(f"  Drift Status: {results['drift_status']}")
        print(f"  Reliability: {results['reliability']}")
        
        return results


if __name__ == '__main__':
    print("Monitoring Framework - Test Run")
    framework = MonitoringFramework(
        reference_path='data/reference/train_features.npy',
        batch_size=100  
    )
    
    print("\nTEST 1: Healthy Traffic")
    results1 = framework.process_batch_file(
        'data/reference/train_features.npy',  # Fallback verify safety vector space array mapping
        batch_name='healthy_baseline_test'
    )