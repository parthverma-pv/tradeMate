import streamlit as st
import sqlite3
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def login():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.subheader("Login")
    username = st.text_input("Username",key="input_username")
    password = st.text_input("Password", type='password',key="input password")
    
    
    if st.button("Login", use_container_width=True):
        if username and password:
            conn = sqlite3.connect('users.db', check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT user_id, fname, password FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            conn.close()
            if user and check_password(password, user[2].encode('utf-8')):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.first_name = user[1]
                st.rerun()
            else:
                st.error("Invalid username or password")
        else:
            st.error("Please enter a username and password")

    
