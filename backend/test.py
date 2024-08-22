import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()
class Test:


    # Database Configuration
    DB_SERVER = os.getenv('DB_SERVER')
    DB_DATABASE = os.getenv('DB_DATABASE')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')


print("DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER=tcp:{Test.DB_SERVER},1433;"
                f"DATABASE={Test.DB_DATABASE};"
                f"UID={Test.DB_USERNAME};"
                f"PWD={Test.DB_PASSWORD};"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
                "Connection Timeout=30;"
            )


