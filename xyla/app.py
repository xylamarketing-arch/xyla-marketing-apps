import streamlit as st
import subprocess
import sys
from supabase import create_client, Client
from datetime import datetime, date
import requests
import pandas as pd
import uuid
import re
import json
import os
import time
from urllib.parse import urlencode

# ────────────────────────────────────────────
# 1. PAGE CONFIG
# ────────────────────────────────────────────
st.set_page_config(page_title="Xyla Clipper Portal", page_icon="✂️", layout="wide")

# ────────────────────────────────────────────
# 2. DISCORD OAUTH CONFIG
# ────────────────────────────────────────────
DISCORD_CLIENT_ID = st.secrets["DISCORD_CLIENT_ID"]
DISCORD_CLIENT_SECRET = st.secrets["DISCORD_CLIENT_SECRET"]
DISCORD_REDIRECT_URI = st.secrets["DISCORD_REDIRECT_URI"]
DISCORD_API_BASE = "https://discord.com/api/v10"

DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize?" + urlencode({
    "client_id": DISCORD_CLIENT_ID,
    "redirect_uri": DISCORD_REDIRECT_URI,
    "response_type": "code",
    "scope": "identify",
})

# ────────────────────────────────────────────
# 3. ADMIN CONFIG
# ────────────────────────────────────────────
ADMIN_DISCORD_USERNAME = "floydiann_"

# ────────────────────────────────────────────
# 4. THEME CSS
# ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

.stApp { background-color: #000000; color: #ffffff; font-family: 'Inter', sans-serif; }

.stApp::before {
    content: ''; position: fixed; top: 50%; left: 50%;
    transform: translate(-50%, -50%); width: 80vw; height: 80vh;
    background-image: url("data:image/svg+xml;utf8,<svg viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'><path d='M30 20 L50 50 L70 20' stroke='white' stroke-width='2' fill='none'/><path d='M30 80 L50 50 L70 80' stroke='white' stroke-width='2' fill='none'/><circle cx='50' cy='50' r='2' fill='white' stroke='none'/></svg>");
    background-repeat: no-repeat; background-position: center;
    opacity: 0.03; z-index: -1; pointer-events: none;
}

.stApp::after {
    content: ''; position: fixed; top: 50%; left: 50%;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(138, 43, 226, 0.2) 0%, rgba(138, 43, 226, 0) 70%);
    filter: blur(80px); transform: translate(-50%, -50%);
    z-index: -2; pointer-events: none;
    animation: pulseGlow 8s infinite alternate;
}

@keyframes pulseGlow {
    0% { transform: translate(-50%, -50%) scale(1); opacity: 0.7; }
    50% { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(1); opacity: 0.7; }
}

