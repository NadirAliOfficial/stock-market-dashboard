import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit App Title
st.title("📈 Stock Market Data Analysis")

# Sidebar for stock selection
st.sidebar.header("Stock Selection")
stock_symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, TSLA, MSFT)", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

# Fetch stock data from Yahoo Finance
@st.cache_data
def get_stock_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)
    # Newer yfinance versions return MultiIndex columns even for a single ticker
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# Validate input
stock_symbol = stock_symbol.strip().upper()
if not stock_symbol:
    st.warning("Please enter a stock symbol.")
    st.stop()
if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

# Load data
data = get_stock_data(stock_symbol, start_date, end_date)
if data.empty:
    st.error(f"No data found for '{stock_symbol}' in the selected date range. Check the symbol and dates.")
    st.stop()

# Display Raw Data
st.subheader(f"Stock Data for {stock_symbol}")
st.write(data.tail())

# Calculate Moving Averages
data["SMA_50"] = data["Close"].rolling(window=50).mean()
data["SMA_200"] = data["Close"].rolling(window=200).mean()

# Calculate Daily Returns
data["Daily Return"] = data["Close"].pct_change()

# Calculate Volatility (Rolling Standard Deviation)
data["Volatility"] = data["Daily Return"].rolling(window=20).std()

# Stock Price Chart
st.subheader("📊 Stock Price Chart")
plt.figure(figsize=(12, 5))
plt.plot(data["Close"], label="Close Price", color="blue")
plt.plot(data["SMA_50"], label="50-Day SMA", linestyle="dashed", color="green")
plt.plot(data["SMA_200"], label="200-Day SMA", linestyle="dashed", color="red")
plt.legend()
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.title(f"{stock_symbol} Stock Price Trend")
st.pyplot(plt)

# Returns & Volatility Visualization
st.subheader("📉 Daily Returns & Volatility")

fig, ax = plt.subplots(2, 1, figsize=(12, 8))
sns.histplot(data["Daily Return"].dropna(), bins=50, kde=True, ax=ax[0], color="purple")
ax[0].set_title("Daily Returns Distribution")

sns.lineplot(x=data.index, y=data["Volatility"], ax=ax[1], color="red")
ax[1].set_title("Stock Volatility Over Time")

st.pyplot(fig)

# Statistical Summary
st.subheader("📊 Statistical Summary")
st.write(data.describe())

# Footer
st.caption("📌 Data source: Yahoo Finance | Built with Streamlit")

