import streamlit as st
import os
import pandas as pd

USER_DATA_FILE = "data/users.csv"

def login_signup():
    st.title("Login/Signup")
    tab_login, tab_signup = st.tabs(["Login", "Signup"])

    # Login tab
    with tab_login:
        st.subheader("Login")
        username_login = st.text_input("Username", key="login_username")  # Unique key for login username
        password_login = st.text_input("Password", type="password", key="login_password")  # Unique key for login password
        if st.button("Login", key="login_button"):  # Unique key for login button
            if authenticate_user(username_login, password_login):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username_login
                # Simulate a rerun by setting a flag in session state
                st.session_state["rerun_flag"] = True
                st.session_state["page"] = "main"  # Indicate the page to render next
            else:
                st.error("Invalid username or password.")

    # Signup tab
    with tab_signup:
        st.subheader("Signup")
        new_username_signup = st.text_input("New Username", key="signup_username")  # Unique key for signup username
        new_password_signup = st.text_input("New Password", type="password", key="signup_password")  # Unique key for signup password
        if st.button("Signup", key="signup_button"):  # Unique key for signup button
            if create_user(new_username_signup, new_password_signup):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username already exists.")

# Function to authenticate user
def authenticate_user(username, password):
    if os.path.exists(USER_DATA_FILE):
        users = pd.read_csv(USER_DATA_FILE)
        if not users.empty:
            user = users[(users["username"] == username) & (users["password"] == password)]
            if not user.empty:
                return True
    return False

# Function to create a new user
def create_user(username, password):
    if not os.path.exists(USER_DATA_FILE):
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        pd.DataFrame(columns=["username", "password"]).to_csv(USER_DATA_FILE, index=False)

    users = pd.read_csv(USER_DATA_FILE)
    if username in users["username"].values:
        return False
    new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
    new_user.to_csv(USER_DATA_FILE, mode="a", header=False, index=False)
    return True
