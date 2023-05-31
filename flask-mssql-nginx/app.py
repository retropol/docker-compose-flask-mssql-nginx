import os
from flask import Flask, request, render_template, render_template_string
import pyodbc
from datetime import datetime
import time
from werkzeug.serving import WSGIRequestHandler

app = Flask(__name__)

# Veritabanı bağlantısı için gerekli bilgileri güncelleyin
server = os.environ.get('DB_SERVER')
database = os.environ.get('DB_NAME')
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')

# Veritabanı bağlantısını oluştur
def create_connection():
    connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=yes"
    cnxn = pyodbc.connect(connection_string, autocommit=True)
    return cnxn


# Veritabanını oluştur
def create_database():
    cnxn = create_connection()
    cursor = cnxn.cursor()

    # Veritabanının var olup olmadığını kontrol et
    cursor.execute(f"SELECT DB_ID('{database}')")
    result = cursor.fetchone()
    if result[0] is None:
        # Veritabanı yoksa oluştur
        create_database_query = f"CREATE DATABASE {database}"
        cursor.execute(create_database_query)
        is_database_created = True
    else:
        is_database_created = False

    cnxn.commit()
    cursor.close()
    cnxn.close()

    return is_database_created


# Tabloyu oluştur
def create_table():
    cnxn = create_connection()
    cursor = cnxn.cursor()

    # Veritabanına bağlan
    cursor.execute(f"USE {database}")

    # Kullanıcılar tablosunu oluştur
    create_table_query = '''
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'istekler')
    BEGIN
        CREATE TABLE istekler (
            id INT IDENTITY(1,1) PRIMARY KEY,
            ip VARCHAR(50),
            date DATETIME
        )
    END
    '''
    cursor.execute(create_table_query)

    cnxn.commit()
    cursor.close()
    cnxn.close()

# Veritabanı ve tablolarını oluştur
is_database_created = create_database()

if is_database_created:
    create_table()

@app.route('/')
def index():
    # Gelen isteği al
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    date = datetime.now()

    # Veritabanına kaydet
    cnxn = create_connection()
    cursor = cnxn.cursor()
    cursor.execute(f"USE {database}")
    cursor.execute("INSERT INTO istekler (ip, date) VALUES (?, ?)", (ip, date))
    cnxn.commit()

    cursor.execute("SELECT TOP 15 date, ip FROM istekler ORDER BY date DESC")
    rows = cursor.fetchall()

    # Hesap makinesi işlevi
    num1 = request.args.get('num1', type=float)
    num2 = request.args.get('num2', type=float)
    operator = request.args.get('operator')

    result = None
    if num1 is not None and num2 is not None and operator is not None:
        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            if num2 != 0:
                result = num1 / num2

    cursor.close()
    cnxn.close()


    # Render template ve sonuçları döndür
    return render_template('index.html', result=result, rows=rows)

if __name__ == '__main__':
    WSGIRequestHandler.protocol_version = 'HTTP/1.1'
    app.run(host='0.0.0.0', port=5000, debug=True)
