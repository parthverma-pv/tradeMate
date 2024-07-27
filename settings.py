import streamlit as st
import sqlite3
import time
from utility import get_user_id

def get_balance(username):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT wallet FROM users WHERE user_id = ?", (get_user_id(username),))
    balance = c.fetchone()
    conn.close()
    return balance[0]

def set_balance(username, amount):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE users SET wallet = ? where user_id = ?", (amount,get_user_id(username)))
    conn.commit()
    conn.close()  

def settings():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("You need to log in to access this page.")
        return

    st.subheader("Account Balance")
    balance = get_balance(st.session_state.username)
    st.write(f"Current Balance:  ₹ {balance:.2f}")
    amount = st.number_input("Add Money to account:", min_value=0.0, step=100.0, format="%f")

    if st.button("Add to Account", use_container_width=True):
        set_balance(st.session_state.username, get_balance(st.session_state.username) + amount)
        st.success("Money successfully added to account.")
        time.sleep(1)
        st.rerun()
        
