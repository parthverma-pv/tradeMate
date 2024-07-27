import streamlit as st
import sqlite3
from login import login
from portfolio import portfolio
from search import search
from settings import settings
from register import register

def createTables():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        fname TEXT NOT NULL,
        lname TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        wallet DECIMAL(10,2) NOT NULL DEFAULT 0.00,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stock_symbol TEXT NOT NULL,
        transaction_type TEXT CHECK(transaction_type IN ('buy', 'sell')) NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );          
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stock_name TEXT NOT NULL,
        stock_symbol TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        average_price REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        UNIQUE(user_id, stock_symbol)
    );
    ''')
    conn.commit()
    conn.close()
    
def main():
    createTables()
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.title("TradeMate")
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        menu = ["Portfolio", "Search", "Wallet", "Logout"]
        tab1, tab2, tab3, tab4 = st.tabs(menu)
        with tab1:
            portfolio()
        with tab2:
            search()
        with tab3:
            settings()
        with tab4:
            if st.button("Logout",use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.starting_capital = None
                st.rerun()

    else:
        menu = ["Login","Register"]
        tab1, tab2 =  st.tabs(menu)
        with tab1:
            login()
        with tab2:
            register()

if __name__ == '__main__':
    main()
