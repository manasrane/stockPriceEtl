import psycopg2
from datetime import datetime
from stockRequestApi import requestApi
from dateutil.parser import parse as date_parse
def connect_to_db():
    try:
        print("Connecting to the PostgreSQL database...")
        return psycopg2.connect(
            host="db",
            port=5432,
            dbname="db",
            user="db_user",
            password="db_password")
    except psycopg2.Error as e:
        print(f"DB connection error: {e}")
        raise

def create_table(conn, schema, table_name, cols_dtypes):
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")

        columns_sql = ",\n    ".join([f"{col} {dtype}" for col, dtype in cols_dtypes.items()])
        full_query = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
            id SERIAL PRIMARY KEY,
            {columns_sql},
            inserted_at TIMESTAMP DEFAULT NOW()
        );
        """
        cursor.execute(full_query)
        conn.commit()
        print(f"✅ Created table {schema}.{table_name}")
    except psycopg2.Error as e:
        print(f"❌ Failed to create table {schema}.{table_name}: {e}")
        raise

def insert_records(conn, schema, table_name, data_dict):
    try:
        cursor = conn.cursor()
        columns = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = list(data_dict.values())

        query = f"""
        INSERT INTO {schema}.{table_name} ({columns}, inserted_at)
        VALUES ({placeholders}, NOW());
        """
        cursor.execute(query, values)
        conn.commit()
        print(f"✅ Inserted record into {schema}.{table_name}")
    except psycopg2.Error as e:
        print(f"❌ Failed to insert into {schema}.{table_name}: {e}")
        raise
    
def clean_timeseries_section(section: dict) -> list[dict]:
    cleaned = []
    for timestamp, data in section.items():
        row = {"timestamp": timestamp}
        for k, v in data.items():
            label = k.split(". ")[1]  # e.g. "1. open" -> "open"
            try:
                row[label] = float(v.replace(",", ""))  # handle floats
            except ValueError:
                row[label] = v
        cleaned.append(row)
    return cleaned

def infer_data_types(record):
    dtypes = {}
    for key, value in record.items():
        if isinstance(value, float):
            dtypes[key] = "FLOAT"
        elif isinstance(value, int):
            dtypes[key] = "INT"
        elif isinstance(value, str):
            try:
                date_parse(value)
                dtypes[key] = "TIMESTAMP"
            except (ValueError, OverflowError):
                try:
                    float(value)
                    dtypes[key] = "FLOAT"
                except ValueError:
                    dtypes[key] = "TEXT"
        else:
            dtypes[key] = "TEXT"
    return dtypes

def flatten_time_series(data, section):
    flat_records = []
    for timestamp, values in data.items():
        flat_record = {"timestamp": timestamp}
        for key, val in values.items():
            col = key.split(". ")[1] if ". " in key else key
            flat_record[col.lower().replace(" ", "_")] = float(val) if val.replace('.', '', 1).isdigit() else val
        flat_records.append(flat_record)
    return flat_records

def main(default_args):
    try:
        conn = connect_to_db()
#        if not all([schema, symbol, interval]):
#            raise ValueError("Missing schema, symbol, or interval in default_args")
        symbol = default_args.get('tableInfo', {}).get("symbol")
        interval = default_args.get('tableInfo', {}).get("interval")
        schema = default_args.get('tableInfo', {}).get("schema")
        data = requestApi(symbol, interval)
        print(f"📊 Fetched data for {symbol} with interval {interval} for schema: {schema}")
        # INTRADAY
        intraday_records = clean_timeseries_section(data.get("intraday", {}))
        if intraday_records: 
            cols_dtypes = infer_data_types(intraday_records[0])
            create_table(conn, schema, "stock_intraday", cols_dtypes)
            for record in intraday_records:
                insert_records(conn, schema, "stock_intraday", record)

        # WEEKLY
        weekly_records = clean_timeseries_section(data.get("weekly", {}))
        if weekly_records:
            cols_dtypes = infer_data_types(weekly_records[0])
            create_table(conn, schema, "stock_weekly", cols_dtypes)
            for record in weekly_records:
                insert_records(conn, schema, "stock_weekly", record)

        # MONTHLY
        monthly_records = clean_timeseries_section(data.get("monthly", {}))
        if monthly_records:
            cols_dtypes = infer_data_types(monthly_records[0])
            create_table(conn, schema, "stock_monthly", cols_dtypes)
            for record in monthly_records:
                insert_records(conn, schema, "stock_monthly", record)

        # GLOBAL QUOTE
        global_quote = data["global_quote"]
        cleaned_quote = {}
        for k, v in data.get("global_quote", {}).items():
            key = k.split(". ")[1].lower().replace(" ", "_")
            try:
                cleaned_quote[key] = float(v.replace(",", ""))
            except ValueError:
                cleaned_quote[key] = v
        create_table(conn, schema, "stock_global_quote", infer_data_types(cleaned_quote))
        insert_records(conn, schema, "stock_global_quote", cleaned_quote)

        # MARKET STATUS (list of dicts)
        """for i, market in enumerate(data["market_status"]["markets"]):
            table = "stock_market_status"
            if i == 0:
                create_table(conn, schema, table, infer_data_types(market))
            insert_records(conn, schema, table, market)"""

    except Exception as e:
        print(f"❌ Exception in ETL pipeline: {e}")
    finally:
        if conn:
            conn.close()
            print("🔒 Database connection closed.")

#if __name__ == "__main__":
#    main()