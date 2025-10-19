import os
from flask import Flask, jsonify, request
from controller.sentiment_controller import sentiment_routes
from controller.stock_controller import stock_routes

# Create directories for outputs
os.makedirs('stock_charts', exist_ok=True)
os.makedirs('reports', exist_ok=True)
os.makedirs('stock_data', exist_ok=True)

# Initialize Flask app
app = Flask(__name__)

# Register routes
app.register_blueprint(sentiment_routes, url_prefix='/api/sentiment')
app.register_blueprint(stock_routes, url_prefix='/api/stocks')

@app.route('/')
def index():
    return jsonify({"status": "API is running"})

if __name__ == "__main__":
    app.run(debug=True)