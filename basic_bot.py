import logging
import time
from binance.client import Client
from binance.enums import *

# ------------------------------
# Logging Setup
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", mode='w'),  # overwrite log each run
        logging.StreamHandler()
    ]
)

# ------------------------------
# BasicBot Class
# ------------------------------
class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            self.client.ping()
            logging.info("✅ Binance Testnet client initialized successfully")
        except Exception as e:
            logging.error(f"❌ Error initializing client: {e}")
            raise

    # ------------------------------
    # Get Futures Account Balance
    # ------------------------------
    def get_balance(self):
        try:
            balance = self.client.futures_account_balance()
            logging.info("✅ Balance fetched successfully")
            for asset in balance:
                logging.info(f"{asset['asset']}: {asset['balance']}")
            return balance
        except Exception as e:
            logging.error(f"❌ Error fetching balance: {e}")
            return None

    # ------------------------------
    # Check if sufficient balance exists
    # ------------------------------
    def has_sufficient_balance(self, symbol, quantity):
        balance_info = self.get_balance()
        if not balance_info:
            return False

        # Get USDT balance
        usdt_balance = 0
        for asset in balance_info:
            if asset['asset'] == 'USDT':
                usdt_balance = float(asset['balance'])
                break

        # Get current price
        try:
            price_data = self.client.futures_symbol_ticker(symbol=symbol)
            current_price = float(price_data['price'])
        except Exception as e:
            logging.error(f"❌ Error fetching current price: {e}")
            return False

        required_amount = current_price * quantity
        if usdt_balance < required_amount:
            logging.warning(f"⚠️ Insufficient USDT balance: {usdt_balance} < {required_amount}")
            return False
        return True

    # ------------------------------
    # Place Order with Retry
    # ------------------------------
    def place_order(self, symbol, side, order_type, quantity, price=None, retries=3):
        if order_type == ORDER_TYPE_MARKET and not self.has_sufficient_balance(symbol, quantity):
            logging.error("❌ Not enough balance to place market order.")
            return None

        for attempt in range(retries):
            try:
                if order_type == ORDER_TYPE_MARKET:
                    order = self.client.futures_create_order(
                        symbol=symbol,
                        side=side,
                        type=ORDER_TYPE_MARKET,
                        quantity=quantity
                    )
                elif order_type == ORDER_TYPE_LIMIT:
                    if price is None:
                        raise ValueError("Price must be specified for LIMIT order")
                    order = self.client.futures_create_order(
                        symbol=symbol,
                        side=side,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=quantity,
                        price=price
                    )
                logging.info(f"✅ Order placed successfully: {order['orderId']}")
                return order
            except Exception as e:
                logging.error(f"❌ Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        logging.error("❌ All attempts to place order failed.")
        return None

# ------------------------------
# Example Usage
# ------------------------------
if __name__ == "__main__":
    # Replace with your Binance Testnet API keys
    API_KEY = "YOUR_API_KEY"
    API_SECRET = "YOUR_API_SECRET"

    bot = BasicBot(api_key=API_KEY, api_secret=API_SECRET, testnet=True)

    # Get account balance
    bot.get_balance()

    # Place a market buy order for BTCUSDT
    bot.place_order(symbol="BTCUSDT", side=SIDE_BUY, order_type=ORDER_TYPE_MARKET, quantity=0.01)

    # Example: Place a limit sell order
    # bot.place_order(symbol="BTCUSDT", side=SIDE_SELL, order_type=ORDER_TYPE_LIMIT, quantity=0.01, price=50000)
