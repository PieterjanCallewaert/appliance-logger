import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- Supabase credentials ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
SUPABASE_TABLE = "sessions"

def log_to_supabase(row: dict):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    res = requests.post(
        f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
        headers=headers,
        json=row
    )
    if res.status_code not in (200, 201):
        st.error(f"❌ Supabase error: {res.status_code} - {res.text}")
    else:
        st.success("✅ Session saved to Supabase.")

# --- Default appliance list ---
default_appliances = ["oven", "dishwasher", "washing machine", "dryer", "sprinkler", "microwave"]
if "appliance_list" not in st.session_state:
    st.session_state.appliance_list = default_appliances.copy()

if "active_sessions" not in st.session_state:
    st.session_state.active_sessions = {}

st.title("🔌 Appliance Logger")

# --- Start a session ---
st.header("▶️ Start Appliance Session")

selected = st.selectbox("Select appliance", st.session_state.appliance_list + ["Other..."])
if selected == "Other...":
    custom_appliance = st.text_input("Enter new appliance name")
    if custom_appliance:
        if custom_appliance not in st.session_state.appliance_list:
            st.session_state.appliance_list.append(custom_appliance)
        appliance = custom_appliance
    else:
        appliance = None
else:
    appliance = selected

notes = st.text_input("Optional notes")
certainty = st.slider("Certainty (1 = unsure, 5 = sure)", 1, 5, 3)

if appliance and appliance not in st.session_state.active_sessions:
    if st.button("▶️ Start"):
        st.session_state.active_sessions[appliance] = {
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notes": notes,
            "certainty": certainty
        }
        st.success(f"{appliance} started.")

# --- Running sessions ---
st.header("⏱ Currently Running")

if st.session_state.active_sessions:
    for app, info in list(st.session_state.active_sessions.items()):
        st.markdown(f"**{app}** — started at {info['start_time']}")
        if st.button(f"⏹ Stop {app}"):
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = {
                "appliance": app,
                "start_time": info["start_time"],
