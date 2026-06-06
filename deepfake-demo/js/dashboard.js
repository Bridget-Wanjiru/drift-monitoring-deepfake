/**
 * System Health Dashboard
 * Generates realistic-looking metric updates
 */

// ============================================================
// DOM Elements
// ============================================================

const systemStatus = document.getElementById('systemStatus');
const apiResponse = document.getElementById('apiResponse');
const modelAccuracy = document.getElementById('modelAccuracy');
const videosAnalyzed = document.getElementById('videosAnalyzed');
const lastUpdateTime = document.getElementById('lastUpdateTime');

const latencyChart = document.getElementById('latencyChart');
const accuracyChart = document.getElementById('accuracyChart');
const latencyLine = document.getElementById('latencyLine');
const accuracyLine = document.getElementById('accuracyLine');

const queueInProgress = document.getElementById('queueInProgress');
const queueWaiting = document.getElementById('queueWaiting');
const queueCompleted = document.getElementById('queueCompleted');

const driftIndicator = document.getElementById('driftIndicator');
const driftHealth = document.getElementById('driftHealth');
const driftMessage = document.getElementById('driftMessage');


// ============================================================
// State Management
// ============================================================

let metrics = {
    latency: [14, 16, 13, 15, 17, 14, 12, 16, 15, 18],
    accuracy: [95.8, 96.1, 96.0, 96.3, 96.2, 96.4, 96.1, 96.2, 96.3, 96.2],
    apiLatency: 14,
    modelAccuracy: 96.2,
    videosAnalyzed: 1247,
    queueInProgress: 3,
    queueWaiting: 12,
    queueCompleted: 342,
    driftHealth: 'HEALTHY',
    driftPsi: 0.084
};


// ============================================================
// INITIALIZE CHARTS
// ============================================================

function initializeCharts() {
    updateLatencyChart();
    updateAccuracyChart();
}

function generateChartPoints(data) {
    const padding = 20;
    const width = 280;
    const height = 110;
    
    const minVal = Math.min(...data);
    const maxVal = Math.max(...data);
    const range = maxVal - minVal || 1;
    
    return data.map((val, idx) => {
        const x = padding + (idx / (data.length - 1)) * width;
        const y = height - ((val - minVal) / range) * height + padding;
        return `${x},${y}`;
    }).join(' ');
}

function updateLatencyChart() {
    latencyLine.setAttribute('points', generateChartPoints(metrics.latency));
}

function updateAccuracyChart() {
    accuracyLine.setAttribute('points', generateChartPoints(metrics.accuracy));
}


// ============================================================
// UPDATE METRICS
// ============================================================

function updateMetrics() {
    // Simulate slight variations
    metrics.apiLatency = Math.floor(Math.random() * 10) + 12;
    metrics.latency.shift();
    metrics.latency.push(metrics.apiLatency);
    
    metrics.modelAccuracy = (Math.random() * 2 + 95.1).toFixed(1);
    metrics.accuracy.shift();
    metrics.accuracy.push(parseFloat(metrics.modelAccuracy));
    
    metrics.videosAnalyzed += Math.floor(Math.random() * 5);
    metrics.queueInProgress = Math.max(0, metrics.queueInProgress + Math.floor(Math.random() * 3) - 1);
    metrics.queueWaiting = Math.max(0, metrics.queueWaiting + Math.floor(Math.random() * 5) - 2);
    metrics.queueCompleted += Math.floor(Math.random() * 8);
    
    // Update drift status
    if (Math.random() > 0.95) {
        metrics.driftHealth = ['HEALTHY', 'CAUTION', 'CRITICAL'][Math.floor(Math.random() * 3)];
        metrics.driftPsi = (Math.random() * 0.5 + 0.05).toFixed(4);
    }

    // Update UI
    updateDisplay();
    updateCharts();
}

function updateDisplay() {
    apiResponse.textContent = metrics.apiLatency + 'ms';
    modelAccuracy.textContent = metrics.modelAccuracy + '%';
    videosAnalyzed.textContent = metrics.videosAnalyzed.toLocaleString();
    
    queueInProgress.textContent = metrics.queueInProgress;
    queueWaiting.textContent = metrics.queueWaiting;
    queueCompleted.textContent = metrics.queueCompleted;
    
    updateDriftStatus();
    updateTimestamp();
}

function updateCharts() {
    updateLatencyChart();
    updateAccuracyChart();
}

function updateDriftStatus() {
    driftHealth.textContent = metrics.driftHealth;
    driftMessage.textContent = `PSI Score: ${metrics.driftPsi} (${
        metrics.driftHealth === 'HEALTHY' ? 'Normal' : 
        metrics.driftHealth === 'CAUTION' ? 'Elevated' : 
        'Critical'
    })`;
    
    driftIndicator.className = `drift-badge ${metrics.driftHealth.toLowerCase()}`;
    
    // Update status indicator color
    const indicator = driftIndicator.previousElementSibling?.previousElementSibling?.querySelector('.status-indicator');
    if (indicator) {
        indicator.className = 'status-indicator';
        if (metrics.driftHealth === 'HEALTHY') {
            indicator.classList.add('healthy');
        } else if (metrics.driftHealth === 'CAUTION') {
            indicator.classList.add('warning');
        }
    }
}

function updateTimestamp() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    
    lastUpdateTime.textContent = `${hours}:${minutes}:${seconds}`;
}


// ============================================================
// AUTO-UPDATE LOOP
// ============================================================

// Update metrics every 5 seconds
setInterval(() => {
    updateMetrics();
}, 5000);

// Initial update
updateMetrics();
initializeCharts();

console.log('Dashboard initialized and running');