"""
Dashboard Generator - Dynamic Neon Cyberpunk Edition
Connects to Neon to pull live telemetry and generates a matching sci-fi dark command viewport.
"""

import os
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine

#  Load variables from the root .env file automatically
load_dotenv()

def load_drift_history_from_neon():
    """Connects directly to Neon using secure .env configuration rules"""
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL missing from your root .env workspace layout!")

        # Enforce secure cloud parameters natively
        if "sslmode=require" not in DATABASE_URL:
            DATABASE_URL += "&sslmode=require" if "?" in DATABASE_URL else "?sslmode=require"
            
        engine = create_engine(
            DATABASE_URL,
            connect_args={"sslmode": "require"}
        )
        
        query = """
            SELECT 
                id AS batch_id, 
                calculated_at AS timestamp, 
                psi_score AS psi, 
                ks_statistic, 
                ks_pvalue, 
                CASE 
                    WHEN system_health = 'HEALTHY' THEN 'none'
                    WHEN system_health = 'CAUTION' THEN 'moderate'
                    ELSE 'high'
                END AS drift_status,
                system_health AS reliability
            FROM drift_metrics 
            ORDER BY calculated_at ASC
        """
        df = pd.read_sql(query, con=engine)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f" DATABASE CONNECTION ERROR: {e}")
        return pd.DataFrame()


def create_psi_trend_chart(df):
    """Create a dual-axis dark-themed matching Plotly chart showing both PSI and KS statistics"""
    from plotly.subplots import make_subplots
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(go.Scatter(
        x=df['batch_id'],
        y=df['psi'],
        mode='lines+markers',
        name='PSI Metric',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#00ff66') 
    ), secondary_y=False)
    
    fig.add_trace(go.Scatter(
        x=df['batch_id'],
        y=df['ks_statistic'],
        mode='lines+markers',
        name='KS Statistic',
        line=dict(color='#a855f7', width=2, dash='dot'),
        marker=dict(size=6, color='#dfa5f9')
    ), secondary_y=True)
    
    fig.add_hline(y=0.25, line_dash="dash", line_color="#f59e0b", line_width=1.5)
    fig.add_hline(y=0.35, line_dash="dash", line_color="#ef4444", line_width=1.5)
    
    fig.update_layout(
        title={"text": "System Stability Metrics: PSI & KS Trends Over Time", "font": {"color": "#3b82f6", "size": 16}},
        xaxis_title="Batch Identification Number",
        height=400,
        paper_bgcolor="#090d16", 
        plot_bgcolor="#090d16",
        font={"color": "#cbd5e1", "family": "'Inter', 'Segoe UI', sans-serif"},
        xaxis={"gridcolor": "#1e293b", "zerolinecolor": "#334155"},
        margin={"t": 50, "b": 50, "l": 60, "r": 60},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        annotations=[
            {"showarrow": False, "text": "PSI Caution (0.25)", "x": 1, "xanchor": "right", "xref": "x domain", "y": 0.25, "yanchor": "bottom", "font": {"color": "#f59e0b"}},
            {"showarrow": False, "text": "PSI Critical (0.35)", "x": 1, "xanchor": "right", "xref": "x domain", "y": 0.35, "yanchor": "bottom", "font": {"color": "#ef4444"}}
        ]
    )
    
    fig.update_yaxes(title_text="PSI Magnitude Scale", secondary_y=False, gridcolor="#1e293b", zerolinecolor="#334155")
    fig.update_yaxes(title_text="KS Statistic Scale (0 to 1)", secondary_y=True, showgrid=False)
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_recommendations(latest_reliability, latest_psi):
    """Generate dark UI matching recommendation alert panels"""
    if latest_reliability == "HEALTHY":
        return """
        <div class="alert-box success-panel">
            <h3>🟢 System operating within baseline thresholds</h3>
            <p>No action required. Model feature distribution variance is performing within expected parameters.</p>
            <p><strong>Recommendations:</strong></p>
            <ul>
                <li>Continue out-of-band monitoring sequences.</li>
                <li>No manual model lifecycle weights reload required.</li>
            </ul>
        </div>
        """
    elif latest_reliability == "CAUTION":
        return f"""
        <div class="alert-box warning-panel">
            <h3>🟡 Moderate feature distribution shift detected</h3>
            <p>Drift warning threshold reached (PSI: {latest_psi:.4f}). System encountering anomalous deepfake attributes.</p>
            <p><strong>Recommendations:</strong></p>
            <ul>
                <li>Flag pipeline logs for moderate trace observation.</li>
                <li>Collect data frames of incoming unknown synthetic formats.</li>
                <li>Plan expansion of the prototypical training cluster.</li>
            </ul>
            <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.9;"><strong>Suggested Lifecycle Refresh:</strong> Operational Window 14-21 Days</p>
        </div>
        """
    else:  # CRITICAL
        return f"""
        <div class="alert-box critical-panel">
            <h3>🔴 Critical Population Drift Alert</h3>
            <p>High data drift recorded (PSI: {latest_psi:.4f}). Target validation accuracy parameters compromised.</p>
            <p><strong>Urgent Recovery Protocols:</strong></p>
            <ul>
                <li><strong>URGENT:</strong> Initialize parallel feature retraining engine sequences immediately.</li>
                <li>Investigate source anomalies: Analyze structural R2 video payload changes.</li>
                <li>Deploy mitigation notifications: Inform consuming clients of accuracy variance.</li>
            </ul>
            <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.9;"><strong>SLA Breach Window:</strong> Enforcement Required Within 48 Hours</p>
        </div>
        """


