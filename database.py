# database.py

import pyodbc

def run_sql_query(sql, conn_str):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute(sql)
    
    try:
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
    except:
        results = {"message": "Sorgu çalıştırıldı fakat veri döndürmedi."}

    cursor.close()
    conn.close()

    return results
