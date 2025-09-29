import streamlit as st
from basic_bot import BasicBot
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT

st.title("Binance Futures Testnet Trading Bot")

# ------------------------------
# API Key Input
# ------------------------------
st.sidebar.header("API Configuration")
api_key = st.sidebar.text_input("API Key")
api_secret = st.sidebar.text_input("API Secret", type="password")

if api_key and api_secret:
    bot = BasicBot(api_key=api_key, api_secret=api_secret, testnet=True)
    
    # ------------------------------
    # Show Balance
    # ------------------------------
    if st.button("Get Balance"):
        balance = bot.get_balance()
        st.write(balance)

    # ------------------------------
    # Place Order
    # ------------------------------
    st.subheader("Place Order")
    symbol = st.text_input("Symbol (e.g., BTCUSDT)", value="BTCUSDT")
    side = st.selectbox("Side", ["BUY", "SELL"])
    order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
    quantity = st.number_input("Quantity", min_value=0.0001, value=0.01, step=0.01)
    price = None
    if order_type == "LIMIT":
        price = st.number_input("Price", min_value=0.0, value=0.0, step=0.01)
    
    if st.button("Place Order"):
        side_enum = SIDE_BUY if side == "BUY" else SIDE_SELL
        order_type_enum = ORDER_TYPE_MARKET if order_type=="MARKET" else ORDER_TYPE_LIMIT
        order = bot.place_order(symbol=symbol, side=side_enum, order_type=order_type_enum, quantity=quantity, price=price)
        st.write(order)
else:
    st.warning("Enter your API Key & Secret in the sidebar.")
