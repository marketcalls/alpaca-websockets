# Real-Time Stock Quote Streaming

A real-time stock quote streaming application built with Flask and Alpaca's WebSocket API. This application provides live bid/ask prices and sizes for selected stocks (AAPL, NVDA, TSLA, META) with a modern, responsive UI.

## Features

- Real-time stock quote streaming using WebSocket
- Modern UI with Tailwind CSS and DaisyUI
- Live bid/ask prices and sizes
- Visual price change indicators
- Connection status monitoring
- Automatic WebSocket reconnection

## Prerequisites

- Python 3.8+
- Alpaca Markets API credentials
- Modern web browser with WebSocket support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/marketcalls/alpaca-websockets.git
cd alpaca-websockets
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.sample` to `.env`
   - Update `.env` with your Alpaca API credentials:
```bash
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_WSS_URL=wss://stream.data.alpaca.markets/v2/iex
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. The application will automatically connect to Alpaca's WebSocket feed and display real-time stock quotes.

## Project Structure

```
├── app.py              # Main Flask application
├── templates/
│   └── index.html     # Frontend template with WebSocket client
├── requirements.txt    # Python dependencies
├── .env.sample        # Sample environment variables
└── .gitignore         # Git ignore rules
```

## Dependencies

- Flask - Web framework
- Flask-SocketIO - WebSocket support for Flask
- websocket-client - WebSocket client for Alpaca API
- python-dotenv - Environment variable management
- Tailwind CSS - Utility-first CSS framework
- DaisyUI - Tailwind CSS component library

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Alpaca Markets](https://alpaca.markets/) for providing the market data API
- [Tailwind CSS](https://tailwindcss.com/) and [DaisyUI](https://daisyui.com/) for the UI components
