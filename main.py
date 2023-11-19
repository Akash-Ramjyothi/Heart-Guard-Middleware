# Import required modules
import random  # For generating random heart rate values
import firebase_admin  # Firebase Admin SDK for Python
from firebase_admin import db, credentials  # Firebase database and credentials handling
from datetime import datetime  # For timestamp handling
import time  # For creating delays
import serial  # Python library for serial communication

# Authenticate to Firebase using credentials from a JSON file
cred = credentials.Certificate("credentials.json")
# Initialize Firebase Admin SDK with database URL
firebase_admin.initialize_app(cred, {"databaseURL":"https://health-guard-v1-default-rtdb.asia-southeast1.firebasedatabase.app"})

# Global variables for storing data and controlling event flow
realtimeDatabaseData = None  # Variable to hold retrieved data from Firebase
SIZE_OF_ROOT = 0  # Counter for the size of the root node in Firebase
SAME_EVENT = False  # Flag to manage event flow

# Function to retrieve data from Firebase database
def select_data():
    try:
        ref = db.reference('/Heartrate-Sensor-0')  # Reference to the desired node in the database
        snapshot = ref.get()  # Retrieve data from the node

        if snapshot is not None:
            return snapshot  # Return the retrieved data
        else:
            print("No data found")
            return None
    except Exception as e:
        print("Error:", e)
        raise e

# Function to insert generated heart rate data into Firebase
def insert_data(number_of_event):
    try:
        ref = db.reference("Heartrate-Sensor-0/" + str(number_of_event))

        for i in range(30):
            heart_rate_value = random.randint(70, 80)  # Generate a random heart rate value

            if 10 < i < 20:
                heart_rate_value *= 2  # Modify heart rate based on specific conditions
            elif i > 20:
                heart_rate_value /= 2
            heart_rate_value = int(heart_rate_value)  # Convert to integer if decimal

            # Prepare data to be pushed to Firebase
            data = {
                'heartRate': heart_rate_value,
                'timeStamp': get_timestamp(),  # Get the current timestamp
            }
            print("data: ",data)
            ref.push(data)  # Push data to Firebase
            time.sleep(2)  # Delay for 2 seconds before next data insertion

    except Exception as e:
        print("Error: ", e)
        raise e

# Function to get current timestamp in a specific format
def get_timestamp():
    now = datetime.now()
    hours = now.strftime('%I')  # Get hours in 12-hour format
    minutes = now.strftime('%M')  # Get minutes
    am_pm = now.strftime('%p')  # Get AM or PM

    return f"{hours}:{minutes} {am_pm}"  # Return formatted timestamp

# Function to read Arduino data via Serial Communication
def read_arduino_data():
    Arduino = serial.Serial('COM3', 9600)  # Specify Port and Baud rate for Arduino

    while 1:
        arduino_data = str(Arduino.readline().decode('ascii'))  # Read heart rate data from Arduino
        print(arduino_data)  # Print heart rate data received from Arduino

# Main function to control the flow of events
def main():
    global SAME_EVENT  # Access the global SAME_EVENT flag

    # To read existing data from Firebase only once
    if SAME_EVENT is False:
        realtimeDatabaseData = select_data()

    # Retrieve existing data and calculate the size of the root node
    print(realtimeDatabaseData)
    SIZE_OF_ROOT = len(realtimeDatabaseData)
    print("SIZE_OF_ROOT: ", SIZE_OF_ROOT)
    SAME_EVENT = True  # Set SAME_EVENT flag to True after retrieving existing data
    print("SAME_EVENT: ", SAME_EVENT)

    # Call Arduino read function (commented out for the moment)
    # read_arduino_data()

    # Insert data into Firebase if SAME_EVENT is True
    if SAME_EVENT is True:
        insert_data(SIZE_OF_ROOT)

# Execute the main function
main()
