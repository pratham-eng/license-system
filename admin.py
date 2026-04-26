import streamlit as st
import json
import requests
import base64

st.set_page_config(layout="wide")
st.title("🛠️ Admin License Panel")

# -------- CONFIG --------
GITHUB_TOKEN = "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"
REPO = "pratham-eng/license-system"
FILE_PATH = "license.json"

# -------- LOAD --------
def load_data():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        data = res.json()
        content = base64.b64decode(data["content"]).decode()
        return json.loads(content), data["sha"]
    else:
        st.error(f"GitHub Load Error: {res.status_code}")
        return {}, None

# -------- SAVE --------
def save_data(data, sha):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    content = json.dumps(data, indent=4)
    encoded = base64.b64encode(content.encode()).decode()

    payload = {
        "message": "update license",
        "content": encoded,
        "sha": sha
    }

    res = requests.put(url, json=payload, headers=headers)
    return res.status_code

# -------- MAIN --------
licenses, sha = load_data()

# -------- CREATE --------
st.subheader("➕ Create License")

key = st.text_input("License Key")
expiry = st.date_input("Expiry Date")
active = st.checkbox("Active", True)

if st.button("Save License"):
    if key:
        licenses[key] = {
            "status": "active" if active else "inactive",
            "expiry": str(expiry)
        }

        status = save_data(licenses, sha)

        if status in [200, 201]:
            st.success("Saved ✅")
            st.rerun()
        else:
            st.error(f"Error: {status}")

st.divider()

# -------- LIST --------
st.subheader("📋 Licenses")

delete_key = None

for k in licenses:
    col1, col2, col3, col4 = st.columns([3,2,2,1])

    col1.write(k)
    new_exp = col2.text_input("Expiry", licenses[k]["expiry"], key=f"exp_{k}")
    active_chk = col3.checkbox("Active", licenses[k]["status"]=="active", key=f"chk_{k}")

    if col4.button("Update", key=f"u_{k}"):
        licenses[k]["expiry"] = new_exp
        licenses[k]["status"] = "active" if active_chk else "inactive"

        status = save_data(licenses, sha)
        if status in [200, 201]:
            st.success("Updated")
            st.rerun()

    if st.button(f"Delete {k}"):
        delete_key = k

if delete_key:
    del licenses[delete_key]

    status = save_data(licenses, sha)
    if status in [200, 201]:
        st.warning("Deleted")
        st.rerun()