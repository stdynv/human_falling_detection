import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()
class Config:
    # General Configurations
    # DEBUG = os.getenv('DEBUG', True)

    # Database Configuration
    DB_SERVER="ehpadserver.database.windows.net"
    DB_DATABASE="ehpad"
    DB_USERNAME="ehpad-admin"
    DB_PASSWORD="Memoire2024!"

    
    
    # Connection String for SQL Server
    SQLALCHEMY_DATABASE_URI = (
    f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_DATABASE}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&Encrypt=yes"
    "&TrustServerCertificate=no"
    "&Connection Timeout=30"
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    @staticmethod
    def get_db_connection():
        """Method to get a database connection using pyodbc"""
        try:
            conn = pyodbc.connect(
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER=tcp:{Config.DB_SERVER},1433;"
                f"DATABASE={Config.DB_DATABASE};"
                f"UID={Config.DB_USERNAME};"
                f"PWD={Config.DB_PASSWORD};"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
                "Connection Timeout=30;"
            )
            print(conn)
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


