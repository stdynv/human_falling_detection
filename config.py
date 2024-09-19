import os
import pyodbc
from dotenv import load_dotenv

# Check if the .env file exists
if os.path.exists(".env"):
    load_dotenv()
else:
    print("No .env file found. Assuming environment variables are set externally.")


class Config:
    DB_SERVER = os.getenv("DB_SERVER")
    DB_DATABASE = os.getenv("DB_DATABASE")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_DATABASE}"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&Encrypt=yes"
        "&TrustServerCertificate=no"
        "&Connection Timeout=60"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_db_connection():
        """Method to get a database connection using pyodbc with dynamic environment fetching."""
        try:
            conn = pyodbc.connect(
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER=tcp:{Config.DB_SERVER},1433;"
                f"DATABASE={Config.DB_DATABASE};"
                f"UID={Config.DB_USERNAME};"
                f"PWD={Config.DB_PASSWORD};"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
                "Connection Timeout=30;"
            )
            print("Connection successful:", conn)
            return conn
        except pyodbc.Error as e:
            print(f"Error connecting to SQL Server: {e}")
            return None


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
