import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# --- 1. DESIGN & BRANDING ---
st.set_page_config(page_title="Xyla Clipper Portal", page_icon="✂️", layout="wide")

# CSS Injection for Background Watermark and Glassmorphism
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;400&family=Outfit:wght@200;700&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    /* Injected exact SVG path from your HTML for the background watermark */
    .stApp::before {
        content: '';
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 80vw;
        height: 80vh;
        background-image: url("data:image/svg+xml;utf8,<svg viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'><path d='M30 20 L50 50 L70 20' stroke='white' stroke-width='2' fill='none' /><path d='M30 80 L50 50 L70 80' stroke='white' stroke-width='2' fill='none' /><path d='M20 25 L30 20' stroke='white' stroke-width='2' fill='none' /><path d='M80 25 L70 20' stroke='white' stroke-width='2' fill='none' /><path d='M20 75 L30 80' stroke='white' stroke-width='2' fill='none' /><path d='M80 75 L70 80' stroke='white' stroke-width='2' fill='none' /><circle cx='20' cy='25' r='3' fill='none' stroke='white' stroke-width='2'/><circle cx='80' cy='25' r='3' fill='none' stroke='white' stroke-width='2'/><circle cx='20' cy='75' r='3' fill='none' stroke='white' stroke-width='2'/><circle cx='80' cy='75' r='3' fill='none' stroke='white' stroke-width='2'/><circle cx='50' cy='50' r='2' fill='white' stroke='none'/></svg>");
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.03;
        z-index: -1;
    }

    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 40px !important;
    }

    button[kind="primaryFormSubmit"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 100px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        border: none !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    button[kind="primaryFormSubmit"]:hover {
        transform: scale(1.02) translateY(-2px);
        box-shadow: 0 10px 25px rgba(255,255,255,0.25);
    }

    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        background: linear-gradient(180deg, #fff 0%, #888 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Top Left Nav Logo Injection ---
st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 1.4rem; letter-spacing: 1px; font-family: 'Outfit', sans-serif; margin-bottom: 2rem;">
        <svg style="width: 30px; height: 30px; stroke: white; stroke-width: 2; fill: none; stroke-linecap: round; stroke-linejoin: round;" viewBox="0 0 100 100">
            <path d="M30 20 L50 50 L70 20 M30 80 L50 50 L70 80" />
            <circle cx="30" cy="20" r="5" fill="white" stroke="none"/>
            <circle cx="70" cy="20" r="5" fill="white" stroke="none"/>
            <circle cx="30" cy="80" r="5" fill="white" stroke="none"/>
            <circle cx="70" cy="80" r="5" fill="white" stroke="none"/>
        </svg>
        XYLA.
    </div>
""", unsafe_allow_html=True)

# --- 2. CONNECT TO SUPABASE ---
URL = "https://hnqpmftzwttcbvwgswmp.supabase.co"
KEY = st.secrets["SUPABASE_KEY"] 
supabase: Client = create_client(URL, KEY)

# --- 3. THE PORTAL CONTENT ---
st.title("CLIPPER PORTAL")
st.write("THE ALGORITHM IS HUMAN.")

# Define Campaign Statuses
active_campaigns = ["SILENT COLLISION", "Wendy Ortiz", "TEST.."]
ended_campaigns = ["Spartans", "BLOCK DAG", "LARK DEVIS"]

# Create the full list with visual markers
display_options = active_campaigns + [f"{c} (ENDED)" for c in ended_campaigns]

with st.form("clipper_form", clear_on_submit=True):
    selected_display = st.selectbox("SELECT CAMPAIGN", display_options)
    
    clipper_discord = st.text_input("YOUR DISCORD USERNAME (e.g. user#1234)")
    video_url = st.text_input("VIDEO URL (TIKTOK/IG)")
    
    submitted = st.form_submit_button("SUBMIT VIDEO TO ENGINE")

# --- 4. LOGIC WITH ENDED CAMPAIGN CHECK ---
if submitted:
    # Check if the selected option contains the "ENDED" tag
    if "(ENDED)" in selected_display:
        st.error(f"⚠️ Submission Failed: {selected_display} is no longer accepting new clips.")
    elif not video_url or not clipper_discord:
        st.error("ALL FIELDS REQUIRED.")
    else:
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = {
                "created_at": now, 
                "campaign_name": selected_display,
                "clipper_discord": clipper_discord, 
                "video_url": video_url,
                "views": 0, 
                "likes": 0, 
                "status": "Pending"
            }
            # Inserts the new clip into your Supabase tracking table
            supabase.table("clips_track").insert(new_entry).execute()
            st.success(f"LOGGED AT {now}. SCALE THE CULTURE.")
        except Exception as e:
            st.error(f"DATABASE ERROR: {e}")