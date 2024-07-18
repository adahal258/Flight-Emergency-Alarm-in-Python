import requests
import time
import pygame  # Import the pygame module
import tkinter as tk
from tkinter import messagebox, simpledialog
from geopy.geocoders import Nominatim
import folium

# Initialize pygame for sound
pygame.mixer.init()

# Function to fetch flight data
def fetch_flight_data():
    url = "https://opensky-network.org/api/states/all"
    params = {
        "lamin": -90,    # Latitude min (South Pole)
        "lomin": -180,   # Longitude min (International Date Line)
        "lamax": 90,     # Latitude max (North Pole)
        "lomax": 180     # Longitude max
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise error for bad responses
        if response.status_code == 200:
            data = response.json()["states"]
            return data
        else:
            print(f"Error fetching data: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except KeyError as e:
        print(f"KeyError: {e}")
        return None

# Function to check for emergency flights
def check_emergency_flights(flights):
    emergency_flights = []
    for flight in flights:
        squawk = flight[14]
        if squawk in ["7700"]:  # Check if squawk code indicates emergency
            emergency_flights.append(flight)
    return emergency_flights

# Function to play alarm sound
def play_alarm_sound(sound_file):
    pygame.mixer.music.load(sound_file)  # Load the sound file
    pygame.mixer.music.play()  # Play the sound file

# Function to geocode locations
def geocode_location(location_name):
    geolocator = Nominatim(user_agent="flight_emergency_system")
    location = geolocator.geocode(location_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

# Function to display map with live location and flight details
def display_map_with_live_location_and_route(flight):
    latitude = flight[6]
    longitude = flight[5]
    altitude = flight[7]
    velocity = flight[9]
    heading = flight[10]
    vertical_rate = flight[11]
    callsign = flight[1]
    origin_country = flight[2]
    
    if latitude and longitude:
        m = folium.Map(location=[latitude, longitude], zoom_start=8)
        
        # Add markers for departure and destination (placeholders)
        dep_coords = geocode_location("New York")  # Placeholder
        dest_coords = geocode_location("Los Angeles")  # Placeholder
        if dep_coords and dest_coords:
            folium.Marker(dep_coords, tooltip='Departure', icon=folium.Icon(color='green')).add_to(m)
            folium.Marker(dest_coords, tooltip='Destination', icon=folium.Icon(color='red')).add_to(m)
            folium.PolyLine(locations=[dep_coords, dest_coords], color='blue').add_to(m)
        
        # Add marker for current flight location with details
        folium.Marker([latitude, longitude], tooltip=f'Flight {callsign} - {origin_country}', icon=folium.Icon(color='blue')).add_to(m)
        folium.CircleMarker([latitude, longitude], radius=6, tooltip=f'Altitude: {altitude} m\nVelocity: {velocity} m/s\nHeading: {heading}°\nVertical Rate: {vertical_rate} m/s', fill=True, color='blue', fill_opacity=0.7).add_to(m)
        
        # Save map to HTML file
        m.save("flight_route_and_location.html")
        messagebox.showinfo("Map Saved", "Flight route and live location map has been saved as 'flight_route_and_location.html'")
    else:
        messagebox.showerror("Location Error", "Unable to get the current location of the flight")

# Function to display flight details
def display_flight_details(flight):
    details = f"""
    Flight Details:
    - ICAO24: {flight[0]}
    - Callsign: {flight[1]}
    - Origin Country: {flight[2]}
    - Latitude: {flight[6]}
    - Longitude: {flight[5]}
    - Altitude: {flight[7]} m
    - Velocity: {flight[9]} m/s
    - Heading: {flight[10]}°
    - Vertical Rate: {flight[11]} m/s
    """
    messagebox.showinfo("Flight Details", details)

# Function to handle fetching and displaying route for emergency flights
def fetch_and_display_route(emergency_flights):
    for flight in emergency_flights:
        icao24 = flight[0]
        print(f"Flight ICAO24: {icao24}")

        # Fetch flight route details (you need a specific API or dataset for this)
        # Here, we're using placeholders for departure and destination locations
        departure = "New York"  # Placeholder
        destination = "Los Angeles"  # Placeholder

        dep_coords = geocode_location(departure)
        dest_coords = geocode_location(destination)
        display_map_with_live_location_and_route(flight)  # Call the function to display map with live location and route

# Function to continuously monitor flights
def monitor_flights():
    while True:
        flights = fetch_flight_data()
        if flights:
            emergency_flights = check_emergency_flights(flights)
            print(emergency_flights)
            if emergency_flights:
                for flight in emergency_flights:
                    squawk = flight[14]
                    if squawk == "7700":
                        print(f"Emergency Signal Alarm! Found {len(emergency_flights)} emergency flights with emergency code 7700:")
                    for flight in emergency_flights:
                        print(f"  - Flight {flight[1]} ({flight[0]}) from {flight[2]}")
                    print("-" * 50)
                    play_alarm_sound("Alert.mp3")  # Call the function to play the alarm sound
                    fetch_and_display_route(emergency_flights)
            else:
                print("Air is safe. No emergency code detected.")
        time.sleep(20)  # Fetch data every 20 seconds

# Function to display emergency flights
def display_emergency_flights():
    flights = fetch_flight_data()
    if flights:
        emergency_flights = check_emergency_flights(flights)
        if emergency_flights:
            emergency_list = "\n".join([f"{flight[0]} - {flight[1]} ({flight[2]})" for flight in emergency_flights])
            messagebox.showinfo("Emergency Flights", emergency_list)
        else:
            messagebox.showinfo("No Emergency Flights", "There are no emergency flights at the moment.")
    else:
        messagebox.showerror("Data Error", "Unable to fetch flight data.")

# Function to display flight details with live location and route
def display_flight_details_with_live_location():
    flights = fetch_flight_data()
    if flights:
        for flight in flights:
            print(flight)
        flight_id = simpledialog.askstring("Flight Selection", "Enter the ICAO24 identifier of the flight:")
        selected_flight = None
        for flight in flights:
            if flight[0] == flight_id:
                selected_flight = flight
                break
        if selected_flight:
            display_flight_details(selected_flight)
            display_map_with_live_location_and_route(selected_flight)
        else:
            messagebox.showerror("Selection Error", "Flight not found.")
    else:
        messagebox.showerror("Data Error", "Unable to fetch flight data.")

# GUI Setup
root = tk.Tk()
root.title("Flight Emergency Detection System")

monitor_button = tk.Button(root, text="Start Monitoring Emergency Flights", command=monitor_flights)
monitor_button.pack(pady=10)

emergency_flights_button = tk.Button(root, text="View Emergency Flights", command=display_emergency_flights)
emergency_flights_button.pack(pady=10)

flight_details_button = tk.Button(root, text="View Flight Details and Live Location", command=display_flight_details_with_live_location)
flight_details_button.pack(pady=10)

root.mainloop()
