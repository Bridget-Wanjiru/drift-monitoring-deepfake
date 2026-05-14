"""
Monitoring Framework - Batch Collection & Orchestration
Collects 16-dim features from Classifier, triggers drift detection when batch full
"""

import numpy as np
from pathlib import Path
from datetime import datetime
import csv
from src.drift_detector import DriftDetector


class MonitoringFramework:
    """
    Orchestrates drift monitoring workflow:
    1. Collect features from Classifier API (one at a time)
    2. Buffer in memory until batch_size reached (1000)
    3. Calculate drift (PSI + KS test)
    4. Log results to CSV
    5. Update current reliability status
    """
    
    def __init__(self, reference_path, config_path='config/thresholds.yaml', batch_size=1000):
        """
        Initialize monitoring framework
        
        Args:
            reference_path: Path to reference features (training baseline)
            config_path: Path to thresholds configuration
            batch_size: Number of features to collect before calculating drift
        """
        # Initialize drift detector
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
        print(f"  Logging to: {self.history_file}")
    
    
    def add_features(self, features, video_id=None, prediction=None, confidence=None):
        """
        Add single feature vector to batch buffer
        This is called by your API when Classifier sends a video's features
        
        Args:
            features: 16-dim feature array (from Classifier JSON)
            video_id: Video UUID (optional, for logging)
            prediction: "real" or "fake" (optional)
            confidence: Confidence score 0-1 (optional)
        
        Returns:
            dict with batch progress and drift metrics (if batch complete)
        """
        # Ensure features are 1D array of length 16
        features = np.array(features).flatten()
        
        if len(features) != self.detector.n_features:
            raise ValueError(
                f"Expected {self.detector.n_features} features, got {len(features)}"
            )
        
        # Add to buffer
        self.feature_buffer.append(features)
        current_count = len(self.feature_buffer)
        
        # Check if batch is complete
        drift_calculated = False
        drift_results = None
        
        if current_count >= self.batch_size:
            # Batch full - calculate drift!
            drift_results = self._calculate_batch_drift()
            drift_calculated = True
            
            # Reset buffer for next batch
            self.feature_buffer = []
            self.batch_count += 1
        
        # Return progress
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
        """
        Internal: Calculate drift for current batch
        Called automatically when batch reaches 1000 features
        """
        # Convert buffer to NumPy array
        batch_array = np.array(self.feature_buffer)
        
        print(f"\nCalculating drift for batch {self.batch_count + 1}")
        print(f"  Batch size: {batch_array.shape[0]} samples")
        
        # Run drift detection
        results = self.detector.detect_drift(batch_array)
        
        # Update current status
        self.current_psi = results['psi']
        self.current_drift_status = results['drift_status']
        self.current_reliability = results['reliability']
        self.last_calculation_time = datetime.now()
        
        # Log to CSV
        self._log_to_history(results)
        
        # Store in memory
        self.drift_history.append({
            'batch_id': self.batch_count + 1,
            'timestamp': self.last_calculation_time,
            'results': results
        })
        
        print(f"  PSI: {results['psi']:.4f}")
        print(f"  Drift Status: {results['drift_status']}")
        print(f"  Reliability: {results['reliability']}")
        
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
        """
        Get current reliability status for API response
        This is what your FastAPI sends to the Frontend
        
        Returns:
            dict with badge_color, badge_text, user_message
        """
        # Determine badge appearance based on reliability
        if self.current_reliability == "High":
            badge_color = "green"
            badge_text = "System Operating Normally"
            show_message = False
            user_message = ""
        
        elif self.current_reliability == "Moderate":
            badge_color = "yellow"
            badge_text = " Caution: Unusual Patterns Detected"
            show_message = True
            user_message = (
                "Our system is encountering videos with characteristics different "
                "from our training data. Results may show higher uncertainty. "
                "For critical decisions, we recommend seeking additional verification."
            )
        
        elif self.current_reliability == "Caution":
            badge_color = "red"
            badge_text = " Warning: System Reliability Compromised"
            show_message = True
            user_message = (
                "IMPORTANT: Our system is encountering significantly different deepfake "
                "types than those in our training data. Detection accuracy may be reduced. "
                "We strongly recommend manual verification by a media forensics expert."
            )
        
        else:  # CHECKING
            badge_color = "gray"
            badge_text = " System Initializing"
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
        """
        Process an entire batch from .npy file (for testing)
        
        Args:
            batch_path: Path to .npy file with features
            batch_name: Name for this batch in logs
        
        Returns:
            dict with drift results
        """
        print(f"\nProcessing batch from file: {batch_path}")
        
        # Load batch
        batch_data = np.load(batch_path)
        print(f"  Loaded {batch_data.shape[0]} samples")
        
        # Calculate drift
        results = self.detector.detect_drift(batch_data)
        
        # Update status
        self.current_psi = results['psi']
        self.current_drift_status = results['drift_status']
        self.current_reliability = results['reliability']
        self.last_calculation_time = datetime.now()
        
        # Log
        self._log_to_history(results)
        
        # Store
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


# Testing code
if __name__ == '__main__':
    print("Monitoring Framework - Test Run")
    
    
    # Initialize framework
    framework = MonitoringFramework(
        reference_path='data/reference/train_features.npy',
        batch_size=100  # Smaller for testing
    )
    
    # TEST 1: Process healthy traffic batch
    print("\nTEST 1: Healthy Traffic")
    
    # UPDATED PATH BELOW:
    results1 = framework.process_batch_file(
        'data/simulation/week1_features.npy', 
        batch_name='healthy_week1'
    )
    
    status1 = framework.get_reliability_status()
    print(f"\nFrontend Badge: {status1['badge_text']}")
    
    # TEST 2: Process drifted traffic batch
    print("\nTEST 2: Drifted Traffic")
    
    # UPDATED PATH BELOW:
    results2 = framework.process_batch_file(
        'data/simulation/week3_features.npy', 
        batch_name='drifted_week3'
    )
    
    status2 = framework.get_reliability_status()
    print(f"\nFrontend Badge: {status2['badge_text']}")