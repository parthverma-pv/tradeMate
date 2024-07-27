import streamlit as st
import sqlite3
import bcrypt
import time
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def register():
    st.subheader("Register")
    fname = st.text_input("First Name")
    lname = st.text_input("Last Name")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    email = st.text_input("Email")
    
    if st.button("Register", use_container_width=True):
        if fname and lname and username and password and email:
            conn = sqlite3.connect('users.db', check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
            result = c.fetchone()
            if result:
                st.error("Username or email already exists. Please choose a different one.")
            else:
                password = hash_password(password)
                c.execute("INSERT INTO users (fname,lname,username,password,email) values (?,?,?,?,?)",(fname,lname,username,password,email))
                conn.commit()
                conn.close()
                st.success("You have registered successfully!")
                time.sleep(1)
        else:
            st.error("Please fill all required details.")

            
