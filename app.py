import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="PocketAlpha Pro", layout="wide")

# --- PREMIUM UI STYLE ---
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0d1117, #161b22);
    color: #e6edf3;
}

h1 {
    font-size: 42px !important;
    font-weight: 700;
    background: -webkit-linear-gradient(#00ff88, #00c3ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

.stButton>button {
    background: linear-gradient(90deg, #00ff88, #00c3ff);
    color: black;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- LOAD NIFTY 500 ---
@st.cache_data
def get_nifty_500_list():
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    df = pd.read_csv(url)
    df['Ticker'] = df['Symbol'] + ".NS"
    return df[['Company Name', 'Symbol', 'Industry', 'Ticker']]

# --- INTELLIGENCE ENGINE ---
def get_live_intelligence(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period="1y")

    if hist.empty:
        return None

    current_price = hist['Close'].iloc[-1]

    # Moving Average Signal
    ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
    signal = "🟢 BUY ZONE" if current_price < ma_50 else "🟡 HOLD / WAIT"

    # Volatility (Annualized)
    daily_returns = hist['Close'].pct_change()
    volatility = daily_returns.std() * np.sqrt(252)

    if volatility < 0.25:
        risk = "🟢 Low Risk"
    elif volatility < 0.40:
        risk = "🟡 Moderate Risk"
    else:
        risk = "🔴 High Risk"

    # Consistency Score
    monthly_returns = hist['Close'].resample('M').last().pct_change()
    positive_months = (monthly_returns > 0).sum()
    consistency_score = int((positive_months / 12) * 100)

    # CAGR
    start_price = hist['Close'].iloc[0]
    end_price = hist['Close'].iloc[-1]
    cagr = (end_price / start_price) - 1

    return current_price, risk, signal, hist, consistency_score, cagr

# --- UI ---
st.title("📊 PocketAlpha Pro – Student Micro Investment Intelligence")
st.markdown("Helping students invest small amounts intelligently using real-time Nifty 500 data.")

# --- SIDEBAR SEARCH ---
nifty500 = get_nifty_500_list()

st.sidebar.header("🔍 Market Search")
search_query = st.sidebar.text_input("Search Company or Industry", "")

filtered_df = nifty500[
    nifty500['Company Name'].str.contains(search_query, case=False) |
    nifty500['Industry'].str.contains(search_query, case=False)
]

st.write(f"Displaying **{len(filtered_df)}** stocks from the Nifty 500 universe.")
st.dataframe(filtered_df[['Company Name', 'Industry', 'Symbol']], use_container_width=True)

st.divider()

# --- STOCK ANALYSIS ---
st.header("🎯 Real-Time Stock Intelligence")

selected_symbol = st.selectbox(
    "Select a stock to analyze",
    filtered_df['Ticker'].tolist()
)

if selected_symbol:

    with st.spinner(f"Analyzing {selected_symbol}..."):
        result = get_live_intelligence(selected_symbol)

    if result:

        price, risk, signal, history, consistency, cagr = result

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Live Price", f"₹{price:,.2f}")
        col2.metric("Risk Meter", risk)
        col3.metric("AI Signal", signal)
        col4.metric("Consistency Score", f"{consistency}/100")

        # --- PRICE CHART ---
        st.subheader("📈 1-Year Price Trend")
        st.line_chart(history['Close'])

        # --- SIP SIMULATOR ---
        st.subheader("🚀 Student SIP Growth Simulator")

        monthly_budget = st.number_input("Monthly Investment (₹)", value=500)
        years = st.slider("Investment Duration (Years)", 1, 10, 2)

        r = cagr / 12
        n = years * 12

        if r > 0:
            fv = monthly_budget * (((1 + r)**n - 1) / r)
        else:
            fv = monthly_budget * n

        units = monthly_budget / price

        st.success(
            f"Projected Portfolio Value: **₹{fv:,.2f}**\n\n"
            f"Monthly Units Purchased: **{units:.3f} shares**\n\n"
            f"Historical CAGR Used: **{cagr*100:.2f}%**"
        )

        # --- DISCIPLINE SCORE ---
        discipline_score = 50

        if years >= 5:
            discipline_score += 20
        elif years >= 3:
            discipline_score += 10

        if monthly_budget >= 1000:
            discipline_score += 15
        elif monthly_budget >= 500:
            discipline_score += 10

        if "Low" in risk:
            discipline_score += 15

        discipline_score = min(discipline_score, 100)

        st.subheader("🧠 Investor Discipline Score")
        st.progress(discipline_score / 100)

        if discipline_score > 80:
            st.success(f"Elite Investor Mindset 🔥 | Score: {discipline_score}/100")
        elif discipline_score > 60:
            st.info(f"Strong Discipline | Score: {discipline_score}/100")
        else:
            st.warning(f"Needs More Consistency | Score: {discipline_score}/100")

        # --- DISCLAIMER ---
        st.warning(
            "⚠ This is an educational simulation based on historical data. "
            "It is NOT financial advice."
        )

    else:
        st.error("Unable to fetch data. Try another stock.")