
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, time

# --- Supabase credentials ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
SUPABASE_TABLE = "sessions"

def log_to_supabase(row: dict):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer " + SUPABASE_KEY,
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

# --- Initial appliance list ---
default_appliances = ["oven", "dishwasher", "washing machine", "dryer", "sprinkler", "microwave"]
if "appliance_list" not in st.session_state:
    st.session_state.appliance_list = default_appliances.copy()

st.title("🔌 Appliance Logger")

if "active_sessions" not in st.session_state:
    st.session_state.active_sessions = {}

# --- Start Session UI ---
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

# --- Running Appliances ---
st.header("⏱ Currently Running")

if st.session_state.active_sessions:
    for app, info in list(st.session_state.active_sessions.items()):
        st.markdown(f"**{app}** — started at {info['start_time']}")
        if st.button(f"⏹ Stop {app}"):
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = {
                "appliance": app,
                "start_time": info["start_time"],
                "end_time": end_time,
                "notes": info["notes"],
                "certainty": info["certainty"]
            }
            log_to_supabase(new_entry)
            del st.session_state.active_sessions[app]
else:
    st.info("No running appliances.")

# --- Manual Entry ---
st.header("✍️ Add Session Manually")

with st.expander("Add manually"):
    man_app = st.selectbox("Appliance", st.session_state.appliance_list + ["Other"], key="manual_app_select")
    if man_app == "Other":
        man_app = st.text_input("Enter custom appliance", key="manual_custom_app")
        if man_app and man_app not in st.session_state.appliance_list:
            st.session_state.appliance_list.append(man_app)

    man_start_date = st.date_input("Start date")
    man_start_time = st.time_input("Start time")
    man_end_date = st.date_input("End date")
    man_end_time = st.time_input("End time")
    man_notes = st.text_input("Notes", key="manual_notes")
    man_certainty = st.slider("Certainty", 1, 5, 3, key="manual_certainty")

    if st.button("➕ Add Session"):
        try:
            start_ts = datetime.combine(man_start_date, man_start_time).strftime("%Y-%m-%d %H:%M:%S")
            end_ts = datetime.combine(man_end_date, man_end_time).strftime("%Y-%m-%d %H:%M:%S")
            new_manual = {
                "appliance": man_app,
                "start_time": start_ts,
                "end_time": end_ts,
                "notes": man_notes,
                "certainty": man_certainty
            }
            log_to_supabase(new_manual)
        except Exception as e:
            st.error(f"Error: {e}")
