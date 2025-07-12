import requests
import json
import pandas as pd
api_key = "V1RJ8K64TS1U7YBA"  # V1RJ8K64TS1U7YBA # Replace with your actual API key


# Base function to hit Alpha Vantage API
def fetch_alpha_vantage(function, symbol=None, interval=None, outputsize="compact", keywords=None):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": function,
        "apikey": api_key
    }
    if symbol:
        params["symbol"] = symbol
    if interval:
        params["interval"] = interval
    if outputsize:
        params["outputsize"] = outputsize
    if keywords:
        params["keywords"] = keywords

    try:
        print("🔗 Fetching data from Alpha Vantage...")
        #print("url:", base_url, "params:", params)
        response = requests.get(base_url, params=params)
        print("urlFired:", response.url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ API Error: {e}")
        return None

def parse_time_series(data, time_key):
    time_series = data.get(time_key, {})
    if not time_series:
        print("⚠️ No time series data found.")
        return None

    df = pd.DataFrame.from_dict(time_series, orient='index')
    df.reset_index(inplace=True)
    df = df.rename(columns={
        'index': 'Date',
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close',
        '5. volume': 'Volume'
    })

    df['Date'] = pd.to_datetime(df['Date'])
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df.sort_values('Date', ascending=False)

def get_intraday(symbol, interval): 
    data = fetch_alpha_vantage("TIME_SERIES_INTRADAY", symbol=symbol, interval=interval)
    return parse_time_series(data, f"Time Series ({interval})")

def get_weekly(symbol):
    data = fetch_alpha_vantage("TIME_SERIES_WEEKLY", symbol=symbol)
    return parse_time_series(data, "Weekly Time Series")

def get_monthly(symbol):
    data = fetch_alpha_vantage("TIME_SERIES_MONTHLY", symbol=symbol)
    return parse_time_series(data, "Monthly Time Series")

def get_global_quote(symbol):
    data = fetch_alpha_vantage("GLOBAL_QUOTE", symbol=symbol)
    return data.get("Global Quote", {})


def search_symbol(keywords):
    data = fetch_alpha_vantage("SYMBOL_SEARCH", keywords=keywords)
    return pd.DataFrame(data.get("bestMatches", []))

def get_market_status():
    data = fetch_alpha_vantage("MARKET_STATUS")
    return data.get("market_status", data)  # fallback to entire response

def requestApi(Symbol,interval):
    # Get intraday 5min data for IBM
    df_intraday = get_intraday(Symbol,interval) # 1min, 5min, 15min, 30min, 60min
    #print(df_intraday.head())

    # Weekly
    df_weekly = get_weekly(Symbol)

    # Monthly
    df_monthly = get_monthly(Symbol)

    # Global quote
    quote = get_global_quote(Symbol)
    #print("Price:", quote.get("05. price"))

    # Symbol search
    search_results = search_symbol(Symbol)
    #print(search_results.head())

    # Market status
    status = get_market_status()
    #print(status)
    return {
        "intraday": df_intraday,
        "weekly": df_weekly,
        "monthly": df_monthly,
        "global_quote": quote,
        "search_results": search_results,
        "market_status": status
    }
def df_to_dict(df):
    if df is not None:
        df = df.copy()
        # Convert all datetime columns to string
        for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
            df[col] = df[col].astype(str)
        return df.to_dict()
    return None
data = requestApi("IBM","5min")
serializable_data = {
    "intraday": df_to_dict(data["intraday"]),
    "weekly": df_to_dict(data["weekly"]),
    "monthly": df_to_dict(data["monthly"]),
    "global_quote": data["global_quote"],
    "search_results": df_to_dict(data["search_results"]) if isinstance(data["search_results"], pd.DataFrame) and not data["search_results"].empty else None,
    "market_status": data["market_status"]
}
with open("output.txt", "w") as f:
        f.write(json.dumps(serializable_data, indent=2))
"""# Example usage:
def requestApi():
    return {'request': {'type': 'City', 'query': 'New York, United States of America', 'language': 'en', 'unit': 'm'}, 'location': {'name': 'New York', 'country': 'United States of America', 'region': 'New York', 'lat': '40.714', 'lon': '-74.006', 'timezone_id': 'America/New_York', 'localtime': '2025-06-21 07:44', 'localtime_epoch': 1750491840, 'utc_offset': '-4.0'}, 'current': {'observation_time': '11:44 AM', 'temperature': 23, 'weather_code': 116, 'weather_icons': ['https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png'], 'weather_descriptions': ['Partly cloudy'], 'astro': {'sunrise': '05:25 AM', 'sunset': '08:31 PM', 'moonrise': '02:00 AM', 'moonset': '04:33 PM', 'moon_phase': 'Waning Crescent', 'moon_illumination': 26}, 'air_quality': {'co': '492.1', 'no2': '20.165', 'o3': '136', 'so2': '12.025', 'pm2_5': '22.94', 'pm10': '24.05', 'us-epa-index': '2', 'gb-defra-index': '2'}, 'wind_speed': 8, 'wind_degree': 313, 'wind_dir': 'NW', 'pressure': 1020, 'precip': 0, 'humidity': 61, 'cloudcover': 50, 'feelslike': 25, 'uv_index': 0, 'visibility': 16, 'is_day': 'yes'}}
requestApi()
"""
