# test_import.py
import requests
import json
import pandas as pd
api_key = "V1RJ8K64TS1U7YBA"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&apikey=V1RJ8K64TS1U7YBA&symbol=IBM&outputsize=compact"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    with open("output.txt", "w") as f:
        f.write(json.dumps(data, indent=2))
    # Extract and transform the time series data
    time_series = data["Time Series (Daily)"]
    df = pd.DataFrame.from_dict(time_series, orient='index')
    df = df.reset_index().rename(columns={'index': 'Date'})
    df.columns = ['Date','Open', 'High', 'Low', 'Close', 'Volume']

    # Optional: Convert data types
    df = df.astype({
        'Date' : 'datetime64[ns]',
        'Open': float,
        'High': float,
        'Low': float,
        'Close': float,
        'Volume': int
    })

    # Sort by date descending
    df = df.sort_index(ascending=False)
    print(df[:10])
else:
    print(f"Error: {response.status_code} - {response.text}")