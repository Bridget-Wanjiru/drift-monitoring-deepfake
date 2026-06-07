"""
Dashboard Generator - Production Dark Neon Style
Creates HTML dashboard with matching website typography, neon aesthetics, and responsiveness.
"""

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime


def load_drift_history(csv_path='outputs/results/drift_history.csv'):
    """Load drift history from CSV"""
    if not Path(csv_path).exists():
        return pd.DataFrame()
    
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def create_psi_trend_chart(df):
    """Create a dual-axis dark-themed matching Plotly chart showing both PSI and KS statistics"""
    from plotly.subplots import make_subplots
    
    # Create a layout with two independent Y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 1. Add PSI trend line (Primary Y-Axis)
    fig.add_trace(go.Scatter(
        x=df['batch_id'],
        y=df['psi'],
        mode='lines+markers',
        name='PSI Metric',
        line=dict(color='#3b82f6', width=3), # Deep Blue
        marker=dict(size=8, color='#00ff00') # Glowing Neon Green
    ), secondary_y=False)
    
    # 2. Add KS Statistic trend line (Secondary Y-Axis)
    fig.add_trace(go.Scatter(
        x=df['batch_id'],
        y=df['ks_statistic'],
        mode='lines+markers',
        name='KS Statistic',
        line=dict(color='#a855f7', width=2, dash='dot'), # Electric Purple
        marker=dict(size=6, color='#dfa5f9')
    ), secondary_y=True)
    
    # Add horizontal threshold bars for PSI safety limits
    fig.add_hline(y=0.25, line_dash="dash", line_color="#f59e0b", line_width=1.5)
    fig.add_hline(y=0.35, line_dash="dash", line_color="#ef4444", line_width=1.5)
    
    fig.update_layout(
        title={"text": "System Stability Metrics: PSI & KS Trends Over Time", "font": {"color": "#3b82f6", "size": 16}},
        xaxis_title="Batch Identification Number",
        height=400,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font={"color": "#cbd5e1", "family": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"},
        xaxis={
            "gridcolor": "#1e293b",
            "zerolinecolor": "#334155"
        },
        margin={"t": 50, "b": 50, "l": 60, "r": 60},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        annotations=[
            {"showarrow": False, "text": "PSI Caution (0.25)", "x": 1, "xanchor": "right", "xref": "x domain", "y": 0.25, "yanchor": "bottom", "font": {"color": "#f59e0b"}},
            {"showarrow": False, "text": "PSI Critical (0.35)", "x": 1, "xanchor": "right", "xref": "x domain", "y": 0.35, "yanchor": "bottom", "font": {"color": "#ef4444"}}
        ]
    )
    
    # Define labels for both vertical axes separate scales
    fig.update_yaxes(title_text="PSI Magnitude Scale", secondary_y=False, gridcolor="#1e293b", zerolinecolor="#334155")
    fig.update_yaxes(title_text="KS Statistic Scale (0 to 1)", secondary_y=True, showgrid=False)
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_recommendations(latest_reliability, latest_psi):
    """Generate dark UI matching recommendation alert panels"""
    if latest_reliability == "HIGH":
        return """
        <div class="alert-box success-panel">
            <h3> The system is operating as required</h3>
            <p>No action required. Model is performing within expected parameters</p>
            <p><strong>Recommendations:</strong></p>
            <ul>
                <li>continue routine monitoring.</li>
                <li>No model updates needed.</li>
            </ul>
        </div>
        """
    
    elif latest_reliability == "MODERATE":
        return f"""
        <div class="alert-box warning-panel">
            <h3>Monitor trends</h3>
            <p>Drift detected (PSI: {latest_psi:.4f}). System encountering new deepfake characteristics.</p>
            <p><strong>Recommendations:</strong></p>
            <ul>
                <li>Continue monitoring - drift is moderate.</li>
                <li>Collect examples of new deepfake types.</li>
                <li>Consider expanding training dataset.</li>
            </ul>
            <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.9;"><strong>Suggested Lifecycle Model Refresh:</strong> Within 14-21 Days</p>
        </div>
        """
    
    else:  # CAUTION / LOW / CRITICAL
        return f"""
        <div class="alert-box critical-panel">
            <h3> Immediate Action Required</h3>
            <p>High drift detected (PSI: {latest_psi:.4f}). Model reliability compromised..</p>
            <p><strong>Urgent Recommendations::</strong></p>
            <ul>
                <li><strong>URGENT:</strong> Plan model retraining.</li>
                <li>Investigate: What changed in video types?</li>
                <li>Communicate: Inform users of uncertainty</li>
                <li>New training data is needed</li>
            </ul>
            <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.9;"><strong>SLA Execution Window:</strong> Critical Enforcement Within 48 Hours</p>
        </div>
        """


def generate_dashboard_html(latest_reliability=None, latest_psi=None):
    """Generate complete dark-slate theme matching dashboard HTML (Accepts arguments safely)"""
    df = load_drift_history()
    
    if df.empty:
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Drift Dashboard - Empty Context</title>
            <style>
                body { background-color: #0f172a; color: #f1f5f9; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 100px 20px; }
            </style>
        </head>
        <body>
            <h1> No Evaluation Stream Data Detected</h1>
            <p>Execute live system testing arrays to populate metrics tables.</p>
        </body>
        </html>
        """
    
    latest = df.iloc[-1]
    # Use computed properties if none were passed directly
    latest_reliability = latest_reliability or latest['reliability']
    latest_psi = latest_psi or latest['psi']
    total_batches = len(df)
    
    psi_chart = create_psi_trend_chart(df)
    recommendations = generate_recommendations(latest_reliability, latest_psi)
    
    # Process the HTML table columns including your KS variables cleanly
    table_html = df[['batch_id', 'timestamp', 'psi', 'ks_statistic', 'ks_pvalue', 'drift_status', 'reliability']].to_html(
        index=False,
        classes='table',
        border=0
    )
    
    # Add custom responsive styling replacements to row cells dynamically
    table_html = table_html.replace('<td>none</td>', '<td style="color: var(--accent-success);">none</td>')
    table_html = table_html.replace('<td>moderate</td>', '<td style="color: var(--accent-warning);">moderate</td>')
    table_html = table_html.replace('<td>high</td>', '<td style="color: var(--accent-danger);">high</td>')
    table_html = table_html.replace('<td>HIGH</td>', '<td><span class="badge success">HIGH</span></td>')
    table_html = table_html.replace('<td>CAUTION</td>', '<td><span class="badge danger">CAUTION</span></td>')
    table_html = table_html.replace('<td>MODERATE</td>', '<td><span class="badge warning">MODERATE</span></td>')

    # Fix generic Pandas header layout naming styles to look professional
    table_html = table_html.replace('<th>batch_id</th>', '<th>Batch ID</th>')
    table_html = table_html.replace('<th>timestamp</th>', '<th>Timestamp Reference</th>')
    table_html = table_html.replace('<th>psi</th>', '<th>PSI Score</th>')
    table_html = table_html.replace('<th>ks_statistic</th>', '<th>KS Distance</th>')
    table_html = table_html.replace('<th>ks_pvalue</th>', '<th>KS p-Value</th>')
    table_html = table_html.replace('<th>drift_status</th>', '<th>Drift Status</th>')
    table_html = table_html.replace('<th>reliability</th>', '<th>SLA Grade</th>')

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Engineering Core - System Drift Telemetry</title>
        <style>
            /* ============================================================
               GLOBAL THEMATIC STYLE CORE (Matching Landing Page App UI)
               ============================================================ */
            :root {{
                --bg-primary: #0f172a;
                --bg-secondary: #1e293b;
                --bg-tertiary: #334155;
                --text-primary: #f1f5f9;
                --text-secondary: #cbd5e1;
                --accent-success: #22c55e;
                --accent-warning: #f59e0b;
                --accent-danger: #ef4444;
                --accent-info: #3b82f6;
                --accent-neon: #00ff00;
                --font-primary: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}

            body {{
                background-color: var(--bg-primary);
                color: var(--text-primary);
                font-family: var(--font-primary);
                margin: 0;
                padding: 30px 20px;
                line-height: 1.6;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: linear-gradient(135deg, #1e293b 0%, #273549 100%);
                border: 1px solid var(--bg-tertiary);
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 25px rgba(0, 0, 0, 0.6);
            }}

            h1 {{
                font-size: 2.2rem;
                font-weight: 700;
                margin: 0 0 5px 0;
                background: linear-gradient(135deg, var(--accent-neon), var(--accent-info));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}

            .subtitle {{
                color: var(--text-secondary);
                font-size: 1rem;
                margin-bottom: 35px;
            }}

            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin-bottom: 35px;
            }}

            .status-card {{
                background: var(--bg-primary);
                border: 2px solid var(--bg-tertiary);
                padding: 22px;
                border-radius: 8px;
                text-align: center;
                transition: all 0.3s ease;
            }}

            .status-card:hover {{
                border-color: var(--accent-info);
                transform: translateY(-3px);
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
            }}

            .status-card h3 {{
                margin: 0 0 12px 0;
                color: var(--text-secondary);
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.8px;
            }}

            .status-card .value {{
                font-size: 32px;
                font-weight: 700;
                color: var(--accent-info);
            }}

            .status-card .value-HIGH {{ color: var(--accent-success); }}
            .status-card .value-MODERATE {{ color: var(--accent-warning); }}
            .status-card .value-CAUTION {{ color: var(--accent-danger); text-shadow: 0 0 10px rgba(239,68,68,0.2); }}

            .section {{
                margin: 45px 0;
            }}

            .section h2 {{
                font-size: 1.4rem;
                color: var(--accent-info);
                border-left: 4px solid var(--accent-neon);
                padding-left: 12px;
                margin-bottom: 20px;
            }}

            .chart-container {{
                background: var(--bg-primary);
                border: 2px solid var(--bg-tertiary);
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
            }}

            .alert-box {{
                padding: 25px;
                border-radius: 8px;
            }}
            .success-panel {{
                border-left: 5px solid var(--accent-success);
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.08) 0%, rgba(21, 128, 61, 0.04) 100%);
                border-top: 1px solid rgba(34, 197, 94, 0.15); border-right: 1px solid rgba(34, 197, 94, 0.15); border-bottom: 1px solid rgba(34, 197, 94, 0.15);
            }}
            .success-panel h3 {{ color: #51cf66; margin-top:0; }}
            
            .warning-panel {{
                border-left: 5px solid var(--accent-warning);
                background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(180, 83, 9, 0.04) 100%);
                border-top: 1px solid rgba(245, 158, 11, 0.15); border-right: 1px solid rgba(245, 158, 11, 0.15); border-bottom: 1px solid rgba(245, 158, 11, 0.15);
            }}
            .warning-panel h3 {{ color: #fcc419; margin-top:0; }}

            .critical-panel {{
                border-left: 5px solid var(--accent-danger);
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(153, 27, 27, 0.04) 100%);
                border-top: 1px solid rgba(239, 68, 68, 0.15); border-right: 1px solid rgba(239, 68, 68, 0.15); border-bottom: 1px solid rgba(239, 68, 68, 0.15);
            }}
            .critical-panel h3 {{ color: #ff6b6b; margin-top:0; }}

            .alert-box ul {{ padding-left: 20px; margin: 15px 0; }}
            .alert-box li {{ margin-bottom: 8px; color: var(--text-secondary); }}

            .table-responsive {{
                width: 100%;
                overflow-x: auto;
                border-radius: 8px;
                border: 1px solid var(--bg-tertiary);
            }}

            .table {{
                width: 100%;
                border-collapse: collapse;
                background: var(--bg-primary);
                margin: 0;
            }}

            .table th, .table td {{
                padding: 14px 16px;
                text-align: left;
                border-bottom: 1px solid var(--bg-tertiary);
                font-size: 0.95rem;
            }}

            .table th {{
                background-color: #090d16;
                color: var(--accent-info);
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.85rem;
                letter-spacing: 0.5px;
            }}

            .table tr:last-child td {{ border-bottom: none; }}
            .table tr:hover {{ background: rgba(51, 65, 85, 0.25); }}

            .badge {{
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            .badge.danger {{ background: rgba(239, 68, 68, 0.15); color: #ff6b6b; border: 1px solid var(--accent-danger); }}
            .badge.success {{ background: rgba(34, 197, 94, 0.15); color: #51cf66; border: 1px solid var(--accent-success); }}
            .badge.warning {{ background: rgba(245, 158, 11, 0.15); color: #fcc419; border: 1px solid var(--accent-warning); }}

            .footer-text {{
                text-align: center; 
                margin-top: 50px; 
                color: var(--text-secondary);
                font-size: 0.85rem;
                opacity: 0.7;
            }}

            @media (max-width: 768px) {{
                body {{ padding: 15px 10px; }}
                .container {{ padding: 20px; }}
                .status-card .value {{ font-size: 26px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1> Drift Monitoring Dashboard</h1>
            <p class="subtitle">Microservice Telemetry Console • Real-time Population Stability Monitoring</p>
            
            <div class="status-grid">
                <div class="status-card">
                    <h3>Current Reliability</h3>
                    <div class="value value-{latest_reliability}">{latest_reliability}</div>
                </div>
                <div class="status-card">
                    <h3>Latest PSI</h3>
                    <div class="value" style="color: var(--accent-warning);">{latest_psi:.4f}</div>
                </div>
                <div class="status-card">
                    <h3>Total Batches</h3>
                    <div class="value">{total_batches}</div>
                </div>
                <div class="status-card">
                    <h3>Last Updated</h3>
                    <div class="value" style="font-size: 1.1rem; line-height: 48px; color: var(--text-secondary); font-weight: 500;">
                        {latest['timestamp'].strftime('%H:%M:%S')}
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Microservice Action Protocol</h2>
                {recommendations}
            </div>
            
            <div class="section">
                <h2>Feature Vector Stability Trend</h2>
                <div class="chart-container">
                    {psi_chart}
                </div>
            </div>
            
            <div class="section">
                <h2>Drift Evaluation Logs</h2>
                <div class="table-responsive">
                    {table_html}
                </div>
            </div>
            
            <div class="footer-text">
                <p>System Telemetry Engine Port 8000 • Re-Calculated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>

        <script src="../js/dashboard.js"></script>
    </body>
    </html>
    """
    return html_template


def save_dashboard(output_path='public/dashboard/index.html'):
    """Generate and save dashboard HTML directly to the Firebase public route"""
    html = generate_dashboard_html()
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    
    with open(target, "w", encoding="utf-8") as f:
         f.write(html)
        
    print(f" UNIFIED TELEMETRY DEPLOYED: {target.resolve()}")
    return str(output_path)


if __name__ == '__main__':
    save_dashboard()