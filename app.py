import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

st.set_page_config(layout="wide")

# Define file path
ADMIN_FOLDER = "admin"
USER_FILE = os.path.join(ADMIN_FOLDER, "users.csv")

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load existing users or create an empty DataFrame
def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE, parse_dates=["Expiration Date"], dayfirst=True)
    else:
        return pd.DataFrame(
            columns=["Email", "Password", "Role", "Create Date", "Expiration Date"]
        )

# User authentication
def authenticate(email, password):
    users_df = load_users()
    user = users_df[(users_df["Email"] == email) & (users_df["Password"] == hash_password(password))]
    if not user.empty:
        expiration_date = user.iloc[0]["Expiration Date"]
        if pd.notna(expiration_date) and expiration_date >= datetime.today():
            return user.iloc[0]["Role"]
        else:
            st.error("Your account has expired. Please contact the administrator.")
            st.stop()
    return None

def logout_func():
    """Clear user session."""
    st.session_state.clear()
    st.rerun()

def login_func():
    st.title("Login")

    with st.form("Login", border=False):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.form_submit_button("Login"):
            if role := authenticate(email, password):
                st.session_state.authenticated = True
                st.session_state.email = email
                st.session_state.role = role.lower()
                st.rerun()
            else:
                st.error("Invalid email or password")

def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    app_pages = []

    if not st.session_state.authenticated:
        app_pages = [st.Page(login_func)]

    if st.session_state.get("role", None):
        # app_pages.append(st.Page("app_pages/Home.py"))
        app_pages.append(st.Page("app_pages/Chat.py"))

        if st.session_state.get("role", None) == "admin":
            app_pages.append(st.Page("app_pages/Upload_Training_Data.py"))
            app_pages.append(st.Page("app_pages/Manage_Training_Data.py"))
            app_pages.append(st.Page("app_pages/Add_User.py"))

    if st.session_state.get("authenticated", None):
        app_pages.append(st.Page(logout_func, title="Logout"))

    page_nav = st.navigation(app_pages)
    page_nav.run()

if __name__ == "__main__":
    main()
