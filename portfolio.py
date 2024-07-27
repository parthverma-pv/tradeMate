import streamlit as st
import sqlite3
import yfinance as yf
import pandas as pd
from utility import get_user_id
from streamlit_autorefresh import st_autorefresh

def get_portfolio(user_id):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT stock_name, stock_symbol, quantity, average_price FROM portfolio WHERE user_id = ?", (user_id,))
    portfolio = c.fetchall()
    conn.close()
    return portfolio

def get_latest_price(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period='1d', interval='1m')
    if not data.empty:
        return data['Close'].iloc[-1]
    else:
        return None

def display_stats(curr_value, total_value):
    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        st.write(f"**Total Invested**")
        st.write(f"₹ {total_value:.2f}")

    with col2:
        st.write(f"**Total Current Value**")
        color = 'green' if curr_value >= total_value else 'red'
        st.markdown(f"<span style='color:{color}'>₹ {curr_value:.2f}</span>", unsafe_allow_html=True)
    
    with col3:
        st.write("**Profit/Loss**")
        color = 'green' if curr_value >= total_value else 'red'
        st.markdown(f"<span style='color:{color}'>₹ {curr_value-total_value:.2f}</span>",unsafe_allow_html=True)

    st.write(" ")
    st.write(" ")
    
def portfolio():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("You need to log in to access this page.")
        return

    user_id = get_user_id(st.session_state.username)
    portfolio_data = get_portfolio(user_id)
    
    if not portfolio_data:
        st.write("Your portfolio is empty.")
        return

    st.write("### Portfolio Summary")
    total_value = 0
    portfolio_df = pd.DataFrame(portfolio_data, columns=['Stock Name','Stock Symbol', 'Quantity', 'Average Price'])
    portfolio_df['LTP'] = portfolio_df['Stock Symbol'].apply(get_latest_price).round(2)
    portfolio_df['Invested Value'] = portfolio_df['Quantity'] * portfolio_df['Average Price']
    portfolio_df['Average Price'] = portfolio_df['Average Price'].round(2)

    portfolio_df['Current Value'] = portfolio_df['LTP'].astype(float) * portfolio_df['Quantity']
    portfolio_df['Profit/Loss'] = portfolio_df['Current Value'] - portfolio_df['Invested Value'] 
    
    portfolio_df['Invested Value'] = portfolio_df['Invested Value'].round(2)
    portfolio_df['Current Value'] = portfolio_df['Current Value'].round(2)
    portfolio_df['Profit/Loss'] = portfolio_df['Profit/Loss'].round(2)
    
    total_value = portfolio_df['Invested Value'].sum()
    curr_value = portfolio_df['Current Value'].sum()
    
    
    display_stats(curr_value,total_value)

    st.write("### Stocks")

    container = st.container()

    for index, row in portfolio_df.iterrows():
        with container:
            profit_loss_class = 'positive' if row['Profit/Loss'] >= 0 else 'negative'
            st.markdown(f"""
            <div class="stock-card">
                <div class="row1">
                    <div>Qty: {row['Quantity']} | Avg Price: ₹{row['Average Price']}</div>
                </div>
                <div class="row2">
                    {row['Stock Symbol']}
                    <div class="profit-loss {profit_loss_class}">
                        ₹{row['Profit/Loss']}
                    </div>
                </div>
                <div class="row3">
                    Invested: ₹{row['Invested Value']}
                    <div class="ltp">
                        LTP: ₹{row['LTP']}
                    </div>
                </div>
            </div>
            <hr>
            """, unsafe_allow_html=True)
    st_autorefresh(5000, key="portfolio_refresh")
