# app.py
import random
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Stock Trading Demo", page_icon="📈", layout="wide")

# Bright, colorful dashboard styling
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f3f7ff 0%, #f8f3ff 48%, #fff7ed 100%);
    color: #18213b;
}
.block-container { padding-top: 2rem; padding-bottom: 3rem; }
.hero {
    padding: 1.8rem 2rem;
    border-radius: 22px;
    color: white;
    background: linear-gradient(115deg, #5b5ce2, #9b4de0 55%, #ed5ab7);
    box-shadow: 0 12px 30px #6c4de033;
    margin-bottom: 1.3rem;
}
.hero h1 { color: white; margin: 0; font-size: 2.5rem; }
.hero p { color: #f3eaff; margin: .45rem 0 0; font-size: 1.05rem; }
.stock-card {
    background: white;
    border: 1px solid #e7e5ff;
    border-radius: 16px;
    padding: 1rem 1.1rem;
    box-shadow: 0 5px 18px #4b42a510;
    min-height: 118px;
}
.stock-ticker { color: #6b5ce7; font-size: .85rem; font-weight: 800; letter-spacing: .08em; }
.stock-name { color: #59627a; font-size: .9rem; margin-top: .2rem; }
.stock-price { color: #18213b; font-weight: 800; font-size: 1.45rem; margin-top: .35rem; }
section[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e7e5ff;
    border-radius: 16px;
    padding: 1rem 1.1rem;
    box-shadow: 0 5px 18px #4b42a510;
}
section[data-testid="stMetric"] label { color: #6b5ce7 !important; }
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(90deg, #5b5ce2, #a34de0);
    color: white;
    border: 0;
    border-radius: 10px;
    font-weight: 700;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    color: white; border: 0; filter: brightness(1.08);
}
[data-testid="stDataFrame"] { border: 1px solid #e7e5ff; border-radius: 14px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>📈 Stock Trading Demo</h1>
  <p>Explore the market, build a portfolio, and practice trading with fictional money.</p>
</div>
""", unsafe_allow_html=True)
st.caption("🧪 Demo only — all prices, balances, and trades are fictional.")

# Fictional market data
stocks = {
    "AAPL": {"name": "Apple", "price": 192.45, "color": "🍎"},
    "MSFT": {"name": "Microsoft", "price": 425.22, "color": "🪟"},
    "NVDA": {"name": "NVIDIA", "price": 875.30, "color": "💚"},
    "TSLA": {"name": "Tesla", "price": 172.63, "color": "🚗"},
    "AMZN": {"name": "Amazon", "price": 183.15, "color": "📦"},
}

# Keep the demo account between Streamlit reruns
if "cash" not in st.session_state:
    st.session_state.cash = 10_000.00
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
if "history" not in st.session_state:
    st.session_state.history = []

# Small random movement makes the fictional market feel active
for stock in stocks.values():
    stock["price"] = round(stock["price"] * random.uniform(0.995, 1.005), 2)
prices = {ticker: info["price"] for ticker, info in stocks.items()}

portfolio_value = sum(
    shares * prices[ticker]
    for ticker, shares in st.session_state.portfolio.items()
)

st.subheader("💼 Account overview")
col1, col2, col3 = st.columns(3)
col1.metric("💵 Available cash", f"${st.session_state.cash:,.2f}")
col2.metric("🎯 Portfolio value", f"${portfolio_value:,.2f}")
col3.metric("✨ Total account value", f"${st.session_state.cash + portfolio_value:,.2f}")

st.subheader("🌈 Market watch")
card_columns = st.columns(len(stocks))
for column, (ticker, info) in zip(card_columns, stocks.items()):
    column.markdown(
        f"""<div class="stock-card">
        <div class="stock-ticker">{info['color']} {ticker}</div>
        <div class="stock-name">{info['name']}</div>
        <div class="stock-price">${info['price']:,.2f}</div>
        </div>""",
        unsafe_allow_html=True,
    )

with st.expander("📋 View market table", expanded=False):
    market = pd.DataFrame([
        {"Ticker": ticker, "Company": info["name"], "Price": info["price"]}
        for ticker, info in stocks.items()
    ])
    st.dataframe(
        market,
        hide_index=True,
        use_container_width=True,
        column_config={"Price": st.column_config.NumberColumn(format="$%.2f")},
    )

st.subheader("🛒 Place a demo trade")
with st.form("trade_form"):
    ticker = st.selectbox("Choose a stock", list(stocks.keys()), format_func=lambda symbol: f"{symbol} — {stocks[symbol]['name']}")
    action = st.radio("Trade type", ["Buy", "Sell"], horizontal=True)
    shares = st.number_input("Number of shares", min_value=1, step=1)
    submitted = st.form_submit_button(f"{action} {ticker}", use_container_width=True)

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
            st.session_state.history.append({"Action": "Buy", "Ticker": ticker, "Shares": shares, "Price": price})
            st.success(f"✅ Bought {shares} shares of {ticker} at ${price:.2f}.")
            st.rerun()
    elif shares > current_shares:
        st.error(f"You only own {current_shares} shares of {ticker}.")
    else:
        st.session_state.cash += shares * price
        remaining = current_shares - shares
        if remaining:
            st.session_state.portfolio[ticker] = remaining
        else:
            st.session_state.portfolio.pop(ticker, None)
        st.session_state.history.append({"Action": "Sell", "Ticker": ticker, "Shares": shares, "Price": price})
        st.success(f"✅ Sold {shares} shares of {ticker} at ${price:.2f}.")
        st.rerun()

left, right = st.columns(2)
with left:
    st.subheader("📊 Your portfolio")
    if st.session_state.portfolio:
        holdings = pd.DataFrame([
            {"Ticker": ticker, "Shares": shares, "Market value": shares * prices[ticker]}
            for ticker, shares in st.session_state.portfolio.items()
        ])
        st.dataframe(
            holdings,
            hide_index=True,
            use_container_width=True,
            column_config={"Market value": st.column_config.NumberColumn(format="$%.2f")},
        )
    else:
        st.info("Your portfolio is empty. Place a demo trade to get started! ✨")

with right:
    st.subheader("🧾 Recent trades")
    if st.session_state.history:
        st.dataframe(
            pd.DataFrame(st.session_state.history[::-1]),
            hide_index=True,
            use_container_width=True,
            column_config={"Price": st.column_config.NumberColumn(format="$%.2f")},
        )
    else:
        st.info("Your demo trades will appear here. 🪄")
