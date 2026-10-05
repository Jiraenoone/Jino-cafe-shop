"""
database/azure_migrate.py — Execute schema.sql on Azure SQL Database
"""
import os
import sys

def migrate(connection_string: str):
    print("Executing schema.sql migration on Azure SQL...")
    try:
        import pyodbc
    except ImportError:
        print("Installing pyodbc...")
        os.system("pip install pyodbc")
        import pyodbc

    with open("database/schema.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Split by GO commands
    statements = [stmt.strip() for stmt in sql_script.split("GO") if stmt.strip()]

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    for idx, stmt in enumerate(statements, 1):
        try:
            cursor.execute(stmt)
            conn.commit()
            print(f"[{idx}/{len(statements)}] Executed statement successfully.")
        except Exception as e:
            print(f"[{idx}/{len(statements)}] Warning/Error: {e}")

    conn.close()
    print("✅ Migration complete!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        migrate(sys.argv[1])
    else:
        print("Usage: python azure_migrate.py <connection_string>")
