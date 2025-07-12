import psycopg2
from requestApi import requestApi
from datetime import datetime

def connect_to_db():
    print("Connecting to the postgreSQL database....")
    try:
        con = psycopg2.connect(
            host = "db",
            port = 5432,
            dbname = "db",
            user = "db_user",
            password = "db_password")
        return con
    except psycopg2.Error as e:
        print(f"ERROR TO CONNECT DB:{e}")
        raise


    
def create_table_air_quality(conn):
    print("creating table")
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS dev;
        CREATE TABLE IF NOT EXISTS dev.air_quality(
            id SERIAL PRIMARY KEY,
                       city TEXT,
                       co FLOAT,
                       no2 FLOAT,
                       o3 FLOAT,
                       so2 FLOAT,
                       pm2_5 FLOAT,
                       pm10 FLOAT,
                       temperature FLOAT,
                       us_epa_index INT,
                       gb_defra_index INT,
                       weather_description TEXT,
                       inserted_at TIMESTAMP DEFAULT NOW()                        
                       );                 
                       """)
        conn.commit()
        print("TABLE was created.")

    except psycopg2.Error as e:
        print(f"FAILED TO CREATE TABLE:{e}")
        raise
   
def create_table_Weather(conn):
    print("creating table")
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS dev;
        CREATE TABLE IF NOT EXISTS dev.raw_weather_data(
            id SERIAL PRIMARY KEY,
                       city TEXT,
                       temperature FLOAT,
                       weather_description TEXT,
                       wind_speed FLOAT,
                       time TIMESTAMP,
                       inserted_at TIMESTAMP DEFAULT NOW(),
                       utc_offset TEXT                          
                       );                 
                       """)
        conn.commit()
        print("TABLE was created.")

    except psycopg2.Error as e:
        print(f"FAILED TO CREATE TABLE:{e}")
        raise

def insert_records_weather(con,data):
    print("Inserting weather data into db...")
    try:
        print(data['current'])
        weather = data['current']
        location = data['location']
        cursor= con.cursor()
        cursor.execute("""
                       INSERT INTO dev.raw_weather_data
                       (city,
                       temperature,
                       weather_description,
                       wind_speed,
                       time,
                       inserted_at,
                       utc_offset
                       ) VALUES (%s,%s,%s,%s,%s,NOW(),%s)
                       """,(location['name'],
                            weather['temperature'],
                            weather['weather_descriptions'][0],
                            weather['wind_speed'],
                            location['localtime'],
#                            datetime.now(),
                            location['utc_offset']))
        con.commit()
        print("Succesfully INSERTED")
    except psycopg2.Error as e:
        print(f"ERROR TO INSERT RECORD INTO DB:{e}")
        raise

def insert_records_airquality(con, data):
    print("Inserting weather data into db...")
    try:
        weather = data['current']
        airquality = weather['air_quality']
        location = data['location']

        cursor = con.cursor()
        cursor.execute("""
            INSERT INTO dev.air_quality (
                city,
                co,
                no2,
                o3,
                so2,
                pm2_5,
                pm10,
                temperature,
                us_epa_index,
                gb_defra_index,
                weather_description,
                inserted_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            location['name'],
            float(airquality["co"]),
            float(airquality["no2"]),
            float(airquality["o3"]),
            float(airquality["so2"]),
            float(airquality["pm2_5"]),
            float(airquality["pm10"]),
            float(weather['temperature']),
            int(airquality["us-epa-index"]),
            int(airquality["gb-defra-index"]),
            weather['weather_descriptions'][0]
        ))

        con.commit()
        print("Successfully INSERTED")
    except psycopg2.Error as e:
        print(f"ERROR TO INSERT RECORD INTO DB: {e}")
        raise
       
def createTables(conn):
    create_table_Weather(conn)
    create_table_air_quality(conn)    
    
    
def insert_records(conn, data):
    insert_records_weather(conn, data)
    insert_records_airquality(conn, data)
    
    
def main():
    try:
        conn = connect_to_db()
        createTables(conn)
        data = requestApi()
        insert_records(conn,data)
    except Exception as e:
        print(f"Exception : {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("Database Connection Closed")
main()