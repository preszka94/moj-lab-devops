import oracledb

# --- DATABASE CONFIGURATION ---
# Replace 'YOUR_PASSWORD' with the password you used when creating the container
DB_USER = "system"
DB_PASSWORD = "admin123"
DB_DSN = "localhost:1521/FREEPDB1" # DSN = Data Source Name

def initialize_database():
    print(f"🔄 Connecting to Oracle DB at {DB_DSN}...")
    try:
        # Create a "Thin" connection
        connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = connection.cursor()
        print("✅ Successfully connected to Oracle Database!")

        # Create the table for our Invoice Metadata
        create_table_sql = """
        CREATE TABLE invoice_metadata (
            uuid VARCHAR2(50) PRIMARY KEY,
            filename VARCHAR2(255) NOT NULL,
            status VARCHAR2(50) NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        print("⚙️ Executing table creation...")
        try:
            cursor.execute(create_table_sql)
            print("✅ Table 'invoice_metadata' created successfully.")
        except oracledb.DatabaseError as e:
            error, = e.args
            if error.code == 955: # ORA-00955: name is already used by an existing object
                print("ℹ️ Table 'invoice_metadata' already exists. Skipping creation.")
            else:
                raise

        connection.commit()
        cursor.close()
        connection.close()
        print("🔒 Database connection closed.")

    except Exception as e:
        print(f"🔥 Database Error: {e}")

if __name__ == "__main__":
    initialize_database()