import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "(localdb)\\MSSQLLocalDB")
DB_NAME = os.getenv("DB_NAME", "FPA_ModelingDB")

def get_connection_string() -> str:
    return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;"