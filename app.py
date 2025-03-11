import streamlit as st

# User authentication (dummy credentials for demo)
USER_CREDENTIALS = {
    "admin": {"password": st.secrets["ADMIN_PW"], "role": "admin"},
    "user": {"password": st.secrets["USER_PW"], "role": "user"},
}

st.set_page_config(layout="wide")


def authenticate(email, password) -> str:
    """Validate user credentials and return role if authenticated."""
    user = USER_CREDENTIALS.get(email)
    if user and user["password"] == password:
        return user["role"]
    return None


def logout_func():
    """Clear user session."""
    st.session_state.clear()
    st.rerun()

def login_func():
    st.title("Login")

    with st.form("Login", border=False):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input(
            "Password", placeholder="Enter your password"
        )

        if st.form_submit_button("Login"):
            if role := authenticate(email, password):
                st.session_state.authenticated = True
                st.session_state.email = email
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid email or password")


def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    app_pages = []

    if not st.session_state.authenticated:
        app_pages = [st.Page(login_func)]

    if st.session_state.get('role', None):
        # app_pages.append(st.Page("app_pages/Home.py"))
        app_pages.append(st.Page("app_pages/Chat.py"))

        if st.session_state.get('role', None) == "admin":
            app_pages.append(st.Page("app_pages/Upload_Training_Data.py"))
            app_pages.append(st.Page("app_pages/Manage_Training_Data.py"))

    if st.session_state.get("authenticated", None):
        app_pages.append(st.Page(logout_func, title="Logout"))
    
    page_nav = st.navigation(app_pages)
    page_nav.run()




if __name__ == "__main__":
    main()
