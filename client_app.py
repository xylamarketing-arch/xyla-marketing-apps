import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- 1. DESIGN & BRANDING ---
st.set_page_config(page_title="Xyla Client Dashboard", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;400&family=Outfit:wght@200;700&display=swap');
    
    .stApp { background-color: #000000; color: #ffffff; font-family: 'Inter', sans-serif; }

    /* The SVG Watermark */
    .stApp::before {
        content: ''; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 80vw; height: 80vh; opacity: 0.03; z-index: -1; pointer-events: none;
        background-image: url("data:image/svg+xml;utf8,<svg viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'><path d='M30 20 L50 50 L70 20' stroke='white' stroke-width='2' fill='none' /><path d='M30 80 L50 50 L70 80' stroke='white' stroke-width='2' fill='none' /><path d='M20 25 L30 20' stroke='white' stroke-width='2' fill='none' /><path d='M80 25 L70 20' stroke='white' stroke-width='2' fill='none' /><path d='M20 75 L30 80' stroke='white' stroke-width='2' fill='none' /><path d='M80 75 L70 80' stroke='white' stroke-width='2' fill='none' /><circle cx='20' cy='25' r='3' fill='none' stroke='white' stroke-width='2'/><circle cx='80' cy='25' r='3' fill='none' stroke='white' stroke-width='2'/><circle cx='20' cy='75' r='3' fill='none' stroke='white' stroke-width='2'/><circle cx='80' cy='75' r='3' fill='none' stroke='white' stroke-width='2'/><circle cx='50' cy='50' r='2' fill='white' stroke='none'/></svg>");
        background-repeat: no-repeat; background-position: center;
    }

    /* The Huge "XYLA" Text Watermark */
    .stApp::after {
        content: 'XYLA';
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        font-family: 'Outfit', sans-serif; font-size: 25vw; font-weight: 700;
        color: rgba(255, 255, 255, 0.02); z-index: -2; pointer-events: none;
    }

    /* Glass Cards */
    div[data-testid="stMetric"], .report-card, .hero-stat-card {
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px;
        padding: 30px !important; margin-bottom: 20px;
        text-align: center;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover, .report-card:hover, .hero-stat-card:hover {
        border-color: rgba(255, 255, 255, 0.2); transform: translateY(-3px);
    }

    h1, h2, h3, .hero-val {
        font-family: 'Outfit', sans-serif !important;
        background: linear-gradient(180deg, #fff 0%, #888 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    .hero-val { font-size: 3.5rem; font-weight: 700; display: block; }
    .hero-lab { font-size: 0.8rem; letter-spacing: 2px; color: #888; text-transform: uppercase; }
    
    /* White Rounded Button */
    .stButton > button {
        background-color: #ffffff !important; color: #000000 !important;
        border-radius: 100px !important; font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important; padding: 0.5rem 2.5rem !important;
        text-transform: uppercase; border: none !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    .stButton > button:hover {
        transform: scale(1.02) translateY(-2px);
        box-shadow: 0 10px 25px rgba(255,255,255,0.25);
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

# --- 2. AUTHENTICATION & LANDING LOGIC ---
PRIVATE_KEY = "xyla2026"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False

# --- LANDING PAGE (Unauthenticated) ---
if not st.session_state["authenticated"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("GLOBAL REACH")
    st.write("THE ALGORITHM IS HUMAN. SCALE WITHOUT LIMITS.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Hero Stat Row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="hero-stat-card"><span class="hero-val">9</span><span class="hero-lab">Total Campaigns</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="hero-stat-card"><span class="hero-val">457M</span><span class="hero-lab">Total Views</span></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="hero-stat-card"><span class="hero-val">1024</span><span class="hero-lab">Total Clippers</span></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Toggle Login Form
    if not st.session_state["show_login"]:
        if st.button("ACCESS YOUR CAMPAIGN"):
            st.session_state["show_login"] = True
            st.rerun()
    else:
        st.markdown('<div class="report-card">', unsafe_allow_html=True)
        st.subheader("🔐 PRIVATE ACCESS")
        user_key = st.text_input("ENTER PRIVATE ACCESS KEY", type="password")
        if st.button("UNLOCK DATA"):
            if user_key == PRIVATE_KEY:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("INVALID KEY. CONTACT YOUR ACCOUNT MANAGER.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.stop() 

# --- 3. DATABASE CONNECTION (Authenticated Only) ---
URL = "https://hnqpmftzwttcbvwgswmp.supabase.co"
KEY = st.secrets["SUPABASE_KEY"] 
supabase: Client = create_client(URL, KEY)

# --- 4. PROTECTED DASHBOARD CONTENT ---
st.title("CAMPAIGN INSIGHTS")
st.write("THE ALGORITHM IS HUMAN.")

res = supabase.table("clips_track").select("*").execute()

if res.data:
    df = pd.DataFrame(res.data)
    
    # Selection Filter
    brands = df['campaign_name'].unique().tolist()
    selected_brand = st.selectbox("CHOOSE YOUR CAMPAIGN", brands)
    
    brand_df = df[df['campaign_name'] == selected_brand]
    
    # CAMPAIGN FEEDBACK & STATS
    st.markdown(f"### 📋 {selected_brand} CAMPAIGN SUMMARY")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("TOTAL VIEWS", f"{brand_df['views'].sum():,}")
    with col2:
        st.metric("TOTAL CLIPS", len(brand_df))
    with col3:
        status = "✅ ACTIVE" if "(ENDED)" not in selected_brand else "🔴 COMPLETED"
        st.metric("CAMPAIGN STATUS", status)

    # FEEDBACK SECTION
    with st.container():
        st.markdown('<div class="report-card">', unsafe_allow_html=True)
        st.subheader("📢 Agency Feedback")
        if "Spartans" in selected_brand:
            st.write("Current focus: Pushing high-energy stream highlights to maximize retention.")
        elif "SILENT COLLISION" in selected_brand:
            st.write("Current focus: Aesthetic-heavy edits to build brand mystery and cult following.")
        else:
            st.write("The algorithm is performing within expected parameters. Scaling in progress.")
        st.markdown('</div>', unsafe_allow_html=True)

    # PERFORMANCE CHART
    st.subheader("CLIPPER LEADERBOARD")
    leaderboard = brand_df.groupby('clipper_discord')['views'].sum().sort_values(ascending=False)
    st.bar_chart(leaderboard, color="#ffffff")

    # LIVE FEED
    st.subheader("LIVE CONTENT FEED")
    st.dataframe(brand_df[['video_url', 'clipper_discord', 'views', 'likes', 'status']], use_container_width=True, hide_index=True)

else:
    st.info("Awaiting initial data stream...")

if st.sidebar.button("LOGOUT"):
    st.session_state["authenticated"] = False
    st.session_state["show_login"] = False
    st.rerun()