h1, h2, h3 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: linear-gradient(180deg, #fff 0%, #888 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}
.stMarkdown p, .stMarkdown li { color: #9ca3af; font-weight: 300; }

.stButton > button, button[kind="primaryFormSubmit"] {
    background-color: #ffffff !important; color: #000000 !important;
    border-radius: 100px !important; font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important; text-transform: uppercase; letter-spacing: 1px;
    border: none !important; padding: 0.55rem 1.8rem !important;
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important; min-height: 42px !important;
}
.stButton > button:hover, button[kind="primaryFormSubmit"]:hover {
    transform: scale(1.02) translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(255,255,255,0.25) !important;
}
.stButton > button:disabled { background-color: rgba(255,255,255,0.08) !important; color: #555 !important; cursor: not-allowed !important; transform: none !important; box-shadow: none !important; }

div[data-testid="stForm"] {
    background: rgba(255,255,255,0.03) !important; backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 20px !important; padding: 30px !important;
}
section[data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid rgba(255,255,255,0.05) !important; }

div[data-testid="stImage"] {
    border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); transition: all 0.4s ease;
}
div[data-testid="stImage"]:hover { border-color: rgba(138,43,226,0.4); transform: translateY(-5px); box-shadow: 0 15px 35px rgba(138,43,226,0.25); }

div[role="radiogroup"] { gap: 6px !important; }
div[role="radiogroup"] label {
    background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 50px !important; padding: 6px 18px !important; font-size: 0.82rem !important; font-weight: 500 !important;
    color: #888 !important; transition: all 0.2s ease !important; white-space: nowrap !important;
}
div[role="radiogroup"] label p, div[role="radiogroup"] label span, div[role="radiogroup"] label div {
    color: #888 !important;
}
div[role="radiogroup"] label:hover { border-color: rgba(138,43,226,0.3) !important; color: #fff !important; background: rgba(138,43,226,0.1) !important; }
div[role="radiogroup"] label:hover p, div[role="radiogroup"] label:hover span { color: #fff !important; }

/* Selected radio — purple glow on white background */
div[role="radiogroup"] label[data-checked="true"],
div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"],
div[role="radiogroup"] label:has(input:checked) {
    background: #c48df5 !important; color: #000000 !important; border-color: #c48df5 !important; font-weight: 700 !important;
}
div[role="radiogroup"] label[data-checked="true"] *,
div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] *,
div[role="radiogroup"] label:has(input:checked) * {
    color: #000000 !important;
}

/* Sidebar radio overrides */
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: #ffffff !important; color: #000000 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] *,
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {
    color: #000000 !important;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px !important;
    text-align: center; transition: all 0.3s ease;
}
div[data-testid="stMetric"]:hover { border-color: rgba(138,43,226,0.3); transform: translateY(-2px); box-shadow: 0 10px 25px rgba(138,43,226,0.15); }
div[data-testid="stMetric"] label { font-size: 0.7rem !important; letter-spacing: 1.5px; text-transform: uppercase; color: #666 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 2rem !important; font-weight: 700 !important;
    background: linear-gradient(180deg, #fff, #888); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important; margin-top: 0.5rem;
}

.hero-glass {
    background: rgba(255,255,255,0.03); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 24px;
    padding: 3rem 2.5rem; text-align: center; max-width: 480px; margin: 0 auto; transition: all 0.4s ease;
}
.hero-glass:hover { border-color: rgba(138,43,226,0.3); transform: translateY(-3px); box-shadow: 0 15px 35px rgba(138,43,226,0.15); }
.discord-btn {
    display: inline-flex; align-items: center; gap: 12px; padding: 14px 36px; border-radius: 100px;
    background: #5865F2; color: #fff; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px; text-decoration: none; transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.discord-btn:hover { transform: scale(1.05) translateY(-3px); box-shadow: 0 15px 35px rgba(88,101,242,0.4); background: #4752C4; color: #fff; }
.discord-btn svg { width: 22px; height: 22px; fill: white; }

.tag-active { display: inline-block; padding: 3px 10px; border-radius: 50px; background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); font-size: 0.72rem; font-weight: 600; }
.tag-ended { display: inline-block; padding: 3px 10px; border-radius: 50px; background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); font-size: 0.72rem; font-weight: 600; }
.tag-new { display: inline-block; padding: 3px 10px; border-radius: 50px; background: rgba(234,179,8,0.15); color: #eab308; border: 1px solid rgba(234,179,8,0.25); font-size: 0.72rem; font-weight: 600; }
.tag-cat { display: inline-block; padding: 3px 8px; border-radius: 6px; background: rgba(255,255,255,0.06); color: #888; border: 1px solid rgba(255,255,255,0.05); font-size: 0.7rem; font-weight: 500; margin-right: 4px; margin-bottom: 4px; }
.payout-pill { display: inline-block; padding: 4px 12px; border-radius: 50px; background: rgba(255,255,255,0.06); color: #aaa; font-size: 0.75rem; font-weight: 500; margin: 6px 0 8px 0; }

.user-card { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; margin-bottom: 1rem; }
.user-card img { width: 40px; height: 40px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.15); }
.user-card .uname { font-weight: 600; font-size: 0.95rem; color: #fff; display: block; }
.user-card .utag { font-size: 0.75rem; color: #888; display: block; }

.clipper-badge { background: rgba(88,101,242,0.1); border: 1px solid rgba(88,101,242,0.25); border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem; }
.clipper-badge img { width: 24px; height: 24px; border-radius: 50%; }
.clipper-badge span { color: #8b9cf7; font-size: 0.85rem; }
.clipper-badge strong { color: #fff; }

.account-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.2rem 1.5rem; display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem; transition: all 0.3s ease; }
.account-card:hover { border-color: rgba(255,255,255,0.15); }
.account-left { display: flex; align-items: center; gap: 12px; }
.account-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.account-icon.tiktok { background: rgba(0,0,0,0.3); border: 1px solid #333; }
.account-icon.instagram { background: rgba(225,48,108,0.15); border: 1px solid rgba(225,48,108,0.3); }
.account-icon.youtube { background: rgba(255,0,0,0.1); border: 1px solid rgba(255,0,0,0.2); }
.account-name { font-weight: 500; color: #fff; font-size: 0.9rem; display: block; }
.account-platform { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; display: block; }
.account-status { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px; padding: 2px 8px; border-radius: 50px; display: inline-block; margin-top: 2px; }
.account-status.verified { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }
.account-status.pending { background: rgba(234,179,8,0.15); color: #eab308; border: 1px solid rgba(234,179,8,0.25); }

.verify-code-box { background: rgba(88,101,242,0.08); border: 1px dashed rgba(88,101,242,0.3); border-radius: 16px; padding: 1.5rem; text-align: center; margin: 1rem 0; }
.stat-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; color: #888; font-weight: 600; margin-bottom: 0.5rem; }
.stat-val { font-size: 1.8rem; font-weight: 700; color: #fff; line-height: 1.2; font-family: 'Plus Jakarta Sans', sans-serif; }

.verify-code { font-family: 'Plus Jakarta Sans', monospace; font-size: 2rem; font-weight: 700; color: #c48df5; letter-spacing: 4px; margin: 0.5rem 0; display: block; }
.verify-step { display: flex; align-items: flex-start; gap: 10px; padding: 10px 0; text-align: left; }
.verify-step-num { width: 24px; height: 24px; border-radius: 50%; background: rgba(255,255,255,0.08); color: #aaa; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; }

.details-link { display: inline-flex; align-items: center; gap: 6px; padding: 5px 14px; border-radius: 50px; background: rgba(88,101,242,0.1); border: 1px solid rgba(88,101,242,0.25); color: #8b9cf7; font-size: 0.75rem; font-weight: 600; text-decoration: none; letter-spacing: 0.5px; transition: all 0.3s ease; margin-bottom: 6px; }
.details-link:hover { background: rgba(88,101,242,0.2); border-color: rgba(88,101,242,0.4); color: #a5b4fc; }

.verify-notice { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); border-radius: 12px; padding: 12px 16px; color: #f87171; font-size: 0.82rem; text-align: center; margin-top: 6px; }

.success-toast { background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); border-radius: 16px; padding: 1.5rem; text-align: center; margin: 1rem 0; }
.success-toast .check { font-size: 2.5rem; margin-bottom: 0.5rem; display: block; }
.success-toast .msg { color: #22c55e; font-size: 1rem; font-weight: 600; display: block; }
.success-toast .sub { color: #888; font-size: 0.82rem; display: block; margin-top: 4px; }

.budget-bar-outer { background: rgba(255,255,255,0.06); border-radius: 50px; height: 8px; margin: 6px 0; overflow: hidden; }
.budget-bar-inner { height: 100%; border-radius: 50px; background: linear-gradient(90deg, #22c55e, #eab308, #ef4444); transition: width 0.5s ease; }
.budget-text { font-size: 0.72rem; color: #888; margin-top: 2px; }

.admin-badge { display: inline-block; padding: 2px 10px; border-radius: 50px; background: rgba(168,85,247,0.15); color: #a855f7; border: 1px solid rgba(168,85,247,0.25); font-size: 0.7rem; font-weight: 600; }

div[data-testid="stStatusWidget"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────
# 5. XYLA LOGO
# ────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;font-weight:700;font-size:1.4rem;letter-spacing:1px;font-family:'Plus Jakarta Sans',sans-serif;margin-bottom:1.5rem;">
    <svg style="width:30px;height:30px;stroke:white;stroke-width:2;fill:none;stroke-linecap:round;stroke-linejoin:round;" viewBox="0 0 100 100">
        <path d="M30 20 L50 50 L70 20 M30 80 L50 50 L70 80"/>
        <circle cx="30" cy="20" r="5" fill="white" stroke="none"/>
        <circle cx="70" cy="20" r="5" fill="white" stroke="none"/>
        <circle cx="30" cy="80" r="5" fill="white" stroke="none"/>
        <circle cx="70" cy="80" r="5" fill="white" stroke="none"/>
    </svg>
    XYLA.
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────
# 6. DISCORD HELPERS
# ────────────────────────────────────────────
def exchange_code_for_token(code: str) -> dict:
    r = requests.post(f"{DISCORD_API_BASE}/oauth2/token",
                      data={"client_id": DISCORD_CLIENT_ID, "client_secret": DISCORD_CLIENT_SECRET,
                            "grant_type": "authorization_code", "code": code, "redirect_uri": DISCORD_REDIRECT_URI},
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
    r.raise_for_status()
    return r.json()

def get_discord_user(access_token: str) -> dict:
    r = requests.get(f"{DISCORD_API_BASE}/users/@me", headers={"Authorization": f"Bearer {access_token}"})
    r.raise_for_status()
    return r.json()

def get_avatar_url(user: dict) -> str:
    if user.get("avatar"):
        return f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=128"
    return f"https://cdn.discordapp.com/embed/avatars/{(int(user['id']) >> 22) % 6}.png"


# ────────────────────────────────────────────
# 7. SESSION STATE
# ────────────────────────────────────────────
defaults = {
    "authenticated": False,
    "discord_user": None,
    "submit_campaign": None,
    "submission_success": None,
    "accounts_loaded": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val
if "accounts" not in st.session_state:
    st.session_state["accounts"] = []


# ────────────────────────────────────────────
# 8. OAUTH CALLBACK
# ────────────────────────────────────────────
code = st.query_params.get("code")
if code and not st.session_state["authenticated"]:
    try:
        token_data = exchange_code_for_token(code)
        user = get_discord_user(token_data["access_token"])
        st.session_state["authenticated"] = True
        st.session_state["discord_user"] = user
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.query_params.clear()
        st.error(f"Discord authentication failed: {e}. Please try logging in again.")
        import time; time.sleep(2)
        st.rerun()


# ────────────────────────────────────────────
# 9. LOGIN GATE
# ────────────────────────────────────────────
if not st.session_state["authenticated"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _c1, _c2, _c3 = st.columns([1, 2, 1])
    with _c2:
        discord_svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189z"/></svg>'
        st.markdown(f"""
        <div class="hero-glass">
            <svg style="width:50px;height:50px;stroke:white;stroke-width:2;fill:none;stroke-linecap:round;stroke-linejoin:round;margin-bottom:1.5rem;" viewBox="0 0 100 100">
                <path d="M30 20 L50 50 L70 20 M30 80 L50 50 L70 80"/>
                <circle cx="30" cy="20" r="5" fill="white" stroke="none"/>
                <circle cx="70" cy="20" r="5" fill="white" stroke="none"/>
                <circle cx="30" cy="80" r="5" fill="white" stroke="none"/>
                <circle cx="70" cy="80" r="5" fill="white" stroke="none"/>
            </svg>
            <h2 style="font-size:1.8rem;margin-bottom:0.5rem;">CLIPPER PORTAL</h2>
            <p style="color:#666;font-size:0.9rem;margin-bottom:2rem;text-transform:uppercase;letter-spacing:2px;">The Algorithm is Human</p>
            <a href="{DISCORD_AUTH_URL}" class="discord-btn">{discord_svg} Login with Discord</a>
        </div>
        """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════
#   AUTHENTICATED
# ══════════════════════════════════════════════
discord_user = st.session_state["discord_user"]
discord_username = discord_user.get("username", "Unknown")
discord_display = discord_user.get("global_name") or discord_username
avatar_url = get_avatar_url(discord_user)

is_admin = (discord_username == ADMIN_DISCORD_USERNAME)

has_verified_account = any(
    a.get("status") == "verified" for a in st.session_state["accounts"]
)

# ── SUPABASE ──
SUPABASE_URL = "https://hnqpmftzwttcbvwgswmp.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ══════════════════════════════════════════════
#   LOAD CAMPAIGNS FROM DATABASE
# ══════════════════════════════════════════════
@st.cache_data(ttl=15)
def load_campaigns():
    """Load all campaigns from the campaigns table."""
    try:
        res = supabase.table("campaigns").select("*").order("created_at", desc=False).execute()
        return res.data or []
    except Exception:
        return []

CAMPAIGNS = load_campaigns()
RATE_LOOKUP = {c.get("name", ""): float(c.get("cpm_rate", 0)) for c in CAMPAIGNS}


# ══════════════════════════════════════════════
#   HELPERS: PERSISTENT ACCOUNT STORAGE
# ══════════════════════════════════════════════
# Table: clipper_accounts — id (uuid), user_id, platform, account_handle, is_verified, created_at

def load_accounts_from_db(discord_id: str) -> list:
    try:
        res = supabase.table("clipper_accounts").select("*").eq("user_id", discord_id).execute()
        accounts = []
        for row in res.data:
            is_verified = row.get("is_verified", False)
            accounts.append({
                "id": row.get("id"), "platform": row.get("platform", ""),
                "username": row.get("account_handle", ""),
                "status": "verified" if is_verified else "pending", "code": "",
            })
        return accounts
    except Exception as e:
        st.toast(f"⚠️ Failed to load accounts: {e}", icon="⚠️")
        return []

def save_account_to_db(discord_id, platform, username):
    try:
        res = supabase.table("clipper_accounts").insert({
            "user_id": discord_id, "platform": platform,
            "account_handle": username, "is_verified": False,
        }).execute()
        if res.data:
            row = res.data[0]
            return {"id": row.get("id"), "platform": row.get("platform"),
                    "username": row.get("account_handle"), "status": "pending", "code": ""}
    except Exception as e:
        st.toast(f"⚠️ DB insert failed: {e}", icon="⚠️")
    return None

def update_account_verified_in_db(row_id, verified):
    try:
        supabase.table("clipper_accounts").update({"is_verified": verified}).eq("id", row_id).execute()
    except Exception as e:
        st.toast(f"⚠️ DB update failed: {e}", icon="⚠️")

def delete_account_from_db(row_id):
    try:
        supabase.table("clipper_accounts").delete().eq("id", row_id).execute()
    except Exception as e:
        st.toast(f"⚠️ DB delete failed: {e}", icon="⚠️")

def generate_verify_code():
    return f"XYLA-{uuid.uuid4().hex[:4].upper()}"

# Load accounts from DB
if st.session_state["authenticated"] and not st.session_state["accounts_loaded"]:
    du = st.session_state["discord_user"]
    if du:
        loaded = load_accounts_from_db(du.get("username", ""))
        for acc in loaded:
            if acc["status"] == "pending" and not acc.get("code"):
                acc["code"] = generate_verify_code()
        st.session_state["accounts"] = loaded
        st.session_state["accounts_loaded"] = True

has_verified_account = any(a.get("status") == "verified" for a in st.session_state["accounts"])


# ══════════════════════════════════════════════
#   HELPERS: ACCOUNT VERIFICATION (Apify)
# ══════════════════════════════════════════════
from apify_client import ApifyClient
APIFY_TOKEN = "apify_api_LVewkbYZ6Ebm1mSzck8XAPegmoG21E4zhBu4"
apify = ApifyClient(APIFY_TOKEN)

def check_bio_for_code(platform, username, code):
    try:
        if platform == "Instagram":
            run = apify.actor("apify/instagram-profile-scraper").call(run_input={"usernames": [username]}, timeout_secs=60)
            for item in apify.dataset(run["defaultDatasetId"]).iterate_items():
                bio = item.get("biography", "") or item.get("bio", "") or ""
                if code in bio: return True
        elif platform == "TikTok":
            run = apify.actor("clockworks/tiktok-profile-scraper").call(run_input={"profiles": [f"https://www.tiktok.com/@{username}"]}, timeout_secs=60)
            for item in apify.dataset(run["defaultDatasetId"]).iterate_items():
                bio = item.get("signature", "") or item.get("bio", "") or ""
                if code in bio: return True
        elif platform == "YouTube":
            resp = requests.get(f"https://www.youtube.com/@{username}", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if resp.status_code == 200 and code in resp.text: return True
        return False
    except Exception:
        return False


# ══════════════════════════════════════════════
#   HELPERS: URL VALIDATION
# ══════════════════════════════════════════════
URL_PATTERN = re.compile(r'^https?://(www\.)?(tiktok\.com|instagram\.com|youtube\.com|youtu\.be|vm\.tiktok\.com)/.+', re.IGNORECASE)
def is_valid_video_url(url): return bool(URL_PATTERN.match(url.strip()))


# ── SIDEBAR ──
with st.sidebar:
    st.markdown(f"""
    <div class="user-card">
        <img src="{avatar_url}" alt="avatar">
        <div><span class="uname">{discord_display}</span><span class="utag">@{discord_username}</span></div>
    </div>
    """, unsafe_allow_html=True)
    if is_admin:
        st.markdown('<span class="admin-badge">👑 ADMIN</span>', unsafe_allow_html=True)
    st.markdown("---")
    nav_options = ["Campaigns", "Dashboard", "Earnings", "Accounts"]
    if is_admin:
        nav_options.append("Admin")
    page = st.radio("NAV", nav_options, label_visibility="collapsed")
    st.markdown("---")
    st.markdown(
        """<a href="mailto:Xylamarketing@gmail.com?subject=Book%20a%20Campaign%20Call%20-%20Google%20Meet" target="_blank" style="display:block; text-align:center; padding:10px; background:rgba(138,43,226,0.15); color:#c48df5; border:1px solid rgba(138,43,226,0.3); border-radius:10px; text-decoration:none; font-weight:600; font-size:0.85rem; margin-bottom:1rem; transition:all 0.3s ease;">🚀 Launch a Campaign</a>""",
        unsafe_allow_html=True
    )
    if st.button("LOGOUT"):
        for k in ["discord_user", "supabase_user", "authenticated"]:
            st.session_state[k] = None
        st.session_state["authenticated"] = False
        st.rerun()


# ══════════════════════════════════════════════
#   PAGE: CAMPAIGNS
# ══════════════════════════════════════════════
if page == "Campaigns":
    st.title("Campaigns")
    st.write("Browse and join active campaigns")

    if st.session_state.get("submission_success"):
        msg = st.session_state["submission_success"]
        st.markdown(f'<div class="success-toast"><span class="check">✅</span><span class="msg">{msg}</span><span class="sub">Your clip has been logged and is pending review.</span></div>', unsafe_allow_html=True)
        st.session_state["submission_success"] = None

    # Stats
    active_count = sum(1 for c in CAMPAIGNS if c.get("is_active"))
    ended_count = sum(1 for c in CAMPAIGNS if not c.get("is_active"))
    m1, m2, m3 = st.columns(3)
    m1.metric("TOTAL CAMPAIGNS", len(CAMPAIGNS))
    m2.metric("ACTIVE", active_count)
    m3.metric("COMPLETED", ended_count)
    st.markdown("")

    # Filter tags
    all_tags_set = set()
    for c in CAMPAIGNS:
        for t in (c.get("tags") or []):
            all_tags_set.add(t)
    all_tags = ["All"] + sorted(all_tags_set)
    active_filter = st.radio("Filter", all_tags, horizontal=True, label_visibility="collapsed")
    st.markdown("")

    if active_filter == "All":
        filtered = CAMPAIGNS
    else:
        filtered = [c for c in CAMPAIGNS if active_filter in (c.get("tags") or [])]

    if not filtered:
        st.info("No campaigns match the selected filter.")
    else:
        cols_per_row = 3
        for row_start in range(0, len(filtered), cols_per_row):
            row_items = filtered[row_start:row_start + cols_per_row]
            cols = st.columns(cols_per_row)
            for i, camp in enumerate(row_items):
                with cols[i]:
                    # Campaign image
                    img_url = camp.get("image_url", "")
                    if img_url:
                        st.image(img_url, use_container_width=True)
                    else:
                        st.image("demo.jpg", use_container_width=True)

                    # Status badge
                    if camp.get("is_active"):
                        badge = '<span class="tag-active">● Active</span>'
                    else:
                        badge = '<span class="tag-ended">● Ended</span>'
                    if camp.get("is_new"):
                        badge += ' <span class="tag-new">✦ NEW</span>'
                    st.markdown(badge, unsafe_allow_html=True)

                    st.markdown(f"**{camp.get('name', '')}**")
                    st.caption(camp.get("description", ""))

                    # Payout pill
                    cpm = float(camp.get("cpm_rate", 0))
                    if cpm > 0:
                        st.markdown(f'<span class="payout-pill">${cpm:.0f} / 100K views</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="payout-pill">TBD</span>', unsafe_allow_html=True)

                    # Tags
                    tags = camp.get("tags") or []
                    if tags:
                        tags_html = "".join(f'<span class="tag-cat">{t}</span>' for t in tags)
                        st.markdown(tags_html, unsafe_allow_html=True)

                    # Budget usage bar
                    total_budget = float(camp.get("total_budget", 0))
                    pct = float(camp.get("pct_used", 0))
                    if total_budget > 0:
                        budget_used = float(camp.get("budget_used", 0))
                        remaining = max(total_budget - budget_used, 0)
                        st.markdown(f'''
                        <div class="budget-bar-outer"><div class="budget-bar-inner" style="width:{min(pct, 100)}%"></div></div>
                        <div class="budget-text">{pct:.1f}% used · ${remaining:,.0f} remaining</div>
                        ''', unsafe_allow_html=True)

                    # Details link
                    docs_url = camp.get("docs_url", "")
                    if docs_url:
                        st.markdown(f'<a href="{docs_url}" target="_blank" class="details-link">📄 Details</a>', unsafe_allow_html=True)

                    # Submit button
                    if camp.get("is_active"):
                        if has_verified_account:
                            if st.button("SUBMIT →", key=f"submit_{camp['name']}", use_container_width=True):
                                st.session_state["submit_campaign"] = camp["name"]
                                st.rerun()
                        else:
                            st.button("SUBMIT →", key=f"submit_{camp['name']}", use_container_width=True, disabled=True)
                            st.markdown('<div class="verify-notice">⚠️ Verify an account to submit</div>', unsafe_allow_html=True)

    # ── Inline Submit Form ──
    if st.session_state.get("submit_campaign"):
        sel_name = st.session_state["submit_campaign"]
        if not has_verified_account:
            st.error("❌ You need at least one verified account to submit clips.")
            st.session_state["submit_campaign"] = None
        else:
            st.markdown("---")
            st.subheader(f"Submit to: {sel_name}")
            sel_camp = next((c for c in CAMPAIGNS if c.get("name") == sel_name), None)

            st.markdown(f'<div class="clipper-badge"><img src="{avatar_url}"><span>CLIPPER: <strong>@{discord_username}</strong></span></div>', unsafe_allow_html=True)

            with st.expander("📌 Submission Guidelines & Rules (Read Before Submitting)"):
                st.markdown("""
                **To ensure your clip is approved and eligible for payouts:**
                - 1. **High Quality**: Video must be at least 720p resolution.
                - 2. **Watermarks**: No watermarks from other platforms (e.g., TikTok logo on an IG Reel).
                - 3. **Relevancy**: Content must be strictly relevant to the campaign.
                - 4. **Originality**: Do not re-upload exact clips submitted by others.
                
                *Clips failing these checks will be **Rejected** by Admins and will not generate earnings.*
                """)

            with st.form("clipper_form", clear_on_submit=True):
                video_url = st.text_input("VIDEO URL", placeholder="https://www.tiktok.com/@user/video/...")
                col_s, col_c = st.columns(2)
                with col_s:
                    submitted = st.form_submit_button("SUBMIT VIDEO", use_container_width=True)
                with col_c:
                    cancel = st.form_submit_button("CANCEL", use_container_width=True)

            if cancel:
                st.session_state["submit_campaign"] = None
                st.rerun()
            if submitted:
                if not video_url:
                    st.error("VIDEO URL IS REQUIRED.")
                elif not is_valid_video_url(video_url):
                    st.error("Invalid URL. Must be a TikTok, Instagram, or YouTube link.")
                else:
                    try:
                        # Clean the URL to check for duplicates (strip www, igsh, query params, trailing slashes)
                        clean_url = video_url.replace("www.", "").split("?")[0].rstrip("/")
                        
                        # Extract shortcode or path for matching to avoid /p/ vs /reel/ duplicate issues
                        try:
                            from urllib.parse import urlparse
                            path_parts = [p for p in urlparse(clean_url).path.split("/") if p]
                            shortcode = path_parts[-1] if path_parts else clean_url
                        except Exception:
                            shortcode = clean_url

                        # Query DB to check if this exact video was already submitted
                        existing = supabase.table("clips_track").select("id").ilike("video_url", f"%{shortcode}%").execute()
                        if existing.data:
                            st.error(f"Duplicate Error: This video has already been submitted to the platform.")
                        else:
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            insert_data = {
                                "created_at": now,
                                "client_name": sel_name,
                                "clipper_name": discord_username,
                                "video_url": video_url,
                                "views": 0, "likes": 0, "status": "Pending",
                            }
                            if sel_camp:
                                insert_data["campaign_id"] = sel_camp.get("id")
                            supabase.table("clips_track").insert(insert_data).execute()
                            st.session_state["submit_campaign"] = None
                            st.session_state["submission_success"] = f"Clip submitted to {sel_name} — Logged at {now}"
                            st.rerun()
                    except Exception as e:
                        st.error(f"DATABASE ERROR: {e}")


# ══════════════════════════════════════════════
#   PAGE: DASHBOARD
# ══════════════════════════════════════════════
elif page == "Dashboard":
    st.title("Dashboard")
    st.write(f"Your performance overview — @{discord_username}")

    try:
        res = supabase.table("clips_track").select("*").eq("clipper_name", discord_username).execute()
        clips = res.data
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        clips = []

    if not clips:
        st.info("No submissions yet. Go to Campaigns and submit your first clip!")
    else:
        # Resolve client_name from campaign_id for any clip missing it
        for c in clips:
            if not c.get("client_name"):
                camp_id = c.get("campaign_id")
                camp_matched = next((camp for camp in CAMPAIGNS if camp.get("id") == camp_id), None)
                c["client_name"] = camp_matched.get("name") if camp_matched else "Unknown"

        df = pd.DataFrame(clips)
        df["client_name"] = df["client_name"].fillna("Unknown")
        df["views"] = pd.to_numeric(df.get("views", 0), errors="coerce").fillna(0).astype(int)
        df["likes"] = pd.to_numeric(df.get("likes", 0), errors="coerce").fillna(0).astype(int)

        total_views = int(df["views"].sum())
        total_likes = int(df["likes"].sum())
        total_clips = len(df)
        total_earnings = 0.0
        for _, row in df.iterrows():
            rate = RATE_LOOKUP.get(row.get("client_name", ""), 0)
            if row.get("status", "Pending") == "Approved":
                total_earnings += (row.get("views", 0) / 1000) * rate

        # -- IN-APP NOTIFICATIONS --
        pending_clips_count = sum(1 for c in clips if c.get("status") == "Pending")
        rejected_clips_count = sum(1 for c in clips if c.get("status") == "Rejected")
        if pending_clips_count > 0:
            st.info(f"⏳ **Update:** You have **{pending_clips_count}** clips pending Admin review.")
        if rejected_clips_count > 0:
            st.warning(f"⚠️ **Alert:** You have **{rejected_clips_count}** rejected clips. Please review the submission guidelines.")

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("TOTAL VIEWS", f"{total_views:,}")
        s2.metric("TOTAL LIKES", f"{total_likes:,}")
        s3.metric("TOTAL CLIPS", total_clips)
        s4.metric("EST. EARNINGS", f"${total_earnings:,.2f}")
        st.markdown("---")

        # -- GAMIFICATION: TOP EARNERS LEADERBOARD --
        try:
            lb_res = supabase.table("clips_track").select("clipper_name", "client_name", "campaign_id", "views").eq("status", "Approved").execute()
            lb_clips = lb_res.data or []
            if lb_clips:
                lb_earnings = {}
                for lbc in lb_clips:
                    cname = lbc.get("client_name")
                    if not cname:
                        camp_id = lbc.get("campaign_id")
                        camp_matched = next((camp for camp in CAMPAIGNS if camp.get("id") == camp_id), None)
                        cname = camp_matched.get("name") if camp_matched else "Unknown"
                    
                    rate = RATE_LOOKUP.get(cname, 0)
                    earnings = (lbc.get("views", 0) / 1000) * rate
                    clipper = lbc.get("clipper_name")
                    lb_earnings[clipper] = lb_earnings.get(clipper, 0.0) + earnings
                
                if lb_earnings:
                    st.subheader("🏆 Top Earners Leaderboard")
                    lb_df = pd.DataFrame(list(lb_earnings.items()), columns=["Clipper", "Approved Earnings"])
                    lb_df = lb_df.sort_values(by="Approved Earnings", ascending=False).head(5)
                    lb_df.insert(0, "Rank", ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][:len(lb_df)])
                    lb_df["Approved Earnings"] = lb_df["Approved Earnings"].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(lb_df, use_container_width=True, hide_index=True)
                    st.markdown("---")
        except Exception as e:
            pass

        st.subheader("Campaign Breakdown")
        for cname in df["client_name"].unique().tolist():
            cdf = df[df["client_name"] == cname]
            c_views = int(cdf["views"].sum())
            c_likes = int(cdf["likes"].sum())
            c_clips = len(cdf)
            rate = RATE_LOOKUP.get(cname, 0)
            c_earnings = (c_views / 1000) * rate

            camp_data = next((c for c in CAMPAIGNS if c.get("name") == cname), None)
            status_badge = ""
            if camp_data:
                status_badge = '<span class="tag-active">● Active</span>' if camp_data.get("is_active") else '<span class="tag-ended">● Ended</span>'

            st.markdown(f"#### {cname}  {status_badge}", unsafe_allow_html=True)
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("Views", f"{c_views:,}")
            e2.metric("Likes", f"{c_likes:,}")
            e3.metric("Clips", c_clips)
            e4.metric("Earnings", f"${c_earnings:,.2f}")

            with st.expander("View submitted clips"):
                display_cols = [c for c in ["video_url", "views", "likes", "status", "created_at"] if c in cdf.columns]
                st.dataframe(cdf[display_cols], use_container_width=True, hide_index=True)
            st.markdown("")

        st.markdown("---")
        st.subheader("Views by Campaign")
        
        # Upgrade messy Streamlit chart to a premium interactive Plotly visualization
        chart_data = df.groupby("client_name")["views"].sum().reset_index()
        chart_data = chart_data.sort_values(by="views", ascending=True) # Ascending for horizontal bar charts
        
        if not chart_data.empty:
            import plotly.express as px
            # Create a sleek horizontal bar chart
            fig = px.bar(
                chart_data, 
                x="views", 
                y="client_name", 
                orientation="h",
                text="views",
                labels={"views": "Total Views", "client_name": "Campaign"},
                color_discrete_sequence=["#8A2BE2"] # Sleek purple brand color
            )
            
            # Premium dark mode aesthetic layout formatting
            fig.update_traces(
                texttemplate='%{text:,.0f}', 
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Views: %{x:,.0f}<extra></extra>',
                marker_line_width=0
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=40, t=20, b=0),
                height=max(250, 50 * len(chart_data) + 100),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", zeroline=False, visible=False),
                yaxis=dict(showgrid=False, title=None, tickfont=dict(color="#AEAAAA", size=14)),
                hoverlabel=dict(bgcolor="#1E1E1E", font_size=13, font_family="sans-serif")
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Not enough data to generate graph.")

# ══════════════════════════════════════════════
#   PAGE: EARNINGS
# ══════════════════════════════════════════════
elif page == "Earnings":
    st.title("Earnings & Payouts")
    st.write(f"Manage withdrawals and view your revenue history — @{discord_username}")

    try:
        res = supabase.table("clips_track").select("client_name", "campaign_id", "views", "status").eq("clipper_name", discord_username).execute()
        clips = res.data or []
        
        # Resolve 'client_name'
        for c in clips:
            if not c.get("client_name"):
                camp_id = c.get("campaign_id")
                camp_matched = next((camp for camp in CAMPAIGNS if camp.get("id") == camp_id), None)
                c["client_name"] = camp_matched.get("name") if camp_matched else "Unknown"

        lifetime_earnings = 0.0
        pending_clearances = 0.0
        campaign_breakdown = {}

        for c in clips:
            rate = RATE_LOOKUP.get(c.get("client_name", ""), 0)
            earnings = (c.get("views", 0) / 1000) * rate
            status = c.get("status", "Pending")
            c_name = c.get("client_name", "Unknown")
            
            if c_name not in campaign_breakdown:
                campaign_breakdown[c_name] = {"Approved": 0.0, "Pending": 0.0, "Rejected": 0.0}
            
            if status in campaign_breakdown[c_name]:
                campaign_breakdown[c_name][status] += earnings
            else:
                campaign_breakdown[c_name]["Pending"] += earnings  # Default catch-all
            
            if status == "Approved":
                lifetime_earnings += earnings
            elif status == "Pending":
                pending_clearances += earnings

        # Calculate current balance = lifetime earnings - total withdrawn (paid or pending withdrawal)
        w_res = supabase.table("withdrawals").select("amount", "status").eq("clipper_name", discord_username).execute()
        withdrawals = w_res.data or []
        total_withdrawn = sum(w.get("amount", 0) for w in withdrawals if w.get("status") in ["Pending", "Paid"])
        
        total_earnings = lifetime_earnings - total_withdrawn

    except Exception as e:
        total_earnings = 0.0
        lifetime_earnings = 0.0
        pending_clearances = 0.0
        campaign_breakdown = {}
        st.error(f"Error computing earnings: {e}")

    s1, s2, s3 = st.columns(3)
    s1.metric("LIFETIME EARNINGS", f"${lifetime_earnings:,.2f}")
    s2.metric("CURRENT BALANCE", f"${total_earnings:,.2f}")
    s3.metric("PENDING CLEARANCES", f"${pending_clearances:,.2f}")
    st.markdown("---")
    
    st.subheader("Campaign Breakdown")
    if campaign_breakdown:
        breakdown_data = []
        for camp, data in campaign_breakdown.items():
            breakdown_data.append({
                "Campaign": camp,
                "Approved": f"${data['Approved']:,.2f}",
                "Pending": f"${data['Pending']:,.2f}",
                "Rejected": f"${data['Rejected']:,.2f}"
            })
        st.dataframe(pd.DataFrame(breakdown_data), use_container_width=True, hide_index=True)
    else:
        st.info("No campaign data yet.")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Request Payout")
        if total_earnings >= 20.00:
            st.success(f"You are eligible to withdraw **${total_earnings:,.2f}**!")
            with st.form("withdrawal_form"):
                payment_method = st.selectbox("Select Payment Method", options=["USDT (BEP20)", "USDC", "PayPal (Coming Soon)"])
                wallet_address = st.text_input("Enter Wallet Address (or PayPal Email)")
                
                req_btn = st.form_submit_button("Submit Request")
                if req_btn:
                    if payment_method == "PayPal (Coming Soon)":
                        st.error("PayPal integration is currently unavailable. Please select Crypto.")
                    elif not wallet_address.strip():
                        st.error("You must enter a valid wallet address.")
                    else:
                        import requests
                        webhook_url = "https://discord.com/api/webhooks/1480061035703570554/4GWR8lIAl1oyK77jMTJ1EG2-I2dCXo9iGnnm4VblpRr7Bv1EI2pmB59K9kah6EpbC0gG"
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        try:
                            # 1. Save to Supabase DB Log
                            insert_data = {
                                "clipper_name": discord_username,
                                "amount": total_earnings,
                                "method": payment_method,
                                "wallet_address": wallet_address,
                                "status": "Pending",
                                "created_at": now
                            }
                            supabase.table("withdrawals").insert(insert_data).execute()
                            
                            # 2. Ping Discord Webhook
                            payload = {
                                "content": f"🚀 **NEW WITHDRAWAL REQUEST** from <@{discord_username}>\n"
                                           f"**Amount:** `${total_earnings:,.2f}`\n"
                                           f"**Method:** `{payment_method}`\n"
                                           f"**Wallet:** `{wallet_address}`\n"
                                           f"*(Mark this as paid via Supabase Database once processed)*"
                            }
                            requests.post(webhook_url, json=payload)
                            st.success("✅ Withdrawal request submitted securely. An admin has been notified.")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to submit withdrawal request. Please ensure you have created the `withdrawals` table in Supabase. Info: {e}")
        else:
            withdraw_progress = (total_earnings / 20.0) * 100
            # Escaping asterisks in Streamlit format
            st.warning(f"🔒 **Minimum withdrawal is $20.00** \— You need **\${(20.0 - total_earnings):,.2f}** more to unlock payouts.")
            st.progress(min(int(withdraw_progress), 100))

    with col2:
        st.subheader("Your Payout History")
        try:
            w_res = supabase.table("withdrawals").select("amount, method, status, created_at").eq("clipper_name", discord_username).order("created_at", desc=True).execute()
            if w_res.data:
                history_df = pd.DataFrame(w_res.data)
                
                # Format the table view cleanly for the dashboard
                history_df["Date"] = pd.to_datetime(history_df["created_at"]).dt.strftime('%m/%d/%Y')
                history_df["Amount"] = history_df["amount"].apply(lambda x: f"${x:,.2f}")
                history_df = history_df.rename(columns={"method": "Method", "status": "Status"})
                
                # Apply colorized statuses based on admin DB actions
                def colorize_status(status):
                    if status.lower() == 'paid': return 'color: #00FF00; font-weight: bold;'
                    elif status.lower() == 'pending': return 'color: orange; font-weight: bold;'
                    return 'color: gray;'
                
                st.dataframe(history_df[["Date", "Amount", "Method", "Status"]].style.map(colorize_status, subset=["Status"]), use_container_width=True, hide_index=True)
            else:
                st.info("You haven't requested any withdrawals yet.")
        except Exception as e:
            st.error(f"Cannot load history: Create `withdrawals` SQL Table. Details: {e}")


# ══════════════════════════════════════════════
#   PAGE: ACCOUNTS
# ══════════════════════════════════════════════
elif page == "Accounts":
    st.title("Accounts")
    st.write("Manage your social media accounts for clipping")
    accounts = st.session_state["accounts"]

    if accounts:
        st.subheader("Your Accounts")
        for idx, acc in enumerate(accounts):
            platform = acc["platform"]
            username = acc["username"]
            status = acc.get("status", "pending")
            code = acc.get("code", "")
            icon_cls = platform.lower().replace("/", "")
            emojis = {"TikTok": "🎵", "Instagram": "📷", "YouTube": "🎬"}
            emoji = emojis.get(platform, "🔗")
            status_html = '<span class="account-status verified">✓ Verified</span>' if status == "verified" else '<span class="account-status pending">⏳ Pending</span>'

            st.markdown(f'<div class="account-card"><div class="account-left"><div class="account-icon {icon_cls}">{emoji}</div><div><span class="account-name">@{username}</span><span class="account-platform">{platform} &nbsp; {status_html}</span></div></div></div>', unsafe_allow_html=True)

            if status == "pending":
                with st.expander(f"🔑 Verify @{username}"):
                    st.markdown(f'<div class="verify-code-box"><div class="verify-instruction">Put this code in your <strong style="color:#fff;">{platform}</strong> bio:</div><span class="verify-code">{code}</span></div>', unsafe_allow_html=True)
                    v1, v2 = st.columns(2)
                    with v1:
                        if st.button("VERIFY NOW", key=f"verify_{idx}", use_container_width=True):
                            with st.spinner(f"Checking @{username}'s bio on {platform}..."):
                                found = check_bio_for_code(platform, username, code)
                            if found:
                                st.session_state["accounts"][idx]["status"] = "verified"
                                row_id = acc.get("id")
                                if row_id:
                                    update_account_verified_in_db(row_id, True)
                                st.success(f"✅ @{username} verified!")
                                st.rerun()
                            else:
                                st.error(f"Code not found in @{username}'s {platform} bio.")
                    with v2:
                        if st.button("REMOVE", key=f"remove_{idx}", use_container_width=True):
                            row_id = acc.get("id")
                            if row_id: delete_account_from_db(row_id)
                            st.session_state["accounts"].pop(idx)
                            st.rerun()
            else:
                if st.button("UNLINK ACCOUNT", key=f"remove_{idx}"):
                    row_id = acc.get("id")
                    if row_id: delete_account_from_db(row_id)
                    st.session_state["accounts"].pop(idx)
                    st.rerun()
            st.markdown("")
    else:
        st.info("No accounts added yet. Add your first social media account below.")

    st.markdown("---")
    st.subheader("Add Account")
    with st.form("add_account_form", clear_on_submit=True):
        a1, a2 = st.columns(2)
        with a1:
            platform = st.selectbox("PLATFORM", ["TikTok", "Instagram", "YouTube"])
        with a2:
            username = st.text_input("USERNAME (without @)")
        add_submitted = st.form_submit_button("ADD ACCOUNT", use_container_width=True)

    if add_submitted:
        if not username:
            st.error("Username is required.")
        else:
            existing = [(a["platform"], a["username"].lower()) for a in st.session_state["accounts"]]
            if (platform, username.lower()) in existing:
                st.warning(f"@{username} on {platform} is already added.")
            else:
                new_code = generate_verify_code()
                saved = save_account_to_db(discord_username, platform, username.strip())
                if saved:
                    saved["code"] = new_code
                    st.session_state["accounts"].append(saved)
                else:
                    st.session_state["accounts"].append({"platform": platform, "username": username.strip(), "status": "pending", "code": new_code})
                st.rerun()


# ══════════════════════════════════════════════
#   PAGE: ADMIN (Owner only)
# ══════════════════════════════════════════════
elif page == "Admin" and is_admin:
    st.title("👑 Admin Portal")
    
    admin_view = st.selectbox("Select Admin Section", ["Campaign Manager", "Submission Review Queue"])
    st.markdown("---")
    
    if admin_view == "Submission Review Queue":
        st.subheader("Clip Review Queue")
        st.write("Approve or reject pending clip submissions before they qualify for payout.")
        
        camp_options = ["All"] + [c.get("name") for c in CAMPAIGNS]
        selected_queue_camp = st.selectbox("Filter by Campaign", camp_options)
        
        try:
            query = supabase.table("clips_track").select("*").eq("status", "Pending")
            
            if selected_queue_camp != "All":
                tgt_camp_id = next((c.get("id") for c in CAMPAIGNS if c.get("name") == selected_queue_camp), None)
                if tgt_camp_id:
                    query = query.eq("campaign_id", tgt_camp_id)
                    
            pending_res = query.execute()
            pending_clips = pending_res.data or []
            
            if not pending_clips:
                st.success("✅ Clean queue! No pending clips to review.")
            else:
                for p_clip in pending_clips:
                    # Dynamically fetch campaign name for context
                    camp_id = p_clip.get('campaign_id')
                    camp_name = next((c.get("name") for c in CAMPAIGNS if c.get("id") == camp_id), "Unknown Campaign")
                    
                    with st.expander(f"Clip from @{p_clip.get('clipper_name')} - {p_clip.get('url')}", expanded=False):
                        st.markdown(f"**Campaign:** {camp_name} (`{camp_id}`)")
                        st.markdown(f"**Submitted At:** {p_clip.get('created_at')}")
                        st.markdown(f"[🔗 View Original Clip]({p_clip.get('url')})")
                        
                        colA, colB = st.columns(2)
                        with colA:
                            if st.button("✅ Approve Clip", key=f"app_{p_clip['id']}", use_container_width=True):
                                supabase.table("clips_track").update({"status": "Approved"}).eq("id", p_clip["id"]).execute()
                                st.rerun()
                        with colB:
                            if st.button("❌ Reject Clip", key=f"rej_{p_clip['id']}", use_container_width=True):
                                supabase.table("clips_track").update({"status": "Rejected"}).eq("id", p_clip["id"]).execute()
                                st.rerun()
        except Exception as e:
            st.error(f"Error loading review queue: {e}")
        
        st.stop() # Prevents rendering the Campaign Manager below it

    st.write("Add, edit, and manage campaigns from here")

    # ── Manual Sync ──
    st.markdown("---")
    st.subheader("🔄 Synchronization")
    if st.button("FORCE VIEW SYNC NOW", help="Fetch the latest views and recalculate budgets."):
        with st.spinner("Syncing with Apify & Supabase... Please wait."):
            try:
                result = subprocess.run(
                    [sys.executable, "bot.py"],
                    capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))
                )
                if result.returncode == 0:
                    st.success("View synchronization and budget recalculation complete!")
                    if result.stdout:
                        st.code(result.stdout, language=None)
                else:
                    st.error(f"Sync failed (exit {result.returncode})")
                    if result.stderr:
                        st.code(result.stderr, language=None)
                load_campaigns.clear()
            except Exception as e:
                st.error(f"Sync failed: {e}")

    # ── Add New Campaign ──
    st.markdown("---")
    st.subheader("➕ Add New Campaign")
    with st.form("add_campaign_form", clear_on_submit=True):
        ac1, ac2 = st.columns(2)
        with ac1:
            new_name = st.text_input("CAMPAIGN NAME")
            new_client = st.text_input("CLIENT NAME")
            new_desc = st.text_area("DESCRIPTION", height=80)
        with ac2:
            new_budget = st.number_input("TOTAL BUDGET ($)", min_value=0.0, step=100.0, value=0.0)
            new_cpm = st.number_input("CPM RATE ($)", min_value=0.0, step=5.0, value=0.0)
            new_docs_url = st.text_input("DOCS URL (Google Docs link)")

        new_tags = st.multiselect("TAGS", ["Music", "TikTok", "Instagram", "YouTube", "Streams", "Sports", "Clipping", "Movies/TV", "Logo"])
        new_image = st.file_uploader("CAMPAIGN IMAGE", type=["jpg", "jpeg", "png"])
        new_client_key = st.text_input("CLIENT ACCESS KEY (for client portal)")

        add_camp = st.form_submit_button("CREATE CAMPAIGN", use_container_width=True)

    if add_camp:
        if not new_name:
            st.error("Campaign name is required.")
        else:
            # Upload image if provided
            img_url = ""
            if new_image:
                try:
                    file_ext = new_image.name.split(".")[-1]
                    file_path = f"campaign_{uuid.uuid4().hex[:8]}.{file_ext}"
                    supabase.storage.from_("campaign-images").upload(file_path, new_image.getvalue(), {"content-type": new_image.type})
                    img_url = f"{SUPABASE_URL}/storage/v1/object/public/campaign-images/{file_path}"
                except Exception as e:
                    st.warning(f"Image upload failed: {e}")

            try:
                supabase.table("campaigns").insert({
                    "name": new_name,
                    "client_name": new_client or "",
                    "description": new_desc or "",
                    "total_budget": new_budget,
                    "cpm_rate": new_cpm,
                    "is_active": True,
                    "is_new": True,
                    "tags": new_tags,
                    "image_url": img_url,
                    "docs_url": new_docs_url or "",
                    "client_key": new_client_key or "",
                }).execute()
                st.success(f"✅ Campaign **{new_name}** created!")
                load_campaigns.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create campaign: {e}")

    # ── Existing Campaigns ──
    st.markdown("---")
    st.subheader("📋 Existing Campaigns")

    for camp in CAMPAIGNS:
        cname = camp.get("name", "")
        is_active = camp.get("is_active", True)
        budget = float(camp.get("total_budget", 0))
        cpm = float(camp.get("cpm_rate", 0))
        pct = float(camp.get("pct_used", 0))
        total_views = int(camp.get("total_views", 0))
        client_key = camp.get("client_key", "")

        status_badge = '<span class="tag-active">● Active</span>' if is_active else '<span class="tag-ended">● Ended</span>'

        with st.expander(f"{cname}  —  {status_badge}", expanded=False):
            st.markdown(f"**Client:** {camp.get('client_name', 'N/A')}", unsafe_allow_html=True)
            st.markdown(f"**Budget:** ${budget:,.2f} | **CPM:** ${cpm:.2f} | **Views:** {total_views:,} | **Used:** {pct:.1f}%")
            if client_key:
                st.code(f"Client Key: {client_key}", language=None)

            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                if is_active:
                    if st.button("⏸ END CAMPAIGN", key=f"end_{cname}"):
                        supabase.table("campaigns").update({"is_active": False}).eq("id", camp["id"]).execute()
                        load_campaigns.clear()
                        st.rerun()
                else:
                    if st.button("▶ REACTIVATE", key=f"reactivate_{cname}"):
                        supabase.table("campaigns").update({"is_active": True}).eq("id", camp["id"]).execute()
                        load_campaigns.clear()
                        st.rerun()
            with ec2:
                if st.button("🗑 DELETE", key=f"delete_{cname}"):
                    supabase.table("campaigns").delete().eq("id", camp["id"]).execute()
                    load_campaigns.clear()
                    st.rerun()
            with ec3:
                if camp.get("is_new"):
                    if st.button("Remove NEW tag", key=f"unnew_{cname}"):
                        supabase.table("campaigns").update({"is_new": False}).eq("id", camp["id"]).execute()
                        load_campaigns.clear()
                        st.rerun()