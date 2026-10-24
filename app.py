# app.py
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Stock Trading Demo", page_icon="📈", layout="wide")

st.title("📈 Stock Trading Demo")
st.caption("Demo only — prices, balances, and trades are fictional.")

# Dummy stock data
stocks = {
    "AAPL": {"name": "Apple", "price": 192.45},
    "MSFT": {"name": "Microsoft", "price": 425.22},
    "NVDA": {"name": "NVIDIA", "price": 875.30},
    "TSLA": {"name": "Tesla", "price": 172.63},
    "AMZN": {"name": "Amazon", "price": 183.15},
}

# Keep demo account state between Streamlit reruns
if "cash" not in st.session_state:
    st.session_state.cash = 10_000.00
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "history" not in st.session_state:
    st.session_state.history = []

# Add small random movement to make the dashboard feel live
for stock in stocks.values():
    stock["price"] = round(stock["price"] * random.uniform(0.995, 1.005), 2)

prices = {ticker: info["price"] for ticker, info in stocks.items()}

# Summary
portfolio_value = sum(
    shares * prices[ticker]
    for ticker, shares in st.session_state.portfolio.items()
)
col1, col2, col3 = st.columns(3)
col1.metric("Available cash", f"${st.session_state.cash:,.2f}")
col2.metric("Portfolio value", f"${portfolio_value:,.2f}")
col3.metric("Total account value", f"${st.session_state.cash + portfolio_value:,.2f}")

# Market table
st.subheader("Market")
market = pd.DataFrame(
    [
        {"Ticker": ticker, "Company": info["name"], "Price": info["price"]}
        for ticker, info in stocks.items()
    ]
)
st.dataframe(
    market,
    hide_index=True,
    use_container_width=True,
    column_config={"Price": st.column_config.NumberColumn(format="$%.2f")},
)

# Buy/sell form
st.subheader("Place a demo trade")
with st.form("trade_form"):
    ticker = st.selectbox("Stock", list(stocks.keys()))
    action = st.radio("Action", ["Buy", "Sell"], horizontal=True)
    shares = st.number_input("Shares", min_value=1, step=1)
    submitted = st.form_submit_button(f"{action} {ticker}")

if submitted:
    price = prices[ticker]
    current_shares = st.session_state.portfolio.get(ticker, 0)

    if action == "Buy":
        cost = shares * price
        if cost > st.session_state.cash:
            st.error("Not enough demo cash for this trade.")
        else:
            st.session_state.cash -= cost
            st.session_state.portfolio[ticker] = current_shares + shares
            st.session_state.history.append(
                {"Action": "Buy", "Ticker": ticker, "Shares": shares, "Price": price}
            )
            st.success(f"Bought {shares} shares of {ticker} at ${price:.2f}.")
            st.rerun()
    else:
        if shares > current_shares:
            st.error(f"You only own {current_shares} shares of {ticker}.")
        else:
            st.session_state.cash += shares * price
            remaining = current_shares - shares
            if remaining:
                st.session_state.portfolio[ticker] = remaining
            else:
                st.session_state.portfolio.pop(ticker, None)
            st.session_state.history.append(
                {"Action": "Sell", "Ticker": ticker, "Shares": shares, "Price": price}
            )
            st.success(f"Sold {shares} shares of {ticker} at ${price:.2f}.")
            st.rerun()

# Portfolio and trade history
left, right = st.columns(2)

with left:
    st.subheader("Your portfolio")
    if st.session_state.portfolio:
        holdings = pd.DataFrame(
            [
                {
                    "Ticker": ticker,
                    "Shares": shares,
                    "Market value": shares * prices[ticker],
                }
                for ticker, shares in st.session_state.portfolio.items()
            ]
        )
        st.dataframe(
            holdings,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Market value": st.column_config.NumberColumn(format="$%.2f")
            },
        )
    else:
        st.info("No holdings yet. Place a demo trade to get started.")

with right:
    st.subheader("Trade history")
    if st.session_state.history:
        st.dataframe(
            pd.DataFrame(st.session_state.history[::-1]),
            hide_index=True,
            use_container_width=True,
            column_config={"Price": st.column_config.NumberColumn(format="$%.2f")},
        )
    else:
        st.info("Your demo trades will appear here.")
