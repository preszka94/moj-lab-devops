# Import the Flask class to create our web application, and render_template to serve HTML files.
from flask import Flask, render_template

# Import the Oracle database driver to allow our Python code to talk to the Oracle database.
import oracledb

# Initialize the Flask application instance. 
# __name__ is a built-in Python variable that tells Flask where to look for directories like 'templates' and 'static'.
app = Flask(__name__)

# Define a function to establish the database connection. 
# Creating a reusable function means we do not have to write the login credentials in every single route.
def get_db_connection():
    # Start a try-except block. This ensures that if the database is offline, the web app will not completely crash.
    try:
        # Attempt to open a connection to the Oracle database using your specific credentials and Tailscale IP.
        connection = oracledb.connect(
            user="system",
            password="admin123",
            dsn="100.84.101.78:1521/FREEPDB1" 
        )
        # If the connection is successful, return the active connection object so other functions can use it to run SQL queries.
        return connection
    
    # If the connection fails for any reason, catch the error and store it in the variable 'e'.
    except Exception as e:
        # Print the exact error message to the terminal so we can troubleshoot what went wrong.
        print(f"Database connection failed: {e}")
        # Return 'None' to signal to the rest of the application that no connection is available.
        return None

# The @app.route decorator binds a URL path to the Python function directly below it.
# The '/' represents the root or homepage of your website (e.g., http://localhost:8080/).
@app.route('/')
def dashboard():
    invoices = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT uuid, seller_name, total_amount, status FROM invoice_metadata")
            invoices = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching invoices: {e}")
        finally:
            cursor.close()
            conn.close()
            
    # Instruct Flask to locate the file 'dashboard.html' inside the 'templates' folder and send it to the user's browser.
    return render_template('dashboard.html', invoices=invoices)

# Bind the '/trading' URL to this specific function.
@app.route('/trading')
def trading():
    # Instruct Flask to serve the HTML page that will contain your investment banking interview knowledge base.
    return render_template('trading.html')

# Bind the '/trade_theory' URL to this specific function.
@app.route('/trade_theory')
def trade_theory():
    # Instruct Flask to serve the HTML page that will contain your university macroeconomic studies.
    return render_template('trade_theory.html')

# This is a standard Python security and structural check. 
# It ensures the web server only starts if this script is executed directly from the command line, 
# preventing it from starting accidentally if another script imports this file.
if __name__ == '__main__':
    # Start the built-in Flask development server.
    # host='0.0.0.0' is crucial for Docker. It tells the app to accept network connections from any IP address, allowing traffic from your Mac to reach inside the container.
    # port=8080 specifies the exact port the application will listen on, which matches our Docker port mapping.
    app.run(host='0.0.0.0', port=8080)