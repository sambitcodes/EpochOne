"""Reusable UI components for Streamlit."""
import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any

def metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    icon: Optional[str] = None,
    color: str = "#00d9ff"
):
    """
    Metric card component.
    
    Args:
        title: Card title
        value: Main value to display
        delta: Change indicator (e.g., "+412")
        icon: Emoji or icon
        color: Accent color
    """
    html = f"""
    <div style="
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
        border-left: 4px solid {color};
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <p style="margin: 0; color: #94a3b8; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">
                    {title}
                </p>
                <h3 style="margin: 0.5rem 0 0 0; color: #00d9ff; font-size: 2rem; font-weight: 600;">
                    {value}
                </h3>
                {f'<p style="margin: 0.5rem 0 0 0; color: #38bdf8; font-size: 0.875rem;">{delta}</p>' if delta else ''}
            </div>
            {f'<div style="font-size: 2rem;">{icon}</div>' if icon else ''}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def stat_box(
    label: str,
    value: str,
    sublabel: Optional[str] = None
):
    """
    Simple stat box.
    
    Args:
        label: Stat label
        value: Stat value
        sublabel: Optional secondary label
    """
    html = f"""
    <div style="
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #334155;
    ">
        <p style="margin: 0; color: #94a3b8; font-size: 0.875rem;">{label}</p>
        <h4 style="margin: 0.5rem 0 0 0; color: #f1f5f9; font-size: 1.5rem;">{value}</h4>
        {f'<p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.75rem;">{sublabel}</p>' if sublabel else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def progress_ring(
    percent: float,
    label: str,
    color: str = "#00d9ff"
):
    """
    Circular progress indicator.
    
    Args:
        percent: Progress percentage (0-100)
        label: Label text
        color: Ring color
    """
    html = f"""
    <div style="text-align: center;">
        <svg width="120" height="120" style="transform: rotate(-90deg);">
            <circle cx="60" cy="60" r="54" fill="none" stroke="#334155" stroke-width="8" />
            <circle 
                cx="60" cy="60" r="54" 
                fill="none" 
                stroke="{color}" 
                stroke-width="8"
                stroke-dasharray="{percent * 3.4:.1f} 340"
                stroke-linecap="round"
            />
        </svg>
        <p style="margin: -3rem 0 0 0; color: #00d9ff; font-size: 1.5rem; font-weight: 600;">
            {percent:.0f}%
        </p>
        <p style="margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 0.875rem;">
            {label}
        </p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def action_button(
    label: str,
    on_click,
    icon: str = "➕",
    variant: str = "primary"
):
    """
    Styled action button.
    
    Args:
        label: Button label
        on_click: Callback function
        icon: Button icon
        variant: "primary" or "secondary"
    """
    colors = {
        "primary": ("#00d9ff", "#0f172a"),
        "secondary": ("#334155", "#f1f5f9"),
    }
    bg_color, text_color = colors.get(variant, colors["primary"])

    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"<p style='font-size: 1.5rem;'>{icon}</p>", unsafe_allow_html=True)
    with col2:
        if st.button(label, key=label):
            on_click()

def section_header(title: str, subtitle: Optional[str] = None):
    """
    Section header with optional subtitle.
    
    Args:
        title: Section title
        subtitle: Optional subtitle
    """
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<p style='color: #94a3b8; margin: -1rem 0 1rem 0;'>{subtitle}</p>", unsafe_allow_html=True)

def info_tooltip(text: str, tooltip: str):
    """
    Text with inline tooltip.
    
    Args:
        text: Main text
        tooltip: Tooltip text on hover
    """
    html = f"""
    <span title="{tooltip}" style="border-bottom: 1px dotted #00d9ff; cursor: help;">
        {text}
    </span>
    """
    st.markdown(html, unsafe_allow_html=True)

def card_container(content_func, title: Optional[str] = None):
    """
    Card container with consistent styling.
    
    Args:
        content_func: Function that renders content
        title: Optional card title
    """
    with st.container():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
            border: 1px solid #334155;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        ">
        """, unsafe_allow_html=True)

        if title:
            st.markdown(f"#### {title}")

        content_func()

        st.markdown("</div>", unsafe_allow_html=True)
