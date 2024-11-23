import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="is335",
        user="postgres",
        password="S@ud8080@",
        host="localhost",
        port="5432"
)

