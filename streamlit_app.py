import streamlit as st
import pandas as pd
import requests


api_key = "c9c342a9-7c10-4351-9f5c-d6735e755c19"

st.title("Weather and Air Quality Web App")
st.header("Streamlit and AirVisual API")


@st.cache_data
def map_creator(latitude, longitude):
    from streamlit_folium import folium_static
    import folium

    # Ensure coordinates are floats
    latitude = float(latitude)
    longitude = float(longitude)

    # Create a map centered on the given coordinates
    m = folium.Map(location=[latitude, longitude], zoom_start=12)

    # Add a marker for the location
    folium.Marker([latitude, longitude], popup="Selected Location", tooltip="Click for more info").add_to(m)

    # Display the map in Streamlit
    folium_static(m)


@st.cache_data
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    countries_dict = requests.get(countries_url).json()
    # st.write(countries_dict)
    return countries_dict


@st.cache_data
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={api_key}"
    states_dict = requests.get(states_url).json()
    # st.write(states_dict)
    return states_dict


@st.cache_data
def generate_list_of_cities(state_selected, country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={api_key}"
    cities_dict = requests.get(cities_url).json()
    # st.write(cities_dict)
    return cities_dict


# TODO: Include a select box for the options: ["By City, State, and Country","By Nearest City (IP Address)","By Latitude and Longitude"]
# and save its selected option in a variable called category

category = st.sidebar.selectbox(
    "Filter do find weather data:",
    ["By City, State, and Country", "By Nearest City (IP Address)", "By Latitude and Longitude"]
)

if category == "By City, State, and Country":
    countries_dict = generate_list_of_countries()
    if countries_dict["status"] == "success":
        countries_list = [i["country"] for i in countries_dict["data"]]
        countries_list.insert(0, "")

        country_selected = st.selectbox("Select a country", options=countries_list)
        if country_selected:
            states_dict = generate_list_of_states(country_selected)
            if states_dict["status"] == "success":
                states_list = [i["state"] for i in states_dict["data"]]
                states_list.insert(0, "")
                state_selected = st.selectbox("Select a state", options=states_list)

                if state_selected:
                    cities_dict = generate_list_of_cities(state_selected, country_selected)
                    if cities_dict["status"] == "success":
                        cities_list = [i["city"] for i in cities_dict["data"]]
                        cities_list.insert(0, "")
                        city_selected = st.selectbox("Select a city", options=cities_list)

                        if city_selected:
                            aqi_data_url = f"https://api.airvisual.com/v2/city?city={city_selected}&state={state_selected}&country={country_selected}&key={api_key}"
                            aqi_data_response = requests.get(aqi_data_url)

                            if aqi_data_response.status_code == 200:
                                aqi_data_dict = aqi_data_response.json()

                                if aqi_data_dict["status"] == "success":
                                    # Extracting weather and air quality data
                                    current_weather = aqi_data_dict['data']['current']['weather']
                                    pollution = aqi_data_dict['data']['current']['pollution']

                                    temperature = current_weather['tp']  # Temperature
                                    humidity = current_weather['hu']  # Humidity
                                    aqi = pollution['aqius']  # Air Quality Index (US EPA standard)

                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.markdown("<h3 style='text-align: center;'>Temperature</h3>",
                                                    unsafe_allow_html=True)
                                        st.markdown(f"<h2 style='text-align: center; color: red;'>{temperature}°C</h2>",
                                                    unsafe_allow_html=True)
                                    with col2:
                                        st.markdown("<h3 style='text-align: center;'>Humidity</h3>",
                                                    unsafe_allow_html=True)
                                        st.markdown(
                                            f"<h2 style='text-align: center; color: blue;'>{humidity}% Humidity</h2>",
                                            unsafe_allow_html=True)
                                    with col3:
                                        st.markdown("<h3 style='text-align: center;'>Air Quality Index</h3>",
                                                    unsafe_allow_html=True)
                                        st.markdown(f"<h2 style='text-align: center; color: green;'>AQI: {aqi}</h2>",
                                                    unsafe_allow_html=True)

                                    # Displaying the map
                                    latitude = aqi_data_dict['data']['location']['coordinates'][1]
                                    longitude = aqi_data_dict['data']['location']['coordinates'][0]
                                    map_creator(latitude, longitude)
                                else:
                                    st.warning("No data available for this location.")
                            else:
                                st.error("Failed to fetch data. Please try again later.")
                        else:
                            st.warning("Please select a city.")
                    else:
                        st.warning("No cities available, please select another state.")
                else:
                    st.warning("Please select a state.")
            else:
                st.warning("No states available, please select another country.")
        else:
            st.warning("Please select a country.")
    else:
        st.error("Error fetching countries. Please try again later.")

elif category == "By Nearest City (IP Address)":
    url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        aqi_data_dict = response.json()

        if aqi_data_dict["status"] == "success":
            # Extracting weather and air quality data
            data = aqi_data_dict['data']
            current_weather = data['current']['weather']
            pollution = data['current']['pollution']

            temperature = current_weather['tp']  # Temperature
            humidity = current_weather['hu']  # Humidity
            aqi = pollution['aqius']  # Air Quality Index (US EPA standard)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("<h3 style='text-align: center;'>Temperature</h3>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center; color: red;'>{temperature}°C</h2>", unsafe_allow_html=True)
            with col2:
                st.markdown("<h3 style='text-align: center;'>Humidity</h3>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center; color: blue;'>{humidity}% Humidity</h2>",
                            unsafe_allow_html=True)
            with col3:
                st.markdown("<h3 style='text-align: center;'>Air Quality Index</h3>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center; color: green;'>AQI: {aqi}</h2>", unsafe_allow_html=True)

            # Displaying the map
            latitude = data['location']['coordinates'][1]
            longitude = data['location']['coordinates'][0]
            map_creator(latitude, longitude)
        else:
            st.warning("No data available for this location.")
    else:
        st.error("Failed to fetch data. Please try again later.")

elif category == "By Latitude and Longitude":
    latitude = st.sidebar.text_input("Enter Latitude:")
    longitude = st.sidebar.text_input("Enter Longitude:")

    if latitude and longitude:
        try:
            # Convert latitude and longitude to float
            lat = float(latitude)
            lon = float(longitude)

            url = f"https://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={api_key}"
            response = requests.get(url)

            if response.status_code == 200:
                aqi_data_dict = response.json()

                if aqi_data_dict["status"] == "success":
                    # Extracting weather and air quality data
                    data = aqi_data_dict['data']
                    current_weather = data['current']['weather']
                    pollution = data['current']['pollution']

                    temperature = current_weather['tp']  # Temperature
                    humidity = current_weather['hu']  # Humidity
                    aqi = pollution['aqius']  # Air Quality Index (US EPA standard)

                    # Creating columns for displaying data
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("<h3 style='text-align: center;'>Temperature</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h2 style='text-align: center; color: red;'>{temperature}°C</h2>",
                                    unsafe_allow_html=True)
                    with col2:
                        st.markdown("<h3 style='text-align: center;'>Humidity</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h2 style='text-align: center; color: blue;'>{humidity}% Humidity</h2>",
                                    unsafe_allow_html=True)
                    with col3:
                        st.markdown("<h3 style='text-align: center;'>Air Quality Index</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h2 style='text-align: center; color: green;'>AQI: {aqi}</h2>",
                                    unsafe_allow_html=True)

                    # Displaying the map
                    latitude = data['location']['coordinates'][1]
                    longitude = data['location']['coordinates'][0]
                    map_creator(latitude, longitude)
                else:
                    st.warning("No data available for the provided coordinates.")
            else:
                st.error("Failed to fetch data. Please try again later.")
        except ValueError:
            st.error("Invalid latitude or longitude. Please enter valid numbers.")

