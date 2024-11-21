import streamlit as st
import pandas as pd
import sqlite3
import re
import os

# Custom CSS for styling
st.markdown("""
    <style>
        body {
            background-color: #f9f9f9;
        }
        .title-box {
            background-color: #87CEEB;  /* Sky Blue */
            color: white;
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .stTextInput > div > div > input, .stDateInput > div > div > input, .stNumberInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #ccc;
            padding: 10px;
        }
        .stButton > button {
            background-color: #1a73e8;
            color: white;
            border-radius: 8px;
            padding: 10px 15px;
            font-weight: bold;
            border: none;
        }
        .stButton > button:hover {
            background-color: #1559c7;
        }
        .search-section {
            margin: 0 auto;
            max-width: 600px;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Email validation function
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Initialize SQLite database
def init_database():
    try:
        conn = sqlite3.connect("SBook.db")
        cursor = conn.cursor()
        
        # Create table for bookings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_type TEXT,
                departure TEXT,
                arrival TEXT,
                travel_date TEXT,
                passengers INTEGER,
                full_name TEXT,
                email TEXT,
                payment_status TEXT
            )
        """)

        # Create table for cities and hotels
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_name TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hotel_name TEXT,
                city TEXT
            )
        """)

        # Insert some Indian cities and hotels if the tables are empty
        cursor.execute("SELECT COUNT(*) FROM Cities")
        if cursor.fetchone()[0] == 0:
            cities = ['Hyderabad', 'Vizag', 'Bangalore', 'Chennai', 'Mumbai', 'Delhi']
            for city in cities:
                cursor.execute("INSERT INTO Cities (city_name) VALUES (?)", (city,))

        cursor.execute("SELECT COUNT(*) FROM Hotels")
        if cursor.fetchone()[0] == 0:
            hotels = [
                ('Taj Hotel', 'Hyderabad'),
                ('The Park', 'Vizag'),
                ('ITC Gardenia', 'Bangalore'),
                ('The Leela Palace', 'Chennai'),
                ('The Oberoi', 'Mumbai'),
                ('The Imperial', 'Delhi')
            ]
            for hotel in hotels:
                cursor.execute("INSERT INTO Hotels (hotel_name, city) VALUES (?, ?)", hotel)

        conn.commit()
        return conn, cursor
    except Exception as e:
        st.error(f"Error initializing the database: {e}")
        return None, None

# Function to save booking data to the database
def save_to_database(cursor, conn, data):
    try:
        cursor.execute("""
            INSERT INTO Bookings (booking_type, departure, arrival, travel_date, passengers, full_name, email, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()
        st.success("Booking saved to the database successfully!")
    except Exception as e:
        st.error(f"Error saving booking to the database: {e}")

# Save data to a CSV file
def save_to_csv(data):
    filename = "bookings.csv"
    df = pd.DataFrame(data, columns=["Type", "From", "To", "Date", "Passengers", "Name", "Email", "Payment"])
    if not os.path.isfile(filename):
        df.to_csv(filename, index=False)
    else:
        df.to_csv(filename, mode='a', header=False, index=False)

# Admin authentication
def user_login():
    st.markdown("<h3>Login</h3>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "user" and password == "password":  # Simple login check for demonstration
            st.session_state["user_authenticated"] = True
            st.success("Login successful!")
        else:
            st.error("Invalid credentials. Please try again.")

def user_register():
    st.markdown("<h3>Register</h3>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password == confirm_password:
            st.session_state["user_authenticated"] = True
            st.success("Registration successful!")
        else:
            st.error("Passwords do not match.")

# Show available cities and hotels for booking
def show_available_bookings(cursor):
    st.markdown('<div class="search-section">', unsafe_allow_html=True)
    st.subheader("Available Bookings")

    # Fetch cities from the database
    cursor.execute("SELECT DISTINCT city_name FROM Cities")
    cities = [row[0] for row in cursor.fetchall()]

    st.write("### Available Cities:")
    for city in cities:
        st.write(f"- {city}")
    
    # Fetch hotels from the database
    cursor.execute("SELECT hotel_name, city FROM Hotels")
    hotels = cursor.fetchall()

    st.write("### Available Hotels:")
    for hotel in hotels:
        st.write(f"- {hotel[0]} in {hotel[1]}")

    st.markdown('</div>', unsafe_allow_html=True)

# Main function
def main():
    if "user_authenticated" not in st.session_state:
        st.session_state["user_authenticated"] = False

    conn, cursor = init_database()

    # Title
    st.markdown('<div class="title-box">Travel Booking System</div>', unsafe_allow_html=True)

    # Menu options
    menu = ["Login/Register", "Search & Book", "Admin Panel"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Login/Register page
    if choice == "Login/Register":
        if not st.session_state["user_authenticated"]:
            auth_choice = st.radio("Select Action", ["Login", "Register"])
            if auth_choice == "Login":
                user_login()
            elif auth_choice == "Register":
                user_register()
        else:
            st.success("You are logged in!")
            show_available_bookings(cursor)

    # Search and booking page
    elif choice == "Search & Book":
        if st.session_state["user_authenticated"]:
            st.markdown('<div class="search-section">', unsafe_allow_html=True)
            st.subheader("Search and Book")

            booking_type = st.selectbox("Booking Type", ["Train", "Bus", "Hotel", "Flight"], index=0)

            col1, col2 = st.columns(2)
            departure = col1.text_input("From")
            arrival = col2.text_input("To" if booking_type != "Hotel" else "Location")
            
            col3, col4 = st.columns(2)
            travel_date = col3.date_input("Travel Date")
            passengers = col4.number_input("Passengers", min_value=1, max_value=10, step=1)

            st.markdown("### Personal Details")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email Address")

            payment_status = st.selectbox("Payment Status", ["Pending", "Completed"])

            if st.button("Book Now"):
                if departure and (arrival or booking_type == "Hotel") and full_name and email:
                    if not is_valid_email(email):
                        st.error("Invalid email format.")
                    else:
                        data = (booking_type, departure, arrival, travel_date, passengers, full_name, email, payment_status)
                        save_to_database(cursor, conn, data)
                        save_to_csv([data])
                        st.success(f"Your {booking_type} booking from {departure} to {arrival} is confirmed!")
                else:
                    st.error("Please fill in all required fields.")

            st.markdown('</div>', unsafe_allow_html=True)

    # Admin panel
    elif choice == "Admin Panel":
        st.subheader("Admin Panel: View All Bookings")
        cursor.execute("SELECT * FROM Bookings")
        bookings = cursor.fetchall()
        if bookings:
            df = pd.DataFrame(bookings, columns=["ID", "Type", "From", "To", "Date", "Passengers", "Name", "Email", "Payment"])
            st.dataframe(df)
        else:
            st.write("No bookings available.")

# Run the app
if __name__ == "__main__":
    main()
