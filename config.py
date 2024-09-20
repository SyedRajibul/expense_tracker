import os

class Config:
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'SYED123')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'rajibul547')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'expense_tracker')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')