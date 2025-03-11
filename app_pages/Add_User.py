import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# Define file path
ADMIN_FOLDER = "admin"
USER_FILE = os.path.join(ADMIN_FOLDER, "users.csv")

# Ensure admin folder exists
os.makedirs(ADMIN_FOLDER, exist_ok=True)

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load existing users or create an empty DataFrame
def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    else:
        return pd.DataFrame(columns=["Email", "Password", "Role", "Create Date", "Expiration Date"])

# Save users to file
def save_users(users_df):
    users_df.to_csv(USER_FILE, index=False)

# User authentication
def authenticate(email, password):
    users_df = load_users()
    user = users_df[(users_df["Email"] == email) & (users_df["Password"] == hash_password(password))]
    if not user.empty:
        return user.iloc[0]["Role"]
    return None

# Streamlit UI
st.title("User Management")

# User input fields
email = st.text_input("Email")
password = st.text_input("Password", type="password")
role = st.selectbox("Role", ["Admin", "User", "Guest"])
create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
expiration_date = st.date_input("Expiration Date")

# Load users data
users_df = load_users()

if st.button("Add User"):
    if email and password and role and expiration_date:
        hashed_password = hash_password(password)
        if ((users_df["Email"] == email) & (users_df["Role"] == role)).any():
            st.error("User with this role already exists. Please use a different password.")
        else:
            new_user = pd.DataFrame({
                "Email": [email],
                "Password": [hashed_password],
                "Role": [role],
                "Create Date": [create_date],
                "Expiration Date": [expiration_date]
            })
            users_df = pd.concat([users_df, new_user], ignore_index=True)
            save_users(users_df)
            st.success("User added successfully!")
    else:
        st.error("Please fill in all fields.")

# Display existing users without passwords
st.subheader("Existing Users")
users_display = users_df.drop(columns=["Password"], errors='ignore')
st.dataframe(users_display)