def generate_dashboard_html(latest_reliability=None, latest_psi=None):
    """Generate complete dark-slate theme matching dashboard HTML safely"""
    df = load_drift_history_from_neon()
    
    if df.empty:
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Telemetry System - Connection Failure</title>
            <style>
                body { background-color: #090d16; color: #ef4444; font-family: monospace; text-align: center; padding: 100px 20px; }
            </style>
        </head>
        <body>
            <h1> DATASET SYNC LINK OFFLINE</h1>
            <p>Verify project environment string configurations inside your backend generator properties.</p>
        </body>
        </html>
        """
    
    latest = df.iloc[-1]
    latest_reliability = latest_reliability or latest['reliability']
    latest_psi = latest_psi or latest['psi']
    total_batches = len(df)
    
    psi_chart = create_psi_trend_chart(df)
    recommendations = generate_recommendations(latest_reliability, latest_psi)
    
    table_html = df[['batch_id', 'timestamp', 'psi', 'ks_statistic', 'ks_pvalue', 'drift_status', 'reliability']].to_html(
        index=False,
        classes='table',
        border=0
    )
    
    table_html = table_html.replace('<td>none</td>', '<td style="color: var(--accent-success); font-family: var(--font-mono);">none</td>')
    table_html = table_html.replace('<td>moderate</td>', '<td style="color: var(--accent-warning); font-family: var(--font-mono);">moderate</td>')
    table_html = table_html.replace('<td>high</td>', '<td style="color: var(--accent-danger); font-family: var(--font-mono);">high</td>')
    table_html = table_html.replace('<td>HEALTHY</td>', '<td><span class="badge success">HEALTHY</span></td>')
    table_html = table_html.replace('<td>CAUTION</td>', '<td><span class="badge warning">CAUTION</span></td>')
    table_html = table_html.replace('<td>CRITICAL</td>', '<td><span class="badge danger">CRITICAL</span></td>')

    table_html = table_html.replace('<th>batch_id</th>', '<th>Batch ID</th>')
    table_html = table_html.replace('<th>timestamp</th>', '<th>Timestamp Reference</th>')
    table_html = table_html.replace('<th>psi</th>', '<th>PSI Score</th>')
    table_html = table_html.replace('<th>ks_statistic</th>', '<th>KS Distance</th>')
    table_html = table_html.replace('<th>ks_pvalue</th>', '<th>KS p-Value</th>')
    table_html = table_html.replace('<th>drift_status</th>', '<th>Drift Status</th>')
    table_html = table_html.replace('<th>reliability</th>', '<th>SLA Grade</th>')

    # Standard string with absolutely NO f-string prefix or .format()
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mpelelezi Core System Drift Telemetry</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-primary: #090d16;
                --bg-secondary: #0f172a;
                --bg-tertiary: #1e293b;
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --accent-neon: #00ff66;
                --accent-info: #3b82f6;
                --accent-warning: #f59e0b;
                --accent-danger: #ef4444;
                --accent-purple: #a855f7;
                --font-sans: 'Inter', sans-serif;
                --font-mono: 'Space Mono', monospace;
            }

            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background-color: var(--bg-primary); color: var(--text-primary); font-family: var(--font-sans); line-height: 1.6; overflow-x: hidden; }
            
            .cyber-header { background-color: rgba(9, 13, 22, 0.85); backdrop-filter: blur(12px); border-bottom: 1px solid var(--bg-tertiary); position: sticky; top: 0; z-index: 1000; padding: 1.2rem 0; }
            .nav-container { max-width: 1200px; margin: 0 auto; padding: 0 2rem; display: flex; justify-content: space-between; align-items: center; }
            .logo-group { display: flex; align-items: center; gap: 0.75rem; }
            .logo-pulse { width: 10px; height: 10px; background-color: var(--accent-neon); border-radius: 50%; box-shadow: 0 0 10px var(--accent-neon); animation: pulse-glow 2s infinite; }
            .logo-group h1 { font-family: var(--font-mono); font-size: 1.4rem; font-weight: 800; letter-spacing: 2px; background: linear-gradient(135deg, var(--text-primary), var(--accent-info)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
            .nav-links { display: flex; align-items: center; gap: 1.5rem; }
            .nav-link { color: var(--text-secondary); text-decoration: none; font-size: 0.9rem; font-weight: 600; padding: 0.5rem 1rem; border-radius: 6px; transition: all 0.2s ease; }
            .nav-link:hover { color: var(--text-primary); background-color: var(--bg-secondary); }
            .nav-link.active-node { border: 1px solid var(--accent-info); color: var(--accent-info); background-color: rgba(59, 130, 246, 0.05); box-shadow: 0 0 15px rgba(59, 130, 246, 0.15); }
            
            .main-content { padding: 3rem 0; }
            .container { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
            .dashboard-panel { background-color: var(--bg-secondary); border: 1px solid var(--bg-tertiary); border-radius: 12px; padding: 2.5rem; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4); }
            
            .panel-header { border-bottom: 1px solid var(--bg-tertiary); padding-bottom: 1.5rem; margin-bottom: 2.5rem; }
            .panel-header h2 { font-family: var(--font-mono); font-size: 1.8rem; font-weight: 800; letter-spacing: -0.5px; color: var(--text-primary); }
            .subtitle { color: var(--text-secondary); font-family: var(--font-mono); font-size: 0.85rem; margin-top: 0.25rem; }
            
            .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-bottom: 3rem; }
            .status-card { background: var(--bg-primary); border: 1px solid var(--bg-tertiary); padding: 1.5rem; border-radius: 8px; text-align: center; transition: border-color 0.2s ease; }
            .status-card:hover { border-color: var(--accent-info); }
            .status-card h3 { margin: 0 0 0.75rem 0; color: var(--text-secondary); font-family: var(--font-mono); font-size: 11px; letter-spacing: 1px; text-transform: uppercase; }
            .status-card .value { font-size: 2rem; font-weight: 700; color: var(--accent-info); }
            .status-card .value-HEALTHY { color: var(--accent-neon); text-shadow: 0 0 10px rgba(0, 255, 102, 0.1); }
            .status-card .value-CAUTION { color: var(--accent-warning); }
            .status-card .value-CRITICAL { color: var(--accent-danger); text-shadow: 0 0 10px rgba(239, 68, 68, 0.1); }
            
            .section { margin: 3.5rem 0; }
            .section h2 { font-family: var(--font-mono); font-size: 1.1rem; color: var(--text-primary); margin-bottom: 1.5rem; letter-spacing: 0.5px; }
            .chart-container { background: var(--bg-primary); border: 1px solid var(--bg-tertiary); border-radius: 8px; padding: 1rem; }
            
            .alert-box { padding: 1.5rem; border-radius: 8px; border: 1px solid var(--bg-tertiary); }
            .success-panel { border-left: 4px solid var(--accent-neon); background: rgba(0, 255, 102, 0.01); }
            .success-panel h3 { color: var(--accent-neon); font-family: var(--font-mono); margin-bottom: 0.5rem; font-size: 1rem; }
            .warning-panel { border-left: 4px solid var(--accent-warning); background: rgba(245, 158, 11, 0.01); }
            .warning-panel h3 { color: var(--accent-warning); font-family: var(--font-mono); margin-bottom: 0.5rem; font-size: 1rem; }
            .critical-panel { border-left: 4px solid var(--accent-danger); background: rgba(239, 68, 68, 0.01); }
            .critical-panel h3 { color: var(--accent-danger); font-family: var(--font-mono); margin-bottom: 0.5rem; font-size: 1rem; }
            .alert-box ul { padding-left: 1.25rem; margin-top: 0.75rem; }
            .alert-box li { margin-bottom: 0.5rem; color: var(--text-secondary); font-size: 0.9rem; }
            
            .table-responsive { width: 100%; overflow-x: auto; border-radius: 8px; border: 1px solid var(--bg-tertiary); }
            .table { width: 100%; border-collapse: collapse; background: var(--bg-primary); margin: 0; }
            .table th, .table td { padding: 1rem 1.25rem; text-align: left; border-bottom: 1px solid var(--bg-tertiary); font-size: 0.85rem; }
            .table th { background-color: #060910; color: var(--text-primary); font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.5px; text-transform: uppercase; }
            .table tr:last-child td { border-bottom: none; }
            .table tr:hover { background: rgba(30, 41, 59, 0.3); }
            
            .badge { padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; font-family: var(--font-mono); }
            .badge.danger { background: rgba(239, 68, 68, 0.1); color: #ff6b6b; border: 1px solid var(--accent-danger); }
            .badge.success { background: rgba(0, 255, 102, 0.1); color: var(--accent-neon); border: 1px solid var(--accent-neon); }
            .badge.warning { background: rgba(245, 158, 11, 0.1); color: var(--accent-warning); border: 1px solid var(--accent-warning); }
            
            .footer-text { text-align: center; margin-top: 4rem; color: var(--text-secondary); font-family: var(--font-mono); font-size: 0.75rem; opacity: 0.5; }
            @keyframes pulse-glow { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.2); opacity: 0.5; } }
            @media (max-width: 768px) { body { padding: 0; } .dashboard-panel { padding: 1.5rem; } }
        </style>
    </head>
    <body>

        <header class="cyber-header">
            <div class="nav-container">
                <div class="logo-group">
                    <div class="logo-pulse"></div>
                    <h1>MPELELEZI</h1>
                </div>
                <nav class="nav-links">
                    <a href="../index.html" class="nav-link">Live Terminal</a>
                    <a href="#" class="nav-link active-node">System Health</a>
                </nav>
            </div>
        </header>

        <main class="main-content">
            <div class="container">
                <div class="dashboard-panel">
                    
                    <div class="panel-header">
                        <h2> SYSTEM METRICS REGISTRY </h2>
                        <p class="subtitle">Microservice Telemetry Console • Statistical Population Stability Index (PSI)</p>
                    </div>
                    
                    <div class="status-grid">
                        <div class="status-card">
                            <h3>Current Reliability</h3>
                            <div class="value value-__RELIABILITY__">__RELIABILITY__</div>
                        </div>
                        <div class="status-card">
                            <h3>Latest PSI Score</h3>
                            <div class="value" style="color: var(--accent-warning); font-family: var(--font-mono);">__LATEST_PSI__</div>
                        </div>
                        <div class="status-card">
                            <h3>Total Processed Batches</h3>
                            <div class="value" style="font-family: var(--font-mono);">__TOTAL_BATCHES__</div>
                        </div>
                        <div class="status-card">
                            <h3>Last Evaluation Check</h3>
                            <div class="value" style="font-size: 1.4rem; line-height: 48px; color: var(--text-secondary); font-family: var(--font-mono); font-weight: 500;">
                                __LATEST_TIME__
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Microservice Mitigation Protocol</h2>
                        __RECOMMENDATIONS__
                    </div>
                    
                    <div class="section">
                        <h2>Latent Distribution Stability Vector Trend</h2>
                        <div class="chart-container">
                            __PSI_CHART__
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Historical Drift Evaluation Database Logs</h2>
                        <div class="table-responsive">
                            __TABLE_HTML__
                        </div>
                    </div>
                    
                    <div class="footer-text">
                        <p>Mpelelezi Engineering Subsystem Telemetry • Re-Compiled: __COMPILE_TIME__</p>
                    </div>

                </div>
            </div>
        </main>
    </body>
    </html>
    """

    # Safe Replacement Engine
    html_template = html_template.replace("__RELIABILITY__", str(latest_reliability))
    html_template = html_template.replace("__LATEST_PSI__", f"{latest_psi:.4f}")
    html_template = html_template.replace("__TOTAL_BATCHES__", str(total_batches))
    html_template = html_template.replace("__LATEST_TIME__", latest['timestamp'].strftime('%H:%M:%S'))
    html_template = html_template.replace("__RECOMMENDATIONS__", recommendations)
    html_template = html_template.replace("__PSI_CHART__", psi_chart)
    html_template = html_template.replace("__TABLE_HTML__", table_html)
    html_template = html_template.replace("__COMPILE_TIME__", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    return html_template

def save_dashboard(latest_reliability=None, latest_psi=None, output_path='public/dashboard/index.html'):
    """Generate and save dashboard HTML directly to the Firebase public route"""
    html = generate_dashboard_html(latest_reliability, latest_psi)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    
    with open(target, "w", encoding="utf-8") as f:
         f.write(html)
        
    print(f"DYNAMIC TELEMETRY DEPLOYED TO FIREBASE CACHE: {target.resolve()}")
    return str(output_path)


if __name__ == '__main__':
    save_dashboard()