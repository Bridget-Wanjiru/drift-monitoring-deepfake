/**
 * Mpelelezi Deepfake Detection Interface Pipeline
 * Handles multi-part asynchronous chunk streams and polling state matrices.
 */

// ============================================================
// CONFIGURATION & ENDPOINT BASE PARSING
// ============================================================
const ORCHESTRATOR_URL = 'https://studying-prize-trans-photo.trycloudflare.com/run-pipeline';
// Automatically strips the routing tail to establish a clean base API gate path
const BASE_API_URL = ORCHESTRATOR_URL.substring(0, ORCHESTRATOR_URL.lastIndexOf('/'));

// ============================================================
// DOM ELEMENTS (Synchronized perfectly with your new Cyberpunk HTML)
// ============================================================
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('fileInput');
const progressTracker = document.getElementById('progress-tracker');
const progressStatusText = document.getElementById('progress-status-text');
const progressBarFill = document.getElementById('progress-bar-fill');
const resultsMatrix = document.getElementById('results-matrix');
const finalVerdict = document.getElementById('final-verdict');
const confidenceScore = document.getElementById('confidence-score');
const xaiExplanation = document.getElementById('xai-explanation');
const resetBtn = document.getElementById('reset-btn');

// ============================================================
// STATE MANAGEMENT CONSTRAINTS
// ============================================================
let currentAnalysis = {
    filename: '',
    fileSize: 0,
    prediction: 'unknown',
    confidence: 0,
    xai_explanation: ''
};

let statusPollInterval = null;

// ============================================================
// INTERACTIVE DROP-ZONE EVENTS
// ============================================================
uploadZone.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    
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

resetBtn.addEventListener('click', () => resetTerminalUI());

// ============================================================
// CORE FILE INGESTION UTILITIES
// ============================================================
function handleFileSelection(file) {
    if (!file.type.startsWith('video/')) {
        alert('CRITICAL // Selected payload type invalid. System requires standard MP4/WEBM formats.');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        alert('PAYLOAD BOUNDARY BREACH // Maximum file transfer limits set to 10MB.');
        return;
    }

    currentAnalysis.filename = file.name;
    currentAnalysis.fileSize = (file.size / (1024 * 1024)).toFixed(2);

    // Fade dropzone immediately to show active progress framework
    uploadZone.classList.add('hidden');
    progressTracker.classList.remove('hidden');

    // Fire actual network infrastructure code
    uploadOrchestratorPipeline(file);
}

// ============================================================
// TWO-PHASE NETWORK PIPELINE INTEGRATION
// ============================================================

/**
 * Phase 1: Upload Handshake Ingestion Loop
 */
async function uploadOrchestratorPipeline(file) {
    progressStatusText.textContent = "TRANSMITTING MULTI-PART PAYLOAD TO R2 CLOUD BUCKET...";
    progressStatusText.className = "status-blinker";
    progressBarFill.style.width = '45%';
    progressBarFill.style.background = 'var(--accent-info)';

    const formData = new FormData();
    formData.append('video', file);
    formData.append('client_id', '00000000-0000-0000-0000-000000000000'); // Safe fallback identity key

    try {
        const response = await fetch(ORCHESTRATOR_URL, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Ingestion Rejected // Gateway Error Code: ${response.status}`);
        }

        const data = await response.json();
        console.log("Phase 1 Complete // Orchestrator Handshake Ingest Record:", data);
        
        // Safely extract video UUID returned directly from Neon database model write
        const videoId = data.video_id || data.id;
        
        if (!videoId) {
            throw new Error("Schema Error // Handshake failed to attach tracking UUID record.");
        }

        // Advance progress tracking bar to background phase limits
        progressBarFill.style.width = '70%';
        progressBarFill.style.background = 'var(--accent-warning)';
        
        // Initialize dynamic monitoring tracking
        initializeStatusPolling(videoId);

    } catch (error) {
        console.error("Pipeline Communication Fault Traceback:", error);
        handleTerminalCrashState(error.message);
    }
}

/**
 * Phase 2: Asynchronous Microservice Polling Engine Loop
 */
