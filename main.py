import sqlite3
from datetime import datetime, timedelta
import random

# Connect to the SQLite database
conn = sqlite3.connect('static/database.db')
cursor = conn.cursor()

# Username to associate with the login logs
username = "testtest"

# Generate login logs with increasing numbers from January to December for the specified username
login_logs = []
current_date = datetime.now()

for month in range(1, 13):
    num_logins = random.randint(1, 12)  # Vary the number of logins for each month (1 to 12)

    for _ in range(num_logins):
        login_logs.append((username, current_date.strftime("%Y-%m-%d %H:%M:%S")))

    # Move to the next month
    current_date = current_date + timedelta(days=30)

# Insert login logs into the Login table
cursor.executemany("INSERT INTO Login_logs (username, date) VALUES (?, ?)", login_logs)
conn.commit()

# Close the database connection
conn.close()

print("Login logs inserted successfully for username 'testtest'.")