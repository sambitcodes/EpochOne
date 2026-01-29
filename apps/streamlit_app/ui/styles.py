"""Global styling and theme configuration."""
import streamlit as st

def apply_theme():
    """Apply custom theme and styling."""
    st.markdown("""
    <style>
        /* Root variables */
        :root {
            --primary-color: #00d9ff;
            --secondary-color: #0284c7;
            --bg-dark: #0f1419;
            --bg-darker: #020617;
            --bg-card: #1a1f2e;
            --bg-elevated: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --border-color: #334155;
        }

        /* Body and main container */
        body {
            background-color: #0f1419;
            color: #f1f5f9;
        }

        [data-testid="stAppViewContainer"] {
            background-color: #0f1419;
        }

        [data-testid="stSidebar"] {
            background-color: #020617;
            border-right: 1px solid #334155;
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 2rem;
        }

        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #00d9ff;
            margin-bottom: 1rem;
        }

        h1 {
            color: #F1C40F !important;
            text-align: center;
            font-size: 3rem; /* Slightly bigger for impact */
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        h2 {
            font-size: 2rem;
            font-weight: 600;
        }

        h3 {
            font-size: 1.5rem;
            font-weight: 600;
        }

        /* Text */
        p {
            color: #cbd5e1;
            line-height: 1.6;
        }

        /* Buttons */
        .stButton > button,
        [data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(90deg, #6200EE, #E84118);
            color: #FFFFFF !important;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(98, 0, 238, 0.3);
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            opacity: 0.9;
            box-shadow: 0 6px 16px rgba(232, 65, 24, 0.4);
            transform: translateY(-2px);
        }

        .stButton > button:active,
        [data-testid="stFormSubmitButton"] > button:active {
            background-color: #0284c7;
        }

        /* Input fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            background-color: #1e293b;
            color: #f1f5f9;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 0.75rem;
            transition: border-color 0.3s ease;
        }

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #00d9ff;
            outline: none;
            box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.1);
        }

        /* Labels */
        .stLabel > label {
            color: #cbd5e1;
            font-weight: 500;
        }

        /* Tabs */
        .stTabs > [data-baseweb="tabs"] > [role="tablist"] {
            background-color: #1a1f2e;
            border-bottom: 1px solid #334155;
        }

        .stTabs > [data-baseweb="tabs"] > [role="tablist"] > button {
            color: #94a3b8;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }

        .stTabs > [data-baseweb="tabs"] > [role="tablist"] > button[aria-selected="true"] {
            color: #00d9ff;
            border-bottom-color: #00d9ff;
        }

        .stTabs > [data-baseweb="tabs"] > [role="tablist"] > button:hover {
            color: #38bdf8;
        }

        /* Dividers */
        .stDivider {
            border-color: #334155;
        }

        /* Messages */
        .stAlert {
            border-radius: 8px;
            padding: 1rem;
        }

        .stSuccess {
            background-color: rgba(34, 197, 94, 0.1);
            border-left: 4px solid #22c55e;
        }

        .stInfo {
            background-color: rgba(0, 217, 255, 0.1);
            border-left: 4px solid #00d9ff;
        }

        .stWarning {
            background-color: rgba(245, 158, 11, 0.1);
            border-left: 4px solid #f59e0b;
        }

        .stError {
            background-color: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #ef4444;
        }

        /* Expandable sections */
        .streamlit-expanderHeader {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #00d9ff;
        }

        .streamlit-expanderHeader:hover {
            background-color: #334155;
        }

        /* Metric containers */
        .metric-container {
            background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
            border-left: 4px solid #00d9ff;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background-color: #0f1419;
        }

        ::-webkit-scrollbar-thumb {
            background-color: #334155;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background-color: #475569;
        }

        /* Cards */
        .card {
            background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
            border: 1px solid #334155;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: #00d9ff;
            box-shadow: 0 8px 24px rgba(0, 217, 255, 0.1);
        }

        /* Utility classes */
        .text-muted {
            color: #94a3b8;
        }

        .text-secondary {
            color: #cbd5e1;
        }

        .text-primary {
            color: #00d9ff;
        }

        .mt-4 {
            margin-top: 1.5rem;
        }

        .mb-4 {
            margin-bottom: 1.5rem;
        }

        .p-4 {
            padding: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Hide sidebar nav if not authenticated
    if "access_token" not in st.session_state or not st.session_state.access_token:
        st.markdown("""
        <style>
            [data-testid="stSidebarNav"] { display: none; }
        </style>
        """, unsafe_allow_html=True)

def get_color_by_intensity(intensity: str) -> str:
    """Get color code by intensity level."""
    colors = {
        "easy": "#38bdf8",
        "moderate": "#00d9ff",
        "hard": "#f59e0b",
        "extreme": "#ef4444",
    }
    return colors.get(intensity, "#00d9ff")

def get_color_by_status(status: str) -> str:
    """Get color code by status."""
    colors = {
        "success": "#22c55e",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#00d9ff",
    }
    return colors.get(status, "#00d9ff")