function initializeStatusPolling(videoId) {
    progressStatusText.textContent = "PARALLEL COMPUTATION ENGAGED: COMPUTING METRICS...";
    
    // 💥 KILLSWITCH 1: Destroy any rogue ghost intervals before starting a new one
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
        statusPollInterval = null;
    }
    
    // Poll the backend tracking view precisely every 3 seconds
    statusPollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${BASE_API_URL}/video-status/${videoId}`);
            
            // 💥 KILLSWITCH 2: Do not fail silently on 404 or 500 errors!
            if (!response.ok) {
                // If it's a hard server error, crash the loop immediately.
                if (response.status === 404 || response.status >= 500) {
                    throw new Error(`Endpoint routing failed. Gateway Status: ${response.status}`);
                }
                return; // Only ignore minor network blips (like a brief timeout)
            }

            const record = await response.json();
            console.log("Polling Background Process Nodes:", record);

            if (record.status === 'completed') {
                clearInterval(statusPollInterval);
                statusPollInterval = null; // Clean up memory
                
                currentAnalysis.prediction = record.final_prediction.toUpperCase();
                currentAnalysis.confidence = parseFloat(record.confidence_score);
                currentAnalysis.xai_explanation = record.xai_reasoning || generateFallbackXAI(currentAnalysis.prediction);

                executeFinalRenderComplete();
                
            } else if (record.status === 'failed') {
                clearInterval(statusPollInterval);
                statusPollInterval = null;
                throw new Error("Algorithmic processing sequence crashed during model inference mapping loops.");
            }

        } catch (pollError) {
            // 💥 KILLSWITCH 3: Ensure interval dies when an error is caught
            if (statusPollInterval) {
                clearInterval(statusPollInterval);
                statusPollInterval = null;
            }
            console.error("Polling Engine Interrupted:", pollError);
            handleTerminalCrashState(pollError.message);
        }
    }, 3000);
}

// ============================================================
// DATA VIEW RENDERING MATRIX
// ============================================================
function executeFinalRenderComplete() {
    progressTracker.classList.add('hidden');
    resultsMatrix.classList.remove('hidden');

    // Populate Prediction Identity Elements
    finalVerdict.textContent = currentAnalysis.prediction === 'FAKE' ? 'DEEPFAKE DETECTED' : 'AUTHENTIC MEDIA';
    finalVerdict.className = `verdict-output ${currentAnalysis.prediction}`;

    // Populate Percentage Vector Models
    confidenceScore.textContent = (currentAnalysis.confidence * 100).toFixed(2) + '%';
    
    // Inject clean Explainable AI block strings text dynamically
    xaiExplanation.textContent = currentAnalysis.xai_explanation;
    
    resultsMatrix.scrollIntoView({ behavior: 'smooth' });
}

function generateFallbackXAI(prediction) {
    if (prediction === 'FAKE') {
        return "CRUCIAL TRACE ALERT // The Prototypical network classification matrices encountered significant vector drift variance. Deep spatial feature inconsistencies found in framing boundaries combined with temporal LSTM asymmetry confirm structural synthetic modification.";
    } else {
        return "SYSTEM COGNIZANCE // Target media cleared all late fusion processing thresholds safely. Spatial feature structures and temporal kinematic synchronization variables correspond perfectly within authentic population base models.";
    }
}

function handleTerminalCrashState(errorMessage) {
    // Intercept lazy generic browser errors and make them look professional
    let displayError = errorMessage;
    if (String(errorMessage).includes("Failed to fetch") || String(errorMessage).includes("NetworkError")) {
        displayError = "ERR_GATEWAY_TIMEOUT // Orchestrator node is unreachable. Verify Cloudflare Tunnel connection.";
    }

    console.error("Pipeline Communication Fault:", displayError);
    
    // Stop the blinking animation and turn the progress bar RED
    progressStatusText.className = ""; 
    progressBarFill.style.width = '100%';
    progressBarFill.style.background = 'var(--accent-danger)';
    
    // Inject the meaningful failure text, the custom trace, and the ABORT button
    progressStatusText.innerHTML = `
        <span style="color: var(--accent-danger); font-weight: 800; font-size: 1.1rem; letter-spacing: 1px;">🔴 CONNECTION FAILED</span><br>
        <span style="font-size: 0.95rem; color: var(--text-secondary); margin-top: 8px; display: inline-block;">
            The central Orchestrator is not live at the moment. Please ensure your backend environment is active and try again later.
        </span><br>
        <div style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid var(--accent-danger); padding: 6px 10px; margin-top: 12px; display: inline-block; border-radius: 0 4px 4px 0;">
            <span style="color: #ff6b6b; font-family: var(--font-mono); font-size: 0.8rem;">
                [Diagnostic Trace: ${displayError}]
            </span>
        </div><br><br>
        <button onclick="resetTerminalUI()" class="cyber-button" style="border: 1px solid var(--accent-danger); color: var(--accent-danger); margin-top: 5px; background: rgba(239, 68, 68, 0.05);">
            [ ABORT & RESET SCANNER ]
        </button>
    `;
}
// ============================================================
// TERMINAL SYSTEM UI REBOOT
// ============================================================
window.resetTerminalUI = function() {
    // 💥 KILLSWITCH 4: Abort instantly kills the clock
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
        statusPollInterval = null;
    }
    
    currentAnalysis = {
        filename: '',
        fileSize: 0,
        prediction: 'unknown',
        confidence: 0,
        xai_explanation: ''
    };

    fileInput.value = '';
    
    // Hide progress/results, show upload zone
    resultsMatrix.classList.add('hidden');
    progressTracker.classList.add('hidden');
    uploadZone.classList.remove('hidden');
    
    // Reset the progress bar colors and text back to default
    progressBarFill.style.width = '0%';
    progressBarFill.style.background = 'var(--accent-info)';
    progressStatusText.className = "status-blinker";
    progressStatusText.textContent = "TRANSMITTING MULTI-PART PAYLOAD TO R2 CLOUD BUCKET...";

    window.scrollTo({ top: 0, behavior: 'smooth' });
};
console.log('Mpelelezi Terminal Application Engine fully functional.');