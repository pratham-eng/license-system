import streamlit as st
import json
from datetime import datetime
import pandas as pd
import os
import requests

st.set_page_config(layout="wide")

# -------- CONFIG --------
LICENSE_URL = "https://raw.githubusercontent.com/pratham-eng/license-system/main/license.json"

# -------- FILE HELPERS --------
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# -------- SESSION --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# -------- LICENSE CHECK --------
def check_license(key):
    try:
        res = requests.get(LICENSE_URL)

        if res.status_code != 200:
            return False, "Server error"

        data = res.json()

        if key in data:
            lic = data[key]

            if lic["status"] != "active":
                return False, "License inactive"

            expiry = datetime.strptime(lic["expiry"], "%Y-%m-%d")
            if datetime.now() > expiry:
                return False, "License expired"

            return True, "Valid"

        return False, "Invalid license"

    except:
        return False, "Connection error"

# -------- SIGNUP --------
def signup():
    st.title("📝 Sign Up")

    users = load_users()

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    lic = st.text_input("License Key")

    if st.button("Create Account"):

        if user in users:
            st.error("User already exists")
            return

        valid, msg = check_license(lic)

        if valid:
            users[user] = {
                "password": pwd,
                "license": lic
            }
            save_users(users)
            st.success("Account created ✅ → Now Login")
        else:
            st.error(msg)

# -------- LOGIN --------
def login():
    st.title("🔐 Login")

    users = load_users()

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        if user in users:

            if users[user]["password"] == pwd:

                lic = users[user]["license"]
                valid, msg = check_license(lic)

                if not valid:
                    st.error(f"Access Denied: {msg}")
                    return

                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.rerun()

            else:
                st.error("Wrong password")
        else:
            st.error("User not found")

# -------- DASHBOARD --------
def dashboard():

    st.title("📊 Daily Store Analytics")

    # Sidebar camera control
    st.sidebar.subheader("⚙️ Settings")
    num_cams = st.sidebar.number_input("Number of Cameras", 0, 10, 2)

    # Load data
    data = {}
    if os.path.exists("data.json"):
        try:
            with open("data.json", "r") as f:
                data = json.load(f)
        except:
            st.warning("Data error")

    # Camera data
    cams = {}
    for i in range(num_cams):
        cam = f"Cam{i+1}"
        cams[cam] = data.get("cams", {}).get(cam, (i+1)*10)

    # KPI
    total = sum(cams.values())
    entries = total
    exits = int(total * 0.8)
    conv = int((exits/entries)*100) if entries else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total", total)
    col2.metric("➡️ Entry", entries)
    col3.metric("⬅️ Exit", exits)
    col4.metric("🔥 Conv%", f"{conv}%")

    st.divider()

    if num_cams == 0:
        st.warning("No Cameras Added")
        return

    # Graphs
    col1, col2 = st.columns(2)

    with col1:
        df = pd.DataFrame({
            "Time": ["10","12","2","4","6","8"],
            "People": [20,40,120,90,200,110]
        })
        st.line_chart(df.set_index("Time"), height=250)

    with col2:
        df2 = pd.DataFrame({
            "Camera": list(cams.keys()),
            "People": list(cams.values())
        })
        st.bar_chart(df2.set_index("Camera"), height=250)

    st.divider()

    st.success("System Running ✅")
    st.write(f"Cameras Active: {num_cams}")

# -------- MAIN --------
menu = st.sidebar.radio("Menu", ["Login", "Sign Up"])

if not st.session_state.logged_in:
    if menu == "Login":
        login()
    else:
        signup()
else:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    dashboard()