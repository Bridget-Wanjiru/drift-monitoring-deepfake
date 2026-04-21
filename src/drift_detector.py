"""
Drift Detector - PSI and KS Test Implementation
Core statistical drift detection engine
"""

import numpy as np
from scipy import stats
import yaml
from pathlib import Path


class DriftDetector:
    """
    Detects distributional drift using PSI and KS test
    """
    
    def __init__(self, reference_path, config_path='config/thresholds.yaml'):
        """
        Initialize drift detector
        
        Args:
            reference_path: Path to reference features (.npy file, shape: n×16)
            config_path: Path to threshold configuration
        """
        self.reference = np.load(reference_path)
        
        if len(self.reference.shape) != 2:
            raise ValueError(f"Reference must be 2D array, got {self.reference.shape}")
        
        self.n_samples, self.n_features = self.reference.shape
        
        # Ensure the config file exists before loading
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Config not found at {config_path}. Please create it first.")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.psi_moderate = self.config['psi']['moderate']
        self.psi_high = self.config['psi']['high']
        self.ks_alpha = self.config['ks_test']['significance_level']
        
        print(f"Drift Detector Initialized")
        print(f"  Reference: {self.n_samples} samples × {self.n_features} features")
        print(f"  PSI thresholds: moderate={self.psi_moderate}, high={self.psi_high}")
    
    def calculate_psi(self, current_data, num_bins=10):
        """
        Calculate Population Stability Index
        
        Formula: PSI = Σ[(actual% - expected%) × ln(actual%/expected%)]
        """
        if current_data.shape[1] != self.n_features:
            raise ValueError(
                f"Feature mismatch: expected {self.n_features}, got {current_data.shape[1]}"
            )
        
        psi_values = []
        
        for feature_idx in range(self.n_features):
            ref_feature = self.reference[:, feature_idx]
            curr_feature = current_data[:, feature_idx]
            
            # Create bins from reference distribution
            percentiles = np.linspace(0, 100, num_bins + 1)
            bin_edges = np.percentile(ref_feature, percentiles)
            bin_edges = np.unique(bin_edges) # Handle low-variance features
            
            if len(bin_edges) < 2:
                continue
            
            # Calculate percentages in each bin
            ref_counts, _ = np.histogram(ref_feature, bins=bin_edges)
            curr_counts, _ = np.histogram(curr_feature, bins=bin_edges)
            
            # Add small epsilon (1e-6) to avoid division by zero or log(0)
            ref_percents = (ref_counts + 1e-6) / (ref_counts.sum() + 1e-6 * len(ref_counts))
            curr_percents = (curr_counts + 1e-6) / (curr_counts.sum() + 1e-6 * len(curr_counts))
            
            # PSI formula for this specific feature dimension
            psi_feature = np.sum(
                (curr_percents - ref_percents) * np.log(curr_percents / ref_percents)
            )
            psi_values.append(psi_feature)
        
        # Return the average PSI across all 16 dimensions
        return float(np.mean(psi_values)) if psi_values else 0.0
    
    def calculate_ks_test(self, current_data):
        """
        Kolmogorov-Smirnov test: Checks if two samples come from the same distribution
        """
        ks_statistics = []
        p_values = []
        
        for feature_idx in range(self.n_features):
            ref_feature = self.reference[:, feature_idx]
            curr_feature = current_data[:, feature_idx]
            
            # Perform two-sample KS test
            ks_stat, p_val = stats.ks_2samp(ref_feature, curr_feature)
            
            ks_statistics.append(ks_stat)
            p_values.append(p_val)
        
        # Return average statistic and the most significant (minimum) p-value
        return float(np.mean(ks_statistics)), float(np.min(p_values))
    
    def detect_drift(self, current_data):
        """
        Complete drift detection analysis combining PSI and KS test
        """
        psi = self.calculate_psi(current_data)
        ks_stat, p_value = self.calculate_ks_test(current_data)
        
        # Classify drift level based on PSI
        if psi < self.psi_moderate:
            drift_status = "none"
            reliability = "HIGH"
        elif psi < self.psi_high:
            drift_status = "moderate"
            reliability = "MODERATE"
        else:
            drift_status = "high"
            reliability = "CAUTION"
        
        # Statistical significance check
        ks_significant = p_value < self.ks_alpha
        
        return {
            'psi': psi,
            'ks_statistic': ks_stat,
            'ks_pvalue': p_value,
            'ks_significant': ks_significant,
            'drift_status': drift_status,
            'reliability': reliability,
            'n_current_samples': current_data.shape[0],
            'n_reference_samples': self.n_samples
        }


if __name__ == '__main__':
    # Local Test Block
   
    print("Drift Detector - Test Run")
    
    
    # Initialize using your training baseline
    detector = DriftDetector('data/reference/train_features.npy')
    
    # TEST 1: Healthy (Week 1)
    print("\n[TEST 1] Healthy Traffic (Expected: none/HIGH)")
    
    try:
        healthy = np.load('data/simulation/week1_features.npy')
        results = detector.detect_drift(healthy)
        print(f"  PSI: {results['psi']:.4f}")
        print(f"  Drift Status: {results['drift_status']}")
        print(f"  Reliability: {results['reliability']}")
        print(f"  KS p-value: {results['ks_pvalue']:.4f}")
    except FileNotFoundError:
        print("  Error: data/simulation/week1_features.npy not found.")
    
    # TEST 2: Drifting (Week 3)
    print("\n[Test 2] Drifted Traffic (Expected: high/CAUTION)")
    
    try:
        drifted = np.load('data/simulation/week3_features.npy')
        results_drift = detector.detect_drift(drifted)
        print(f"  PSI: {results_drift['psi']:.4f}")
        print(f"  Drift Status: {results_drift['drift_status']}")
        print(f"  Reliability: {results_drift['reliability']}")
        print(f"  KS p-value: {results_drift['ks_pvalue']:.4f}")
    except FileNotFoundError:
        print("  ERROR: data/simulation/week3_features.npy not found.")