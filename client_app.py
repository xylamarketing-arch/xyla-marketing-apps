import streamlit as st
from supabase import create_client, Client

# --- 1. CONNECT TO SUPABASE ---
URL = "https://hnqpmftzwttcbvwgswmp.supabase.co"
KEY = "sb_publishable_Wv2u3WllKwhgn2JNXZd2nQ_gNxCKmsK"
supabase: Client = create_client(URL, KEY)

# --- 2. PASSWORDS ---
CAMPAIGN_KEYS = {
    "spartan_vip_2026": "Spartans",
    "faze_clips_99": "FaZe Lacy",
    "speed_dash_01": "IShowSpeed",
    "wendy_edit_55": "Wendy Ortiz",
    "test_key_123": "Other"
}

st.set_page_config(page_title="Client Portal | Xyla", page_icon="🔒", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔒 Client Access Portal")
    with st.form("login"):
        pwd = st.text_input("Campaign Key:", type="password")
        if st.form_submit_button("Access Dashboard"):
            if pwd in CAMPAIGN_KEYS:
                st.session_state['logged_in'] = True
                st.session_state['client'] = CAMPAIGN_KEYS[pwd]
                st.rerun()
            else:
                st.error("Invalid Key")

if st.session_state['logged_in']:
    client = st.session_state['client']
    st.title(f"📊 {client} Dashboard")
    
    # FETCH DATA
    res = supabase.table("clips_track").select("*").eq("client_name", client).execute()
    
    if res.data:
        st.write("### Tracked Clips (Newest First)")
        # Show the table (created_at will appear automatically)
        st.dataframe(res.data, use_container_width=True)
    else:
        st.info("No clips found.")
        
    if st.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()