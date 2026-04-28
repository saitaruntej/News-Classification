import streamlit as st
import pandas as pd
import requests
import os
import time

st.set_page_config(
    page_title="Prism News Intelligence",
    page_icon="🔺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Prism UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-color: #0c0c0e;
        --sidebar-bg: #111114;
        --card-bg: #151518;
        --border-color: #2a2a2e;
        --text-primary: #f8f8f8;
        --text-secondary: #8c8c94;
        --accent-orange: #f59e0b;
        --accent-orange-dim: rgba(245, 158, 11, 0.15);
        --accent-green: #10b981;
        --font-sans: 'Inter', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }
    
    /* Global Styles */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-primary);
        font-family: var(--font-sans);
    }
    
    /* Hide top header and padding */
    header {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1200px;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }
    
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 5px;
    }
    .triangle-icon {
        width: 32px;
        height: 32px;
        stroke: var(--accent-orange);
        stroke-width: 2;
        fill: none;
    }
    .logo-text {
        font-weight: 800;
        font-size: 1.8rem;
        letter-spacing: -0.5px;
        color: white;
    }
    .logo-subtext {
        font-family: var(--font-mono);
        font-size: 0.7rem;
        letter-spacing: 2px;
        color: var(--text-secondary);
        margin-top: 4px;
        margin-bottom: 40px;
        text-transform: uppercase;
    }

    /* Sidebar Navigation */
    .nav-section {
        font-family: var(--font-mono);
        font-size: 0.65rem;
        letter-spacing: 1.5px;
        color: var(--text-secondary);
        margin-top: 25px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        margin-bottom: 4px;
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    .nav-item:hover {
        background-color: rgba(255,255,255,0.05);
    }
    .nav-item.active {
        background-color: var(--accent-orange-dim);
        color: var(--accent-orange);
        border-left: 3px solid var(--accent-orange);
    }
    .nav-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--accent-orange);
        margin-right: 12px;
    }
    .nav-dot.inactive {
        background-color: var(--text-secondary);
        opacity: 0.5;
    }

    /* Top Section */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 2rem;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .main-subtitle {
        font-family: var(--font-mono);
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    .model-tag {
        font-family: var(--font-mono);
        color: var(--accent-orange);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 4px;
        padding: 6px 12px;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
    }

    /* Input Box styling */
    .input-container-box {
        background-color: transparent;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 2rem;
    }
    .input-label {
        font-family: var(--font-mono);
        color: var(--text-secondary);
        font-size: 0.75rem;
        letter-spacing: 1px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    /* Override Streamlit text area */
    .stTextArea textarea {
        background-color: #1e1e21 !important;
        color: white !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-size: 1.2rem !important;
        padding: 15px !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--accent-orange) !important;
        box-shadow: 0 0 0 1px var(--accent-orange) !important;
    }
    
    .input-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 15px;
    }
    .char-count {
        font-family: var(--font-mono);
        color: var(--text-secondary);
        font-size: 0.75rem;
    }
    
    /* Custom button to look like Analyse */
    .stButton>button {
        background-color: transparent;
        border: 1px solid var(--border-color);
        color: white;
        font-family: var(--font-sans);
        font-weight: 600;
        border-radius: 6px;
        padding: 8px 20px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: rgba(255,255,255,0.05);
        border-color: white;
        color: white;
    }
    
    /* Cards Layout */
    .metric-card {
        background-color: transparent;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card.highlight {
        border-color: rgba(245, 158, 11, 0.4);
    }
    .card-title {
        font-family: var(--font-mono);
        color: var(--text-secondary);
        font-size: 0.7rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .card-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .card-value.orange {
        color: var(--accent-orange);
    }
    .card-subtext {
        font-family: var(--font-mono);
        color: var(--text-secondary);
        font-size: 0.75rem;
    }
    
    /* Confidence Bar */
    .conf-bar-bg {
        background-color: #2a2a2e;
        height: 4px;
        border-radius: 2px;
        width: 100%;
        margin-bottom: 10px;
        margin-top: 5px;
    }
    .conf-bar-fill {
        background-color: var(--accent-orange);
        height: 100%;
        border-radius: 2px;
    }

    /* Sentiment Layout */
    .sentiment-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .sentiment-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: var(--accent-green);
        display: inline-block;
        margin-right: 8px;
    }
    .sentiment-dot.negative { background-color: #ef4444; }
    .sentiment-dot.neutral { background-color: #8c8c94; }

    /* Pills Section */
    .section-title {
        font-family: var(--font-mono);
        color: var(--text-secondary);
        font-size: 0.75rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 15px;
        margin-top: 30px;
    }
    .pills-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding: 20px;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        margin-bottom: 30px;
    }
    .pill {
        font-family: var(--font-mono);
        font-size: 0.75rem;
        padding: 6px 12px;
        border-radius: 4px;
        border: 1px solid var(--border-color);
        background-color: transparent;
        color: var(--text-secondary);
    }
    .pill.active {
        border-color: rgba(245, 158, 11, 0.4);
        color: var(--accent-orange);
    }

    /* Recent Headlines List */
    .recent-list {
        border-top: 1px solid var(--border-color);
    }
    .recent-item {
        display: flex;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid var(--border-color);
    }
    .recent-tag {
        font-family: var(--font-mono);
        font-size: 0.65rem;
        padding: 3px 8px;
        border: 1px solid var(--border-color);
        border-radius: 3px;
        color: var(--text-secondary);
        width: 90px;
        text-align: center;
        margin-right: 20px;
    }
    .recent-text {
        font-size: 0.95rem;
        color: var(--text-primary);
        flex-grow: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .status-dot-bottom {
        position: absolute;
        bottom: 20px;
        left: 20px;
        font-family: var(--font-mono);
        font-size: 0.7rem;
        color: var(--text-secondary);
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    /* Hide main streamlit components we don't want */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <svg class="triangle-icon" viewBox="0 0 24 24">
            <polygon points="12,2 22,20 2,20"></polygon>
            <line x1="12" y1="2" x2="12" y2="20"></line>
        </svg>
        <span class="logo-text">Prism</span>
    </div>
    <div class="logo-subtext">NEWS INTELLIGENCE</div>
    
    <div class="nav-section">ANALYSE</div>
    <div class="nav-item active">
        <div class="nav-dot"></div> Live Prediction
    </div>
    <div class="nav-item">
        <div class="nav-dot inactive"></div> Batch Classify
    </div>
    
    <div class="nav-section">EXPLORE</div>
    <div class="nav-item">
        <div class="nav-dot inactive"></div> Dataset Analytics
    </div>
    <div class="nav-item">
        <div class="nav-dot inactive"></div> Category Trends
    </div>
    <div class="nav-item">
        <div class="nav-dot inactive"></div> Sentiment Map
    </div>
    
    <div class="nav-section">SYSTEM</div>
    <div class="nav-item">
        <div class="nav-dot inactive"></div> Model Config
    </div>
    <div class="nav-item">
        <div class="nav-dot inactive"></div> Retrain
    </div>
    
    <div class="status-dot-bottom">
        <div><span style="color:var(--accent-green)">●</span> API connected · 8000</div>
        <div style="opacity:0.5">DistilBERT · 7 classes</div>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN AREA ---
# Header
st.markdown("""
<div class="header-container">
    <div>
        <div class="main-title">Live Prediction</div>
        <div class="main-subtitle">Real-time headline classification</div>
    </div>
    <div class="model-tag">DISTILBERT-BASE-UNCASED</div>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_recent_headlines():
    try:
        df = pd.read_csv("combined_news.csv")
        return df['headline'].dropna().tolist()[-50:][::-1] # latest 50
    except:
        return []

# Defaults
if 'headline_widget' not in st.session_state:
    st.session_state.headline_widget = "elon musk and openai ceo sam altman head to court in high-stakes showdown over ai — ap news"
if 'prediction_data' not in st.session_state:
    st.session_state.prediction_data = None

def update_textarea():
    if st.session_state.search_box:
        st.session_state.headline_widget = st.session_state.search_box

st.markdown('<div class="input-label" style="margin-bottom: -15px;">🔍 SEARCH RECENT NEWS</div>', unsafe_allow_html=True)
recent_headlines = load_recent_headlines()
st.selectbox(
    "Search Recent News Suggestions", 
    options=[""] + recent_headlines, 
    index=0,
    key="search_box",
    on_change=update_textarea,
    label_visibility="collapsed"
)
st.markdown('<br>', unsafe_allow_html=True)

# Input Container
st.markdown('<div class="input-container-box"><div class="input-label">HEADLINE INPUT</div>', unsafe_allow_html=True)

# We use columns to put text area and button together to mimic the layout somewhat,
# but Streamlit's layout constraints mean the button has to be below or next to it.
# We will place the button on the right side using columns.
headline = st.text_area("", key="headline_widget", label_visibility="collapsed")

col_left, col_right = st.columns([4, 1])
with col_left:
    char_count = len(headline)
    st.markdown(f'<div class="char-count">{char_count} chars · truncated to 128 tokens</div>', unsafe_allow_html=True)

with col_right:
    # Use a container to right align the button
    st.markdown('<div style="display:flex; justify-content:flex-end;">', unsafe_allow_html=True)
    analyze_clicked = st.button("Analyse →")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

api_url = "http://127.0.0.1:8000"

if analyze_clicked:
    with st.spinner("Analyzing..."):
        try:
            response = requests.post(f"{api_url}/predict", json={"text": headline})
            if response.status_code == 200:
                st.session_state.prediction_data = response.json()
            else:
                st.error("API Error")
        except Exception as e:
            st.error(f"Connection failed: {e}")

# Display Results
data = st.session_state.prediction_data

if data:
    cat = data['category'].upper()
    conf = data['confidence'] * 100
    sent = data['sentiment'].capitalize()
    sent_score = data['sentiment_score']
    all_scores = data.get('all_scores', {})
    
    # Sort scores descending
    sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Determine sentiment dot color
    dot_class = "sentiment-dot"
    if sent.upper() == "NEGATIVE":
        dot_class += " negative"
    elif sent.upper() == "NEUTRAL":
        dot_class += " neutral"
        
    conf_msg = "Low — consider retraining" if conf < 50 else "High confidence"
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card highlight">
            <div class="card-title">CATEGORY</div>
            <div class="card-value orange">{cat}</div>
            <div class="card-subtext">Top prediction</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-title">CONFIDENCE</div>
            <div class="card-value">{conf:.1f}%</div>
            <div class="conf-bar-bg">
                <div class="conf-bar-fill" style="width: {conf}%"></div>
            </div>
            <div class="card-subtext">{conf_msg}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-title">SENTIMENT</div>
            <div class="sentiment-row">
                <div><span class="{dot_class}"></span><span style="font-size:1.2rem; font-weight:500;">{sent}</span></div>
                <div style="font-family:var(--font-mono); color:var(--text-secondary);">{sent_score:.2f}</div>
            </div>
            <div class="card-subtext" style="margin-top:10px;">{conf_msg if sent_score > 0.8 else "Moderate confidence"}</div>
        </div>
        """, unsafe_allow_html=True)

    # Pills Section
    st.markdown('<div class="section-title">ALL CATEGORY SCORES</div>', unsafe_allow_html=True)
    
    pills_html = '<div class="pills-container">'
    for label, score in sorted_scores:
        score_pct = score * 100
        active_class = " active" if label.upper() == cat else ""
        pills_html += f'<div class="pill{active_class}">{label.upper()} {score_pct:.0f}%</div>'
    pills_html += '</div>'
    
    st.markdown(pills_html, unsafe_allow_html=True)

else:
    # Placeholder if no data yet (for initial render without hitting API if you don't want to)
    st.info("Click 'Analyse →' to see predictions.")

# Recent Headlines
st.markdown('<div class="section-title">RECENT HEADLINES</div>', unsafe_allow_html=True)

# Load recent from csv if exists
recent_html = '<div class="recent-list">'
try:
    df = pd.read_csv("combined_news.csv")
    recent = df.tail(3).iloc[::-1]
    for _, row in recent.iterrows():
        c = row['category'].upper()
        h = row['headline']
        recent_html += f"""
        <div class="recent-item">
            <div class="recent-tag">{c}</div>
            <div class="recent-text">{h}</div>
            <div class="sentiment-dot" style="margin:0;"></div>
        </div>
        """
except Exception:
    # Fallback to mock data if csv not found or error
    mock_recent = [
        ("TECHNOLOGY", "apple unveils new iphone with ai chip and satellite messaging"),
        ("SCIENCE", "google announces breakthrough in quantum error correction research"),
        ("SPORTS", "underdog team wins dramatic overtime victory in world cup final")
    ]
    for c, h in mock_recent:
        recent_html += f"""
        <div class="recent-item">
            <div class="recent-tag">{c}</div>
            <div class="recent-text">{h}</div>
            <div class="sentiment-dot" style="margin:0;"></div>
        </div>
        """
recent_html += '</div>'

st.markdown(recent_html, unsafe_allow_html=True)

