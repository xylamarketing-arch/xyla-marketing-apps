import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# --- 1. CONNECT TO SUPABASE ---
URL = "https://hnqpmftzwttcbvwgswmp.supabase.co"
KEY = "sb_publishable_Wv2u3WllKwhgn2JNXZd2nQ_gNxCKmsK"

supabase: Client = create_client(URL, KEY)

# --- 2. BUILD THE WEBPAGE ---
st.set_page_config(page_title="Xyla Clipper Portal", page_icon="✂️")
st.title("✂️ Xyla Marketing | Clipper Portal")
st.write("Log your newly posted videos here so the tracking bot can find them.")

with st.form("clipper_form"):
    client_name = st.selectbox("Select Client", ["Spartans", "FaZe Lacy", "IShowSpeed", "Wendy Ortiz", "Other"])
    clipper_name = st.text_input("Your Name (Clipper)")
    video_url = st.text_input("Video URL (TikTok or Instagram)")
    submitted = st.form_submit_button("Submit Video to Database")

# --- 3. SUBMISSION LOGIC ---
if submitted:
    if video_url == "" or clipper_name == "":
        st.error("Please fill in your name and the video URL!")
    else:
        try:
            # Check for duplicates
            check = supabase.table("clips_track").select("video_url").eq("video_url", video_url).execute()
            
            if len(check.data) > 0:
                st.warning("⚠️ This link has already been submitted!")
            else:
                # Get local time
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                new_data = {
                    "created_at": current_time,
                    "client_name": client_name,
                    "clipper_name": clipper_name,
                    "video_url": video_url,
                    "views": 0,
                    "likes": 0,
                    "status": "Pending",
                    "client_notes": ""
                }
                
                supabase.table("clips_track").insert(new_data).execute()
                st.success(f"Success! Submitted for {client_name} at {current_time}.")
                
        except Exception as e:
            st.error(f"Database Error: {e}")