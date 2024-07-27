import streamlit as st
import yfinance as yf
import sqlite3
import pandas as pd
from settings import get_balance,set_balance
from utility import get_user_id
from streamlit_autorefresh import st_autorefresh


def get_stock_details(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period='1d', interval='1m')
    if not data.empty:
        current_price = data['Close'].iloc[-1]
        # info = ticker.info
        stock_name = ticker.info['shortName']
        return stock_name, current_price
    else:
        return None, None,

def update_portfolio(user_id,stock_name, ticker_symbol, quantity, price, type):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    
    
    c.execute("SELECT quantity, average_price FROM portfolio WHERE user_id = ? AND stock_symbol = ?", (user_id, ticker_symbol))
    result = c.fetchone()
    if type == "buy":
        if result:
            existing_quantity, average_price = result
            new_quantity = existing_quantity + quantity
            new_average_price = (average_price * existing_quantity + price * quantity) / new_quantity
            c.execute("UPDATE portfolio SET quantity = ?, average_price = ? WHERE user_id = ? AND stock_symbol = ?", 
                    (new_quantity, new_average_price, user_id, ticker_symbol))
        else:
            c.execute("INSERT INTO portfolio (user_id, stock_name, stock_symbol, quantity, average_price) VALUES (?, ?, ?, ?, ?)", 
                    (user_id, stock_name, ticker_symbol, quantity, price))
    else:
        if result:
            existing_quantity, average_price = result
            new_quantity = existing_quantity - quantity
            if(new_quantity<0):
                st.error("Cannot sell quantity more than you have in Portfolio.")
            else:
                new_average_price = (average_price * existing_quantity + price * quantity) / new_quantity
                c.execute("UPDATE portfolio SET quantity = ?, average_price = ? WHERE user_id = ? AND stock_symbol = ?", 
                    (new_quantity, new_average_price, user_id, ticker_symbol))
        else:
            st.error("Cannot sell stock which is not in Portfolio")
    conn.commit()
    conn.close()

def update_transactions(user_id, ticker_symbol, quantity, price,type):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, stock_symbol, transaction_type, quantity, price) VALUES (?,?,?,?,?)", 
              (user_id, ticker_symbol, type, quantity, price))

    conn.commit()
    conn.close()

def search():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    df = pd.read_csv('yfinData.csv')
    name = st.selectbox("#### Search for a stock:",df['name'], index=None, placeholder="Stock Name")
    st.write(" ")
    ticker =""
    if name:
        ticker = (df[df['name']==name].id).to_string(index=False).strip()
        st.write(ticker)
    if ticker:
        stock_name, price = get_stock_details(ticker)
        if price:
            st.write(f"#### Stock Details for {ticker}")
            st.write(f"**Current Price:** ₹ {price:.2f}")
            
            
            quantity = st.number_input("Enter quantity:", min_value=1, step=1, value=1)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                buy_clicked = st.button("Buy", use_container_width=True)
                
            with col2:
                sell_clicked = st.button("Sell", use_container_width=True)

            balance = get_balance(st.session_state.username)
            if buy_clicked:
                if 'logged_in' in st.session_state and st.session_state.logged_in:
                    type = "buy"
                    if(balance - quantity*price < 0):
                        st.error("Not enough Account Balance")
                    else:
                        user_id = get_user_id(st.session_state.username)
                        set_balance(st.session_state.username,balance - quantity*price)
                        update_portfolio(user_id, stock_name,ticker, quantity, price, type)
                        update_transactions(user_id, ticker, quantity, price, type)
                        st.write(f"Order submitted: {quantity} shares of {ticker} at ₹ {price:.2f}")
                else:
                    st.error("You need to log in to submit an order.")

            if sell_clicked:
                if 'logged_in' in st.session_state and st.session_state.logged_in:
                    type = "sell"
                    user_id = get_user_id(st.session_state.username)
                    set_balance(st.session_state.username,balance+quantity*price)
                    update_portfolio(user_id, ticker, quantity, price, type)
                    update_transactions(user_id, ticker, quantity, price, type)
                    st.write(f"Order submitted: {quantity} shares of {ticker} at ₹ {price:.2f}")
                else:
                    st.error("You need to log in to submit an order.")
        st_autorefresh(5000, key="price_refresh")
    


    