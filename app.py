import streamlit as st
import json
import os
import pandas as pd
import requests
from datetime import datetime
import time

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

# -------- LICENSE CHECK (FINAL FIXED) --------
def check_license(key):
    try:
        for _ in range(3):  # retry 3 times
            url = LICENSE_URL + "?t=" + str(time.time())
            res = requests.get(url, timeout=5)

            if res.status_code == 200:
                data = res.json()

                if key in data:
                    lic = data[key]

                    if lic["status"] != "active":
                        return False, "License inactive"

                    expiry = datetime.strptime(lic["expiry"], "%Y-%m-%d")
                    if datetime.now() > expiry:
                        return False, "License expired"

                    return True, "Valid"

            time.sleep(1)

        return False, "License not found"

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

    users = load_users()
    user = st.session_state.current_user

    if user in users:
        lic = users[user]["license"]

        # real-time check
        valid, msg = check_license(lic)

        if not valid:
            st.session_state.logged_in = False
            st.error(f"Access revoked: {msg}")
            st.stop()

    # Sidebar
    st.sidebar.subheader("⚙️ Settings")
    num_cams = st.sidebar.number_input("Number of Cameras", 0, 10, 2)

    cams = {f"Cam{i+1}": (i+1)*10 for i in range(num_cams)}

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
    else:
        col1, col2 = st.columns(2)

        with col1:
            df = pd.DataFrame({
                "Time": ["10","12","2","4","6","8"],
                "People": [20,40,120,90,200,110]
            })
            st.line_chart(df.set_index("Time"))

        with col2:
            df2 = pd.DataFrame({
                "Camera": list(cams.keys()),
                "People": list(cams.values())
            })
            st.bar_chart(df2.set_index("Camera"))

    st.success("System Running ✅")

    # auto refresh every 5 sec
    time.sleep(5)
    st.rerun()

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
