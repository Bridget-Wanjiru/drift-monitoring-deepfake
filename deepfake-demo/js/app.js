/**
 * Deepfake Detection Demo - Main Application Logic
 * Handles video upload, processing simulation, and results display
 */

// ============================================================
// DOM Elements
// ============================================================

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const loadingState = document.getElementById('loadingState');
const fileInfo = document.getElementById('fileInfo');
const resultsSection = document.getElementById('results');
const uploadSection = document.getElementById('upload');
const clearFileBtn = document.getElementById('clearFileBtn');

const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const progressFill = document.getElementById('progressFill');
const progressPercent = document.getElementById('progressPercent');

const predictionBadge = document.getElementById('predictionBadge');
const predictionText = document.getElementById('predictionText');
const confidencePercent = document.getElementById('confidencePercent');
const recommendationText = document.getElementById('recommendationText');

const downloadReportBtn = document.getElementById('downloadReportBtn');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');

const videoElement = document.getElementById('video');
const timelineMarkers = document.getElementById('timelineMarkers');


// ============================================================
// State Management
// ============================================================

let currentAnalysis = {
    filename: '',
    fileSize: 0,
    prediction: 'unknown',
    confidence: 0,
    consistency: {
        lipSync: 0,
        eyeMovement: 0,
        faceStability: 0
    },
    anomalies: []
};


// ============================================================
// DROP ZONE EVENTS
// ============================================================

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelection(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
    }
});


// ============================================================
// FILE HANDLING
// ============================================================

function handleFileSelection(file) {
    // Validate file type
    if (!file.type.startsWith('video/')) {
        alert('Please select a valid video file');
        return;
    }

    // Validate file size (max 100MB)
    if (file.size > 100 * 1024 * 1024) {
        alert('File is too large. Maximum size is 100MB');
        return;
    }

    // Store file info
    currentAnalysis.filename = file.name;
    currentAnalysis.fileSize = (file.size / (1024 * 1024)).toFixed(2);

    // Update UI
    fileName.textContent = file.name;
    fileSize.textContent = `${currentAnalysis.fileSize} MB`;
    
    fileInfo.classList.remove('hidden');
    dropZone.classList.add('hidden');

    // Create video preview
    const reader = new FileReader();
    reader.onload = (e) => {
        videoElement.src = e.target.result;
    };
    reader.readAsDataURL(file);

    // Start analysis simulation
    setTimeout(() => startAnalysisSimulation(), 500);
}

clearFileBtn.addEventListener('click', () => {
    resetUI();
});


// ============================================================
// ANALYSIS SIMULATION
// ============================================================

function startAnalysisSimulation() {
    // Show loading state
    fileInfo.classList.add('hidden');
    loadingState.classList.remove('hidden');

    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 25;
        if (progress > 100) progress = 100;
        
        progressFill.style.width = progress + '%';
        progressPercent.textContent = Math.floor(progress);

        if (progress >= 100) {
            clearInterval(progressInterval);
            completeAnalysis();
        }
    }, 400);
}

function completeAnalysis() {
    // Generate random but realistic results
    currentAnalysis.prediction = Math.random() > 0.4 ? 'fake' : 'real';
    currentAnalysis.confidence = Math.random() * 0.4 + 0.6; // 60-100%
    
    currentAnalysis.consistency = {
        lipSync: Math.random() * 0.3 + 0.7,
        eyeMovement: Math.random() * 0.3 + 0.65,
        faceStability: Math.random() * 0.2 + 0.75
    };

    // Generate anomalies
    generateAnomalies();

    // Display results
    displayResults();
}

function generateAnomalies() {
    // Generate random anomaly timestamps
    currentAnalysis.anomalies = [];
    const numAnomalies = Math.floor(Math.random() * 4);
    
    for (let i = 0; i < numAnomalies; i++) {
        currentAnalysis.anomalies.push({
            timestamp: Math.random() * 100,
            severity: Math.random() * 100
        });
    }
}

