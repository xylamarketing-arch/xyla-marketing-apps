import streamlit as st
from supabase import create_client, Client
from urllib.parse import urlencode
import requests
import pandas as pd
import uuid

# ────────────────────────────────────────────
# 1. PAGE CONFIG
# ────────────────────────────────────────────
st.set_page_config(page_title="Xyla Client Portal", page_icon="📊", layout="wide")

# ────────────────────────────────────────────
# 2. SUPABASE (available pre-login for stats)
# ────────────────────────────────────────────
SUPABASE_URL = "https://hnqpmftzwttcbvwgswmp.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ────────────────────────────────────────────
# 3. DISCORD OAUTH CONFIG
# ────────────────────────────────────────────
DISCORD_CLIENT_ID = st.secrets["DISCORD_CLIENT_ID"]
DISCORD_CLIENT_SECRET = st.secrets["DISCORD_CLIENT_SECRET"]
DISCORD_REDIRECT_URI = st.secrets.get("CLIENT_DISCORD_REDIRECT_URI", "http://localhost:8502/")
DISCORD_API_BASE = "https://discord.com/api/v10"

EXACT_REDIRECT_URI = "http://localhost:8502/"

DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize?" + urlencode({
    "client_id": DISCORD_CLIENT_ID,
    "redirect_uri": EXACT_REDIRECT_URI,
    "response_type": "code",
    "scope": "identify email",
})

# ────────────────────────────────────────────
# 4. ADMIN CONFIG
# ────────────────────────────────────────────
ADMIN_DISCORD_USERNAME = "floydiann_"

