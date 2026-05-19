"""
Dashboard Generator
Creates HTML dashboard with PSI trends, drift history, and recommendations
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    """Create PSI trend line chart with threshold lines"""
    fig = go.Figure()
    
    # PSI trend line
    fig.add_trace(go.Scatter(
        x=df['batch_id'],
        y=df['psi'],
        mode='lines+markers',
        name='PSI',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8)
    ))
    
    # Threshold lines
    fig.add_hline(y=0.25, line_dash="dash", line_color="orange",
                  annotation_text="Moderate (0.25)")
    fig.add_hline(y=0.35, line_dash="dash", line_color="red",
                  annotation_text="High (0.35)")
    
    fig.update_layout(
        title="PSI Trend Over Time",
        xaxis_title="Batch ID",
        yaxis_title="PSI Value",
        height=400,
        template="plotly_white"
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_recommendations(latest_reliability, latest_psi):
    """Generate context-aware recommendations"""
    if latest_reliability == "HIGH":
        return """
        <div style="background: #d4edda; padding: 20px; border-radius: 5px; border-left: 4px solid #28a745;">
            <h3 style="color: #155724; margin-top: 0;">✓ System Healthy</h3>
            <p>No action required. Model is performing within expected parameters.</p>
            <p><strong>Recommendations:</strong></p>
            <ul>
                <li>Continue routine monitoring</li>
                <li>No model updates needed</li>
            </ul>
        </div>
        """
    
    elif latest_reliability == "MODERATE":
        return f"""
        <div style="background: #fff3cd; padding: 20px; border-radius: 5px; border-left: 4px solid #ffc107;">
            <h3 style="color: #856404; margin-top: 0;">⚠ Monitor Trends</h3>
            <p>Drift detected (PSI: {latest_psi:.4f}). System encountering new deepfake characteristics.</p>
            <p><strong>Recommendations:</strong></p>
            <ul>
                <li>Continue monitoring - drift is moderate</li>
                <li>Collect examples of new deepfake types</li>
                <li>Consider expanding training dataset</li>
                <li>Review recent video uploads for patterns</li>
            </ul>
            <p><strong>Estimated model refresh:</strong> 2-3 weeks</p>
        </div>
        """
    
    else:  # CAUTION
        return f"""
        <div style="background: #f8d7da; padding: 20px; border-radius: 5px; border-left: 4px solid #dc3545;">
            <h3 style="color: #721c24; margin-top: 0;"> Immediate Action Required</h3>
            <p>High drift detected (PSI: {latest_psi:.4f}). Model reliability compromised.</p>
            <p><strong>Urgent Recommendations:</strong></p>
            <ul>
                <li><strong>URGENT:</strong> Plan model retraining</li>
                <li>Investigate: What changed in video types?</li>
                <li>Communicate: Inform users of uncertainty</li>
                <li>Collect: New training data ASAP</li>
                <li>Consider: Temporarily disable auto-accept</li>
            </ul>
            <p><strong>Recommended action:</strong> Within 48 hours</p>
        </div>
        """


def generate_dashboard_html():
    """Generate complete dashboard HTML"""
    
    # Load data
    df = load_drift_history()
    
    if df.empty:
        return """
        <html>
        <head><title>Drift Dashboard</title></head>
        <body style="font-family: Arial, sans-serif; padding: 50px; text-align: center;">
            <h1>No Data Yet</h1>
            <p>Run the traffic simulation to generate drift data.</p>
            <p><code>python scripts/simulate_live_traffic.py</code></p>
        </body>
        </html>
        """
    
    # Get latest metrics
    latest = df.iloc[-1]
    latest_reliability = latest['reliability']
    latest_psi = latest['psi']
    total_batches = len(df)
    
    # Create PSI chart
    psi_chart = create_psi_trend_chart(df)
    
    # Generate recommendations
    recommendations = generate_recommendations(latest_reliability, latest_psi)
    
    # Create drift history table
    table_html = df[['batch_id', 'timestamp', 'psi', 'drift_status', 'reliability']].to_html(
        index=False,
        classes='table',
        border=0
    )
    
    # Complete HTML
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drift Monitoring Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #7f8c8d;
                margin-bottom: 30px;
            }}
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .status-card {{
                background: #ecf0f1;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }}
            .status-card h3 {{
                margin: 0 0 10px 0;
                color: #7f8c8d;
                font-size: 14px;
                font-weight: normal;
            }}
            .status-card .value {{
                font-size: 32px;
                font-weight: bold;
                color: #2c3e50;
            }}
            .chart-container {{
                margin: 30px 0;
            }}
            .table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            .table th, .table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ecf0f1;
            }}
            .table th {{
                background: #34495e;
                color: white;
                font-weight: bold;
            }}
            .table tr:hover {{
                background: #f8f9fa;
            }}
            .section {{
                margin: 40px 0;
            }}
            .section h2 {{
                color: #34495e;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Drift Monitoring Dashboard</h1>
            <p class="subtitle">Real-time system reliability monitoring</p>
            
            <div class="status-grid">
                <div class="status-card">
                    <h3>Current Reliability</h3>
                    <div class="value">{latest_reliability}</div>
                </div>
                <div class="status-card">
                    <h3>Latest PSI</h3>
                    <div class="value">{latest_psi:.4f}</div>
                </div>
                <div class="status-card">
                    <h3>Total Batches</h3>
                    <div class="value">{total_batches}</div>
                </div>
                <div class="status-card">
                    <h3>Last Updated</h3>
                    <div class="value" style="font-size: 16px;">{latest['timestamp'].strftime('%H:%M:%S')}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {recommendations}
            </div>
            
            <div class="section">
                <h2>PSI Trend</h2>
                <div class="chart-container">
                    {psi_chart}
                </div>
            </div>
            
            <div class="section">
                <h2>Drift History</h2>
                {table_html}
            </div>
            
            <div style="text-align: center; margin-top: 40px; color: #7f8c8d;">
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template


def save_dashboard(output_path='outputs/dashboards/dashboard.html'):
    """Generate and save dashboard HTML"""
    html = generate_dashboard_html()
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f" Dashboard saved to: {output_path}")
    return output_path


if __name__ == '__main__':
    print("Generating Dashboard...")
    path = save_dashboard()
    print(f"\nOpen in browser: file:///{Path(path).absolute()}")