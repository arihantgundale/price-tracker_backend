import requests
import json
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- 1. IMPORT CORS

# --- Initialize the Flask Application ---
app = Flask(__name__)
CORS(app)  # <-- 2. ENABLE CORS FOR YOUR APP

# --- Configuration (Keep your keys and IDs here) ---
API_KEY = "579b464db66ec23bdd000001ee885840c47c49684f34c042ddbf9f24"
RESOURCE_ID = "35985678-0d79-46b4-9ed6-6f13308a1d24"
BASE_URL = "https://api.data.gov.in/resource/"


# --- API Endpoint ---
@app.route('/api/prices', methods=['GET'])
def get_market_prices():
    """
    This endpoint fetches market data based on query parameters.
    """
    # Get parameters from the request URL
    state = request.args.get('state')
    district = request.args.get('district')
    commodity = request.args.get('commodity')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Validate that date parameters are provided
    if not all([start_date_str, end_date_str]):
        return jsonify({"error": "Please provide both 'start_date' and 'end_date' in YYYY-MM-DD format."}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    if start_date > end_date:
        return jsonify({"error": "start_date cannot be after end_date."}), 400

    # Fetch data using the logic from our script
    all_records = []
    current_date = start_date
    while current_date <= end_date:
        query_date_str = current_date.strftime("%Y-%m-%d")

        url = (
            f"{BASE_URL}{RESOURCE_ID}?api-key={API_KEY}&format=json"
            f"&filters[Arrival_Date]={query_date_str}"
        )
        if state: url += f"&filters[State]={state}"
        if district: url += f"&filters[District]={district}"
        if commodity: url += f"&filters[Commodity]={commodity}"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if 'records' in data and data.get('records'):
                all_records.extend(data['records'])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {query_date_str}: {e}")

        current_date += timedelta(days=1)
        time.sleep(0.5)

    # Return the collected data as a JSON response
    return jsonify({
        "query_parameters": {
            "state": state,
            "district": district,
            "commodity": commodity,
            "start_date": start_date_str,
            "end_date": end_date_str
        },
        "record_count": len(all_records),
        "data": all_records
    })


# --- Main block to run the app ---
if __name__ == '__main__':
    app.run(debug=True)