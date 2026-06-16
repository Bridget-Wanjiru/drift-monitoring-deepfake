# Drift Monitoring Microservice

Component 5 of the Deepfake Detection System

## Purpose
Monitors distributional drift in Meta-Learning Classifier outputs to detect when the model encounters novel deepfake types.

## Author
Bridget Wanjiru

Mpelelezi is a web-based machine learning pipeline designed to identify manipulated audiovisual media in real-time while actively monitoring its own statistical reliability. Unlike static classification models that silently degrade over time, Mpelelezi integrates an MLOps perspective directly into the user experience.

The system utilizes a late-fusion approach, combining MesoInception-4 models for spatial feature extraction with LSTM networks for temporal kinematic synchronization. Crucially, an asynchronous background engine continually evaluates model decay by calculating the Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) metrics against a "Golden Standard" baseline, ensuring the system remains resilient in dynamic, adversarial environments.


## Architecture

Note: The system utilizes a decoupled microservice architecture, separating the heavy video ingestion handshake from the lightweight status-polling engine to keep the browser responsive during deep learning inference.*

## Tech Stack

Frontend (Client-Side)
    Languages: HTML5, CSS3 (Custom Neon Cyberpunk Theme), Vanilla JavaScript
    Responsibilities:Drag-and-(Explainable AI) diagnostics.

Backend (Orchestration & Inference)
     Framework: Python 3.10+, FastAPI
     Machine Learning: PyTorch, OpenCV, NumPy, SciPy (for statistical drift methods)
     Responsibilities: Multipart payload routing, parallel CV/LSTM model inference, and background drift calculation      (`drift_detector.py`).

## Data Layer & Networking
   Database: Neon (Serverless PostgreSQL) for state management and drift metrics.
   Storage: Cloudflare R2 Storage for raw video archiving.
  Networking:Cloudflare Tunnels for secure local-to-web routing (bypassing NAT/firewalls and enforcing HTTPS).

## Technology Stack
- Python 3.11+
- FastAPI (REST API)
- NumPy/SciPy (Statistical testing)
- Evidently AI (Dashboard)
