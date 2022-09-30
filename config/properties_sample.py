# Rename this file to properties.py and update the values to match your environment.
DB_DRIVER = "{ODBC Driver 17 for SQL Server}"
DB_SERVER = "XXX.XXX.XXX.XXX"
DB_PORT = "XXXX"
DB_NAME = "XXXXX"
DB_USER = "XXXXX"
DB_PASSWORD = "XXXX"
DB_STRING = "DRIVER={0};Server={1};port={2};Database={3};uid={4};pwd={5};"
DB_CONN_STRING = DB_STRING.format(DB_DRIVER, DB_SERVER, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
OUTPUT_DIR = "./output/"