# ────────────────────────────────────────────
# 5. THEME CSS
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
div[role="radiogroup"] label p, div[role="radiogroup"] label span, div[role="radiogroup"] label div { color: #888 !important; }
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
div[role="radiogroup"] label:has(input:checked) * { color: #000000 !important; }

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

.tag-active { display:inline-block;padding:3px 10px;border-radius:50px;background:rgba(34,197,94,0.15);color:#22c55e;border:1px solid rgba(34,197,94,0.25);font-size:0.72rem;font-weight:600; }
.tag-ended { display:inline-block;padding:3px 10px;border-radius:50px;background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.25);font-size:0.72rem;font-weight:600; }
.tag-cat { display:inline-block;padding:3px 8px;border-radius:6px;background:rgba(255,255,255,0.06);color:#888;border:1px solid rgba(255,255,255,0.05);font-size:0.7rem;font-weight:500;margin-right:4px;margin-bottom:4px; }
.payout-pill { display:inline-block;padding:4px 12px;border-radius:50px;background:rgba(255,255,255,0.06);color:#aaa;font-size:0.75rem;font-weight:500;margin:6px 0 8px 0; }

.budget-bar-outer { background:rgba(255,255,255,0.06); border-radius:50px; height:10px; margin:8px 0; overflow:hidden; }
.budget-bar-inner { height:100%; border-radius:50px; transition:width 0.5s ease; }
.budget-text { font-size:0.72rem; color:#888; margin-top:2px; }

.user-card { display:flex;align-items:center;gap:12px;padding:12px 16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;margin-bottom:1rem; }
.user-card img { width:40px;height:40px;border-radius:50%;border:2px solid rgba(255,255,255,0.15); }
.user-card .uname { font-weight:600;font-size:0.95rem;color:#fff;display:block; }
.user-card .utag { font-size:0.75rem;color:#888;display:block; }

.report-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:1.5rem; margin-bottom:1rem; }

.admin-badge { display:inline-block;padding:2px 10px;border-radius:50px;background:rgba(168,85,247,0.15);color:#a855f7;border:1px solid rgba(168,85,247,0.25);font-size:0.7rem;font-weight:600; }

.stat-hero { text-align:center; padding:2rem 0; }
.stat-hero .val { font-family:'Plus Jakarta Sans',sans-serif; font-size:3.5rem; font-weight:700; color:#fff; display:block; }
.stat-hero .lab { font-size:0.75rem; letter-spacing:2px; color:#666; text-transform:uppercase; }

.key-badge { display:inline-block; padding:4px 14px; border-radius:8px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); font-family:monospace; font-size:0.85rem; color:#22c55e; letter-spacing:1px; }

div[data-testid="stStatusWidget"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────
# 6. XYLA LOGO
# ────────────────────────────────────────────
XYLA_SVG = """<svg style="width:{size}px;height:{size}px;stroke:white;stroke-width:2;fill:none;stroke-linecap:round;stroke-linejoin:round;" viewBox="0 0 100 100">
    <path d="M30 20 L50 50 L70 20 M30 80 L50 50 L70 80"/>
    <circle cx="30" cy="20" r="5" fill="white" stroke="none"/>
    <circle cx="70" cy="20" r="5" fill="white" stroke="none"/>
    <circle cx="30" cy="80" r="5" fill="white" stroke="none"/>
    <circle cx="70" cy="80" r="5" fill="white" stroke="none"/>
</svg>"""

st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;font-weight:700;font-size:1.4rem;letter-spacing:1px;font-family:'Outfit',sans-serif;margin-bottom:1.5rem;">
    {XYLA_SVG.format(size=30)}
    XYLA.
</div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────
# 7. DISCORD HELPERS
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
# 8. DB HELPERS
# ────────────────────────────────────────────
def upsert_client_user(discord_user: dict) -> dict:
    """Create or update client_users row. Returns the row."""
    provider_id = discord_user.get("id", "")
    username = discord_user.get("username", "")
    display_name = discord_user.get("global_name") or username
    avatar = get_avatar_url(discord_user)
    email = discord_user.get("email", "")

    try:
        # Check if exists
        res = supabase.table("client_users").select("*").eq("provider", "discord").eq("provider_id", provider_id).execute()
        if res.data:
            # Update
            row = res.data[0]
            supabase.table("client_users").update({
                "username": username, "display_name": display_name,
                "avatar_url": avatar, "email": email,
            }).eq("id", row["id"]).execute()
            row.update({"username": username, "display_name": display_name, "avatar_url": avatar, "email": email})
            return row
        else:
            # Insert
            is_admin = (username == ADMIN_DISCORD_USERNAME)
            ins = supabase.table("client_users").insert({
                "provider": "discord", "provider_id": provider_id,
                "username": username, "display_name": display_name,
                "avatar_url": avatar, "email": email, "is_admin": is_admin,
            }).execute()
            return ins.data[0] if ins.data else {}
    except Exception as e:
        st.toast(f"⚠️ User save error: {e}", icon="⚠️")
        return {}

def get_unlocked_campaign_ids(user_id: str) -> list:
    """Get list of campaign IDs this user has unlocked."""
    try:
        res = supabase.table("client_unlocks").select("campaign_id").eq("user_id", user_id).execute()
        return [r["campaign_id"] for r in res.data] if res.data else []
    except Exception:
        return []

def unlock_campaign(user_id: str, access_key: str) -> tuple:
    """Try to unlock a campaign with an access key. Returns (success, message)."""
    try:
        # Find the key
        res = supabase.table("campaign_keys").select("*").eq("access_key", access_key).eq("is_active", True).execute()
        if not res.data:
            return False, "Invalid or expired access key."
        key_row = res.data[0]
        campaign_id = key_row["campaign_id"]

        # Check if already unlocked
        existing = supabase.table("client_unlocks").select("id").eq("user_id", user_id).eq("campaign_id", campaign_id).execute()
        if existing.data:
            return True, "This campaign is already unlocked!"

        # Create unlock
        supabase.table("client_unlocks").insert({
            "user_id": user_id, "campaign_id": campaign_id,
        }).execute()

        # Get campaign name for success message
        camp = supabase.table("campaigns").select("name").eq("id", campaign_id).execute()
        camp_name = camp.data[0]["name"] if camp.data else "Campaign"
        return True, f"✅ Unlocked: **{camp_name}**"
    except Exception as e:
        return False, f"Error: {e}"

@st.cache_data(ttl=30)
def load_agency_stats():
    """Load aggregate agency stats for the public landing page."""
    try:
        # Total views, clips from clips_track
        res = supabase.table("clips_track").select("views", count="exact").execute()
        total_views = sum(r.get("views", 0) for r in (res.data or []))
        total_clips = res.count or len(res.data or [])

        # Campaigns data
        camp_res = supabase.table("campaigns").select("id, is_active, budget_used").execute()
        camps = camp_res.data or []
        active_campaigns = sum(1 for c in camps if c.get("is_active"))
        total_campaigns = len(camps)
        total_paid = sum(float(c.get("budget_used", 0)) for c in camps)

        return {
            "total_views": total_views,
            "total_clips": total_clips,
            "active_campaigns": active_campaigns,
            "total_campaigns": total_campaigns,
            "total_paid": total_paid,
        }
    except Exception:
        return {"total_views": 0, "total_clips": 0, "active_campaigns": 0, "total_campaigns": 0, "total_paid": 0}

@st.cache_data(ttl=15)
def load_campaigns():
    """Load all campaigns."""
    try:
        return supabase.table("campaigns").select("*").order("created_at", desc=False).execute().data or []
    except Exception:
        return []


# ────────────────────────────────────────────
# 9. SESSION STATE
# ────────────────────────────────────────────
defaults = {
    "authenticated": False,
    "discord_user": None,
    "client_db_user": None,
    "view_campaign": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ────────────────────────────────────────────
# 10. OAUTH CALLBACK
# ────────────────────────────────────────────
code = st.query_params.get("code")
if code and not st.session_state["authenticated"]:
    # Force EXACT redirect URI match
    EXACT_REDIRECT_URI = "http://localhost:8502/"
    
    try:
        # Inline the exchange to ensure the exact URI is used
        r = requests.post(f"{DISCORD_API_BASE}/oauth2/token",
                      data={"client_id": DISCORD_CLIENT_ID, "client_secret": DISCORD_CLIENT_SECRET,
                            "grant_type": "authorization_code", "code": code, "redirect_uri": EXACT_REDIRECT_URI},
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        if r.status_code != 200:
            st.error(f"Discord API Error {r.status_code}: {r.text}")
            st.stop()
            
        token_data = r.json()
        discord_user = get_discord_user(token_data["access_token"])
        db_user = upsert_client_user(discord_user)
        st.session_state["authenticated"] = True
        st.session_state["discord_user"] = discord_user
        st.session_state["client_db_user"] = db_user
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.query_params.clear()
        st.error(f"Discord authentication failed: {e}. Please try logging in again.")
        import time; time.sleep(2)
        st.rerun()


# ════════════════════════════════════════════
#  PUBLIC LANDING PAGE (pre-login)
# ════════════════════════════════════════════
if not st.session_state["authenticated"]:
    stats = load_agency_stats()

    # Agency Overview Stats — TOP
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Agency Overview")
    st.write("Real-time metrics across all campaigns")

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("TOTAL VIEWS", f"{stats['total_views']:,}")
    s2.metric("ACTIVE CAMPAIGNS", stats["active_campaigns"])
    s3.metric("TOTAL CLIPS", f"{stats['total_clips']:,}")
    s4.metric("CAMPAIGNS MANAGED", stats["total_campaigns"])
    s5.metric("TOTAL PAID", f"${stats['total_paid']:,.2f}")

    # Login Card — BELOW
    st.markdown("<br><br>", unsafe_allow_html=True)
    _c1, _c2, _c3 = st.columns([1, 2, 1])
    with _c2:
        discord_svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189z"/></svg>'

        st.markdown(f"""
        <div class="hero-glass">
            {XYLA_SVG.format(size=50)}
            <h2 style="font-size:1.8rem;margin:1rem 0 0.5rem;">CLIENT PORTAL</h2>
            <p style="color:#666;font-size:0.9rem;margin-bottom:2rem;text-transform:uppercase;letter-spacing:2px;">The Algorithm is Human</p>
            <a href="{DISCORD_AUTH_URL}" class="discord-btn">{discord_svg} Login with Discord</a>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ════════════════════════════════════════════
#  AUTHENTICATED — SETUP
# ════════════════════════════════════════════
discord_user = st.session_state["discord_user"]
db_user = st.session_state["client_db_user"]
discord_username = discord_user.get("username", "Unknown")
discord_display = discord_user.get("global_name") or discord_username
avatar_url = get_avatar_url(discord_user)
user_db_id = db_user.get("id", "")
is_admin = db_user.get("is_admin", False) or (discord_username == ADMIN_DISCORD_USERNAME)

ALL_CAMPAIGNS = load_campaigns()
unlocked_ids = get_unlocked_campaign_ids(user_db_id)

# Admin sees all campaigns
if is_admin:
    user_campaigns = ALL_CAMPAIGNS
else:
    user_campaigns = [c for c in ALL_CAMPAIGNS if c.get("id") in unlocked_ids]


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
    nav_options = ["Campaigns", "Dashboard"]
    if is_admin:
        nav_options.append("Admin")
    page = st.radio("NAV", nav_options, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(
        """<a href="mailto:Xylamarketing@gmail.com?subject=Book%20a%20Campaign%20Call%20-%20Google%20Meet" target="_blank" style="display:block; text-align:center; padding:10px; background:rgba(138,43,226,0.15); color:#c48df5; border:1px solid rgba(138,43,226,0.3); border-radius:10px; text-decoration:none; font-weight:600; font-size:0.85rem; margin-bottom:1rem; transition:all 0.3s ease;">🚀 Launch a Campaign</a>""",
        unsafe_allow_html=True
    )
    if st.button("LOGOUT"):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()


# ════════════════════════════════════════════
#  PAGE: CAMPAIGNS
# ════════════════════════════════════════════
if page == "Campaigns":

    # ── Campaign Detail View ──
    if st.session_state.get("view_campaign"):
        camp_id = st.session_state["view_campaign"]
        camp = next((c for c in ALL_CAMPAIGNS if c.get("id") == camp_id), None)

        if not camp:
            st.error("Campaign not found.")
            st.session_state["view_campaign"] = None
            st.rerun()
        else:
            if st.button("← BACK TO CAMPAIGNS"):
                st.session_state["view_campaign"] = None
                st.rerun()

            cname = camp.get("name", "")
            total_budget = float(camp.get("total_budget", 0))
            budget_used = float(camp.get("budget_used", 0))
            pct_used = float(camp.get("pct_used", 0))
            total_views = int(camp.get("total_views", 0))
            cpm = float(camp.get("cpm_rate", 0))
            remaining = max(total_budget - budget_used, 0)
            is_active = camp.get("is_active", True)

            st.title(cname)
            badge = '<span class="tag-active">● Active</span>' if is_active else '<span class="tag-ended">● Completed</span>'
            st.markdown(badge, unsafe_allow_html=True)
            st.write(camp.get("description", ""))

            # Key Metrics
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("TOTAL VIEWS", f"{total_views:,}")
            m2.metric("TOTAL BUDGET", f"${total_budget:,.0f}")
            m3.metric("BUDGET USED", f"${budget_used:,.2f}")
            m4.metric("REMAINING", f"${remaining:,.0f}")

            # Budget Progress
            bar_color = "#22c55e" if pct_used < 50 else ("#eab308" if pct_used < 80 else "#ef4444")
            st.markdown(f'''
            <div style="margin:1rem 0;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="color:#888;font-size:0.8rem;">Budget Utilization</span>
                    <span style="color:#fff;font-size:0.9rem;font-weight:700;">{pct_used:.1f}%</span>
                </div>
                <div class="budget-bar-outer" style="height:14px;">
                    <div class="budget-bar-inner" style="width:{min(pct_used, 100)}%;background:{bar_color};"></div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            # CPM Details
            st.markdown(f"""
            <div class="report-card">
                <strong style="color:#fff;">💰 Pricing Model</strong><br>
                <span style="color:#9ca3af;">CPM Rate: <strong style="color:#fff;">${cpm:.2f}</strong></span><br>
                <span style="color:#9ca3af;">Formula: (Total Views ÷ 1,000) × CPM = Budget Used</span><br>
                <span style="color:#9ca3af;">({total_views:,} ÷ 1,000) × ${cpm:.2f} = <strong style="color:#fff;">${budget_used:,.2f}</strong></span>
            </div>
            """, unsafe_allow_html=True)

            # Clipper Leaderboard
            st.markdown("---")
            st.subheader("CLIPPER LEADERBOARD")
            try:
                clips_res = supabase.table("clips_track").select("*").eq("campaign_id", camp_id).execute()
                clips = clips_res.data or []
            except Exception:
                clips = []

            if clips:
                df = pd.DataFrame(clips)
                leaderboard = df.groupby("clipper_name")["views"].sum().sort_values(ascending=False)
                st.bar_chart(leaderboard, color="#ffffff")

                st.subheader("LIVE CONTENT FEED")
                display_cols = [c for c in ["video_url", "clipper_name", "views", "likes", "status", "created_at"] if c in df.columns]
                st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
            else:
                st.info("No clips submitted yet for this campaign.")

            # Agency Notes
            notes = camp.get("notes", "")
            if notes:
                st.markdown("---")
                st.markdown(f'<div class="report-card"><strong style="color:#fff;">📢 Agency Feedback</strong><br><span style="color:#9ca3af;">{notes}</span></div>', unsafe_allow_html=True)

    else:
        # ── Campaign Cards ──
        st.title("Your Campaigns")
        st.write(f"Welcome back, {discord_display}")

        # Unlock key input
        st.markdown("---")
        k_col1, k_col2 = st.columns([3, 1])
        with k_col1:
            key_input = st.text_input("🔑 ENTER ACCESS KEY", placeholder="e.g. XYLA-SILENT-123", label_visibility="collapsed")
        with k_col2:
            unlock_btn = st.button("UNLOCK CAMPAIGN", use_container_width=True)

        if unlock_btn and key_input:
            success, msg = unlock_campaign(user_db_id, key_input.strip())
            if success:
                st.success(msg)
                st.cache_data.clear()
                import time; time.sleep(1)
                st.rerun()
            else:
                st.error(msg)

        st.markdown("---")

        if not user_campaigns and not is_admin:
            st.info("No campaigns unlocked yet. Enter an access key above to unlock your campaign dashboard.")
        else:
            cols_per_row = 3
            for row_start in range(0, len(user_campaigns), cols_per_row):
                row_items = user_campaigns[row_start:row_start + cols_per_row]
                cols = st.columns(cols_per_row)
                for i, camp in enumerate(row_items):
                    with cols[i]:
                        img_url = camp.get("image_url", "")
                        if img_url:
                            st.image(img_url, use_container_width=True)
                        else:
                            st.image("demo.jpg", use_container_width=True)

                        is_active = camp.get("is_active", True)
                        badge = '<span class="tag-active">● Active</span>' if is_active else '<span class="tag-ended">● Completed</span>'
                        st.markdown(badge, unsafe_allow_html=True)

                        st.markdown(f"**{camp.get('name', '')}**")
                        st.caption(camp.get("description", ""))

                        total_budget = float(camp.get("total_budget", 0))
                        pct_used = float(camp.get("pct_used", 0))
                        total_views = int(camp.get("total_views", 0))
                        cpm = float(camp.get("cpm_rate", 0))

                        if cpm > 0:
                            st.markdown(f'<span class="payout-pill">${cpm:.0f} CPM</span>', unsafe_allow_html=True)

                        if total_budget > 0:
                            bar_color = "#22c55e" if pct_used < 50 else ("#eab308" if pct_used < 80 else "#ef4444")
                            st.markdown(f'''
                            <div class="budget-bar-outer"><div class="budget-bar-inner" style="width:{min(pct_used, 100)}%;background:{bar_color};"></div></div>
                            <div class="budget-text">{pct_used:.1f}% used · {total_views:,} views</div>
                            ''', unsafe_allow_html=True)

                        tags = camp.get("tags") or []
                        if tags:
                            st.markdown("".join(f'<span class="tag-cat">{t}</span>' for t in tags), unsafe_allow_html=True)

                        if st.button("ACCESS CAMPAIGN →", key=f"access_{camp['id']}", use_container_width=True):
                            st.session_state["view_campaign"] = camp["id"]
                            st.rerun()


# ════════════════════════════════════════════
#  PAGE: DASHBOARD (aggregate)
# ════════════════════════════════════════════
elif page == "Dashboard":
    st.title("Dashboard")
    st.write(f"Overview for {discord_display}")

    if not user_campaigns:
        st.info("No campaigns unlocked yet. Go to Campaigns and enter an access key.")
    else:
        total_budget_all = sum(float(c.get("total_budget", 0)) for c in user_campaigns)
        total_used_all = sum(float(c.get("budget_used", 0)) for c in user_campaigns)
        total_views_all = sum(int(c.get("total_views", 0)) for c in user_campaigns)
        total_remaining = max(total_budget_all - total_used_all, 0)
        overall_pct = (total_used_all / total_budget_all * 100) if total_budget_all > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TOTAL VIEWS", f"{total_views_all:,}")
        m2.metric("TOTAL BUDGET", f"${total_budget_all:,.0f}")
        m3.metric("TOTAL SPENT", f"${total_used_all:,.2f}")
        m4.metric("REMAINING", f"${total_remaining:,.0f}")

        bar_color = "#22c55e" if overall_pct < 50 else ("#eab308" if overall_pct < 80 else "#ef4444")
        st.markdown(f'''
        <div style="margin:1rem 0 2rem 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="color:#888;font-size:0.8rem;">Overall Budget Utilization</span>
                <span style="color:#fff;font-size:0.9rem;font-weight:700;">{overall_pct:.1f}%</span>
            </div>
            <div class="budget-bar-outer" style="height:14px;">
                <div class="budget-bar-inner" style="width:{min(overall_pct, 100)}%;background:{bar_color};"></div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Campaign Breakdown")
        for camp in user_campaigns:
            cname = camp.get("name", "")
            budget = float(camp.get("total_budget", 0))
            used = float(camp.get("budget_used", 0))
            views = int(camp.get("total_views", 0))
            pct = float(camp.get("pct_used", 0))
            is_active = camp.get("is_active", True)

            badge = '<span class="tag-active">● Active</span>' if is_active else '<span class="tag-ended">● Completed</span>'
            st.markdown(f"#### {cname}  {badge}", unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Views", f"{views:,}")
            c2.metric("Budget", f"${budget:,.0f}")
            c3.metric("Spent", f"${used:,.2f}")
            c4.metric("Used", f"{pct:.1f}%")

            bar_color = "#22c55e" if pct < 50 else ("#eab308" if pct < 80 else "#ef4444")
            st.markdown(f'<div class="budget-bar-outer"><div class="budget-bar-inner" style="width:{min(pct, 100)}%;background:{bar_color};"></div></div>', unsafe_allow_html=True)
            st.markdown("")


# ════════════════════════════════════════════
#  PAGE: ADMIN (floydiann_ only)
# ════════════════════════════════════════════
elif page == "Admin" and is_admin:
    st.title("👑 Admin Panel")
    st.write("Manage access keys, view clients, and monitor the agency")

    admin_tab = st.radio("Section", ["Agency Overview", "Access Keys", "Clients"], horizontal=True, label_visibility="collapsed")

    # ── Agency Overview ──
    if admin_tab == "Agency Overview":
        st.markdown("---")
        st.subheader("Agency Overview")
        stats = load_agency_stats()
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("TOTAL VIEWS", f"{stats['total_views']:,}")
        s2.metric("ACTIVE CAMPAIGNS", stats["active_campaigns"])
        s3.metric("TOTAL CLIPS", f"{stats['total_clips']:,}")
        s4.metric("CAMPAIGNS MANAGED", stats["total_campaigns"])

        st.markdown("---")
        st.subheader("All Campaigns")
        for camp in ALL_CAMPAIGNS:
            cname = camp.get("name", "")
            budget = float(camp.get("total_budget", 0))
            used = float(camp.get("budget_used", 0))
            views = int(camp.get("total_views", 0))
            pct = float(camp.get("pct_used", 0))
            is_active = camp.get("is_active", True)
            badge = '<span class="tag-active">● Active</span>' if is_active else '<span class="tag-ended">● Completed</span>'

            with st.expander(f"{cname}  —  {badge}"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Views", f"{views:,}")
                c2.metric("Budget", f"${budget:,.0f}")
                c3.metric("Used", f"${used:,.2f}")
                c4.metric("%", f"{pct:.1f}%")

    # ── Access Keys ──
    elif admin_tab == "Access Keys":
        st.markdown("---")
        st.subheader("Generate New Access Key")

        with st.form("gen_key_form", clear_on_submit=True):
            camp_options = {c.get("name", ""): c.get("id", "") for c in ALL_CAMPAIGNS}
            selected_camp = st.selectbox("Campaign", list(camp_options.keys()))
            key_label = st.text_input("Label (optional)", placeholder="e.g., Key for client John")
            gen_btn = st.form_submit_button("GENERATE KEY", use_container_width=True)

        if gen_btn and selected_camp:
            camp_id = camp_options[selected_camp]
            # Generate a readable key
            short = selected_camp.replace(" ", "-")[:10].upper()
            new_key = f"XYLA-{short}-{uuid.uuid4().hex[:4].upper()}"
            try:
                supabase.table("campaign_keys").insert({
                    "campaign_id": camp_id, "access_key": new_key,
                    "label": key_label or f"Key for {selected_camp}", "is_active": True,
                }).execute()
                st.success(f"✅ Key generated!")
                st.markdown(f'<span class="key-badge">{new_key}</span>', unsafe_allow_html=True)
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Failed: {e}")

        st.markdown("---")
        st.subheader("Existing Keys")
        try:
            keys_res = supabase.table("campaign_keys").select("*, campaigns(name)").order("created_at", desc=True).execute()
            keys = keys_res.data or []
        except Exception:
            keys = []

        if keys:
            for k in keys:
                camp_info = k.get("campaigns", {})
                camp_name = camp_info.get("name", "Unknown") if isinstance(camp_info, dict) else "Unknown"
                status_text = "🟢 Active" if k.get("is_active") else "🔴 Revoked"
                label = k.get("label", "")

                with st.expander(f"{k.get('access_key', '')}  —  {camp_name}  —  {status_text}"):
                    st.write(f"**Label:** {label}")
                    st.write(f"**Campaign:** {camp_name}")
                    st.write(f"**Created:** {k.get('created_at', '')[:10]}")
                    if k.get("is_active"):
                        if st.button("🔴 REVOKE KEY", key=f"revoke_{k['id']}"):
                            supabase.table("campaign_keys").update({"is_active": False}).eq("id", k["id"]).execute()
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        if st.button("🟢 REACTIVATE", key=f"reactivate_{k['id']}"):
                            supabase.table("campaign_keys").update({"is_active": True}).eq("id", k["id"]).execute()
                            st.cache_data.clear()
                            st.rerun()
        else:
            st.info("No access keys generated yet.")

    # ── Clients ──
    elif admin_tab == "Clients":
        st.markdown("---")
        st.subheader("Registered Clients")
        try:
            clients_res = supabase.table("client_users").select("*").order("created_at", desc=True).execute()
            clients = clients_res.data or []
        except Exception:
            clients = []

        if clients:
            for client in clients:
                c_name = client.get("display_name") or client.get("username", "Unknown")
                c_user = client.get("username", "")
                c_provider = client.get("provider", "")
                c_email = client.get("email", "")
                c_admin = client.get("is_admin", False)
                c_avatar = client.get("avatar_url", "")
                c_joined = client.get("created_at", "")[:10] if client.get("created_at") else ""

                with st.expander(f"{'👑 ' if c_admin else ''}{c_name}  —  @{c_user}  —  {c_provider}"):
                    ec1, ec2 = st.columns([1, 3])
                    with ec1:
                        if c_avatar:
                            st.image(c_avatar, width=80)
                    with ec2:
                        st.write(f"**Username:** @{c_user}")
                        st.write(f"**Provider:** {c_provider}")
                        if c_email:
                            st.write(f"**Email:** {c_email}")
                        st.write(f"**Joined:** {c_joined}")
                        if c_admin:
                            st.markdown('<span class="admin-badge">👑 ADMIN</span>', unsafe_allow_html=True)

                    # Show unlocked campaigns
                    try:
                        unlocks = supabase.table("client_unlocks").select("campaign_id, campaigns(name)").eq("user_id", client["id"]).execute()
                        if unlocks.data:
                            st.write("**Unlocked campaigns:**")
                            for u in unlocks.data:
                                ci = u.get("campaigns", {})
                                cn = ci.get("name", "Unknown") if isinstance(ci, dict) else "Unknown"
                                st.markdown(f"&nbsp;&nbsp;✅ {cn}")
                        else:
                            st.write("No campaigns unlocked.")
                    except Exception:
                        st.write("Could not load unlocks.")
        else:
            st.info("No clients registered yet.")