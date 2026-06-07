import streamlit as st
from config import FOOTER_CREATOR

def inject_custom_css():
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {{
        font-family: 'Outfit', sans-serif;
    }}
    
    /* Custom KPI Cards */
    .kpi-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 25px;
    }}
    
    .kpi-card {{
        background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-left: 5px solid #4F46E5;
        flex: 1 1 200px;
        min-width: 180px;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }}
    
    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }}
    
    .kpi-card.pending {{
        border-left-color: #F59E0B;
    }}
    
    .kpi-card.completed {{
        border-left-color: #10B981;
    }}
    
    .kpi-card.overdue {{
        border-left-color: #EF4444;
    }}
    
    .kpi-card.total {{
        border-left-color: #3B82F6;
    }}
    
    .kpi-title {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B7280;
        font-weight: 600;
        margin-bottom: 5px;
    }}
    
    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.2;
    }}
    
    .kpi-desc {{
        font-size: 0.75rem;
        color: #9CA3AF;
        margin-top: 5px;
    }}

    /* Edited Tag */
    .edited-badge {{
        background-color: #D1FAE5;
        color: #065F46;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
        margin-left: 8px;
        display: inline-block;
        border: 1px solid #A7F3D0;
    }}
    
    /* Card headers for dashboard sections */
    .section-header {{
        font-size: 1.25rem;
        font-weight: 600;
        color: #1E293B;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 8px;
        margin-top: 25px;
        margin-bottom: 15px;
    }}
    
    /* Footer styles */
    .footer-container {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        text-align: center;
        padding: 10px 0;
        font-size: 0.8rem;
        color: #94A3B8;
        border-top: 1px solid #E2E8F0;
        z-index: 100;
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.8);
    }}
    
    /* Dark mode support adjustments */
    @media (prefers-color-scheme: dark) {{
        .kpi-card {{
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-left: 5px solid #6366F1;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }}
        .kpi-value {{
            color: #F8FAFC;
        }}
        .kpi-title {{
            color: #94A3B8;
        }}
        .section-header {{
            color: #F1F5F9;
            border-bottom: 2px solid #334155;
        }}
        .footer-container {{
            background: rgba(15, 23, 42, 0.8);
            border-top: 1px solid #334155;
            color: #64748B;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def draw_footer():
    footer_html = f"""
    <div class="footer-container">
        {FOOTER_CREATOR} | TaskTracker Pro &copy; 2026
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
