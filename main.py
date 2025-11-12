import psycopg2

with open("CreateTables.sql", "r") as f:
    sql_script = f.read()

conn = psycopg2.connect(
    dbname="basketball",
    user="postgres",
    password="secret",
    host="localhost",
    port="5432"
)
cur = conn.cursor()
cur.execute(sql_script)
conn.commit()
cur.close()
conn.close()

print("Created")
