from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import websocket
import json
import threading
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)

# Alpaca WebSocket settings
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
ALPACA_WSS_URL = os.getenv('ALPACA_WSS_URL')

# Global variables
ws_app = None
AVAILABLE_SYMBOLS = ["AAPL", "MSFT", "NVDA", "TSLA"]
active_subscriptions = {"AAPL"}  # Set of currently subscribed symbols

def on_message(ws, message):
    """Handles incoming WebSocket messages from Alpaca."""
    try:
        data = json.loads(message)
        print(f"\nReceived from Alpaca: {json.dumps(data, indent=2)}")

        if isinstance(data, list):
            for item in data:
                if item.get('T') == 'q':  # Quote data
                    print(f"\nEmitting quote for {item['S']}: Bid={item.get('bp')} Ask={item.get('ap')}")
                    socketio.emit('market_data', item, namespace='/')
                elif item.get('T') == 'error':
                    print(f"Error from Alpaca: {item}")
                elif item.get('T') == 'success':
                    print(f"Success message from Alpaca: {item}")
        elif isinstance(data, dict):
            print(f"Received single message: {data}")
            if data.get('T') == 'q':
                socketio.emit('market_data', data, namespace='/')
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        print(f"Raw message: {message}")

def on_error(ws, error):
    print(f"Alpaca WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Alpaca WebSocket closed: {close_status_code} - {close_msg}")
    time.sleep(5)  # Wait before reconnecting
    connect_alpaca()

def on_open(ws):
    """Authenticate and subscribe to real-time stock quotes."""
    print("\nAlpaca WebSocket connected! Authenticating...")
    auth_data = {
        "action": "auth",
        "key": ALPACA_API_KEY,
        "secret": ALPACA_SECRET_KEY
    }
    ws.send(json.dumps(auth_data))
    print("Authentication data sent")

    # Subscribe after a short delay to ensure auth is processed
    def delayed_subscribe():
        time.sleep(1)
        if active_subscriptions:  # Only subscribe if there are active subscriptions
            subscribe_data = {
                "action": "subscribe",
                "quotes": list(active_subscriptions)
            }
            print(f"\nSubscribing to quotes: {json.dumps(subscribe_data, indent=2)}")
            ws.send(json.dumps(subscribe_data))
            print("Subscription data sent")

    threading.Thread(target=delayed_subscribe).start()

def connect_alpaca():
    """Create and connect to Alpaca WebSocket."""
    global ws_app
    websocket.enableTrace(True)
    ws_app = websocket.WebSocketApp(
        ALPACA_WSS_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws_app.run_forever()

def update_subscriptions(symbols_to_subscribe=None, symbols_to_unsubscribe=None):
    """Update websocket subscriptions."""
    if not ws_app:
        return False
    
    if symbols_to_subscribe:
        subscribe_data = {
            "action": "subscribe",
            "quotes": list(symbols_to_subscribe)
        }
        ws_app.send(json.dumps(subscribe_data))
        
    if symbols_to_unsubscribe:
        unsubscribe_data = {
            "action": "unsubscribe",
            "quotes": list(symbols_to_unsubscribe)
        }
        ws_app.send(json.dumps(unsubscribe_data))
    
    return True

@app.route("/")
def index():
    """Render the frontend."""
    return render_template("index.html", 
                         available_symbols=AVAILABLE_SYMBOLS,
                         active_subscriptions=list(active_subscriptions))

@socketio.on('connect')
def handle_connect():
    print(f"\nClient connected! sid: {request.sid}")
    socketio.emit('connection_response', {
        'status': 'connected',
        'active_subscriptions': list(active_subscriptions)
    }, room=request.sid)

@socketio.on('subscribe')
def handle_subscribe(data):
    symbol = data.get('symbol')
    if symbol and symbol in AVAILABLE_SYMBOLS and symbol not in active_subscriptions:
        active_subscriptions.add(symbol)
        success = update_subscriptions(symbols_to_subscribe={symbol})
        socketio.emit('subscription_update', {
            'action': 'subscribe',
            'symbol': symbol,
            'success': success,
            'active_subscriptions': list(active_subscriptions)
        })

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    symbol = data.get('symbol')
    if symbol and symbol in active_subscriptions:
        active_subscriptions.remove(symbol)
        success = update_subscriptions(symbols_to_unsubscribe={symbol})
        socketio.emit('subscription_update', {
            'action': 'unsubscribe',
            'symbol': symbol,
            'success': success,
            'active_subscriptions': list(active_subscriptions)
        })

@socketio.on('disconnect')
def handle_disconnect():
    print(f"\nClient disconnected! sid: {request.sid}")

if __name__ == "__main__":
    # Start Alpaca WebSocket connection in a separate thread
    alpaca_thread = threading.Thread(target=connect_alpaca, daemon=True)
    alpaca_thread.start()
    
    # Start Flask app
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)