import pandas as pd
import psycopg

conn = psycopg.connect("dbname=test user=postgres password=secret host=localhost")

# Einfacher SQL-Query direkt ins DataFrame
df = pd.read_sql_query("SELECT * FROM my_table", conn)

print(df.head())
conn.close()