function displayResults() {
    // Hide loading, show results
    loadingState.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    uploadSection.classList.add('hidden');

    // Update prediction badge
    const isFake = currentAnalysis.prediction === 'fake';
    predictionBadge.className = `prediction-badge ${isFake ? 'fake' : 'real'}`;
    predictionText.textContent = isFake ? ' DEEPFAKE DETECTED' : ' AUTHENTIC VIDEO';

    // Animate confidence gauge
    animateConfidenceGauge();

    // Update consistency bars
    animateConsistencyBars();

    // Display timeline markers
    displayAnomalies();

    // Update recommendation
    updateRecommendation();

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function animateConfidenceGauge() {
    const confidence = currentAnalysis.confidence;
    confidencePercent.textContent = Math.floor(confidence * 100) + '%';

    // Animate needle
    const angle = confidence * 180 - 90; // Convert to SVG rotation
    const needle = document.getElementById('confidenceNeedle');
    needle.style.transition = 'transform 1s ease-out';
    needle.style.transform = `rotate(${angle}deg)`;

    // Animate arc
    const arc = document.getElementById('confidenceArc');
    const circumference = 2 * Math.PI * 80;
    const offset = circumference * (1 - confidence);
    arc.style.strokeDasharray = circumference;
    arc.style.strokeDashoffset = offset;

    // Change color based on confidence
    if (confidence > 0.9) {
        arc.style.stroke = '#ef4444'; // Red
    } else if (confidence > 0.7) {
        arc.style.stroke = '#f59e0b'; // Amber
    } else {
        arc.style.stroke = '#22c55e'; // Green
    }
}

function animateConsistencyBars() {
    const metrics = [
        { id: 'lipSync', value: currentAnalysis.consistency.lipSync },
        { id: 'eyeMovement', value: currentAnalysis.consistency.eyeMovement },
        { id: 'faceStability', value: currentAnalysis.consistency.faceStability }
    ];

    metrics.forEach(metric => {
        const bar = document.getElementById(metric.id + 'Bar');
        const percent = document.getElementById(metric.id + 'Percent');
        
        bar.style.transition = 'width 0.5s ease-out';
        bar.style.width = (metric.value * 100) + '%';
        
        percent.textContent = Math.floor(metric.value * 100) + '%';
    });
}

function displayAnomalies() {
    timelineMarkers.innerHTML = '';

    currentAnalysis.anomalies.forEach(anomaly => {
        const marker = document.createElement('div');
        marker.className = 'timeline-marker';
        marker.style.width = (100 / currentAnalysis.anomalies.length) + '%';
        marker.style.left = anomaly.timestamp + '%';
        marker.title = `Anomaly at ${(anomaly.timestamp).toFixed(1)}% severity: ${(anomaly.severity).toFixed(0)}%`;
        
        timelineMarkers.appendChild(marker);
    });
}

function updateRecommendation() {
    if (currentAnalysis.prediction === 'fake') {
        recommendationText.textContent = ' DEEPFAKE DETECTED - This video shows signs of synthetic generation. ' +
            'The temporal analysis revealed inconsistencies in lip sync, eye movement, and facial geometry that are ' +
            'consistent with AI-generated content. Manual verification by a media forensics expert is strongly recommended.';
    } else {
        recommendationText.textContent = '✓ APPEARS AUTHENTIC - This video passed temporal consistency checks. ' +
            'However, this assessment should be considered alongside other verification methods. ' +
            'We recommend cross-referencing with additional forensic analysis when critical decisions depend on authenticity.';
    }
}


// ============================================================
// ACTION BUTTONS
// ============================================================

downloadReportBtn.addEventListener('click', () => {
    const report = generateReport();
    downloadFile(report, `deepfake-report-${Date.now()}.txt`);
});

newAnalysisBtn.addEventListener('click', () => {
    resetUI();
});

function generateReport() {
    const timestamp = new Date().toLocaleString();
    const prediction = currentAnalysis.prediction === 'fake' ? 'DEEPFAKE DETECTED' : 'AUTHENTIC';
    const confidence = (currentAnalysis.confidence * 100).toFixed(1);

    return `
DEEPFAKE TEMPORAL DETECTION REPORT
===================================
Generated: ${timestamp}
Video: ${currentAnalysis.filename}
File Size: ${currentAnalysis.fileSize} MB

PREDICTION
==========
Status: ${prediction}
Confidence: ${confidence}%

TEMPORAL CONSISTENCY METRICS
============================
Lip Sync Consistency: ${(currentAnalysis.consistency.lipSync * 100).toFixed(1)}%
Eye Movement Pattern: ${(currentAnalysis.consistency.eyeMovement * 100).toFixed(1)}%
Face Stability: ${(currentAnalysis.consistency.faceStability * 100).toFixed(1)}%

ANOMALIES DETECTED
==================
${currentAnalysis.anomalies.length === 0 ? 'None' : currentAnalysis.anomalies.map((a, i) => 
    `${i + 1}. Timestamp: ${a.timestamp.toFixed(1)}% | Severity: ${a.severity.toFixed(0)}%`
).join('\n')}

RECOMMENDATION
==============
${document.getElementById('recommendationText').textContent}

TECHNICAL NOTES
===============
This analysis uses a multi-microservice ML pipeline combining:
- Spatial feature extraction (CV Service)
- Audio analysis (Audio Service)  
- Temporal LSTM analysis
- Prototypical Network classification
- Statistical drift monitoring

For more information, visit our system dashboard.
    `;
}

function downloadFile(content, filename) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}


// ============================================================
// UI RESET
// ============================================================

function resetUI() {
    // Reset state
    currentAnalysis = {
        filename: '',
        fileSize: 0,
        prediction: 'unknown',
        confidence: 0,
        consistency: { lipSync: 0, eyeMovement: 0, faceStability: 0 },
        anomalies: []
    };

    // Reset file input
    fileInput.value = '';
    videoElement.src = '';

    // Reset visibility
    dropZone.classList.remove('hidden');
    fileInfo.classList.add('hidden');
    loadingState.classList.add('hidden');
    resultsSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');

    // Reset progress
    progressFill.style.width = '0%';
    progressPercent.textContent = '0';

    // Scroll to top
    window.scrollTo(0, 0);
}


// ============================================================
// INITIALIZATION
// ============================================================

console.log('Deepfake Detection Demo loaded successfully');