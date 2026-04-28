import oracledb
import uuid

# Define the connection parameters
dsn = "100.84.101.78:1521/FREEPDB1"
user = "system"
password = "admin123"

# Establish the connection
try:
    connection = oracledb.connect(user=user, password=password, dsn=dsn)
    cursor = connection.cursor()
    
    # Define our dummy data, now including a simulated filename as the second item in each tuple
    dummy_invoices = [
        (str(uuid.uuid4()), "GS_settlement_Q3.pdf", "Goldman Sachs", 1500000.00, "SETTLED"),
        (str(uuid.uuid4()), "MS_margin_call.pdf", "Morgan Stanley", 750000.50, "PENDING"),
        (str(uuid.uuid4()), "BBG_terminal_fee.pdf", "Bloomberg LP", 12000.00, "FAILED"),
        (str(uuid.uuid4()), "Reuters_data_feed.pdf", "Reuters", 8500.00, "SETTLED")
    ]
    
    # Update the SQL statement to include the filename column and a 5th placeholder (:5)
    sql = "INSERT INTO invoice_metadata (uuid, filename, seller_name, total_amount, status) VALUES (:1, :2, :3, :4, :5)"
    
    # Execute the insertion for many rows at once
    cursor.executemany(sql, dummy_invoices)
    
    # Commit the transaction to save it permanently in the database
    connection.commit()
    
    print(f"Successfully inserted {cursor.rowcount} dummy invoices.")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    # Always close the cursor and connection to prevent resource leaks
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()