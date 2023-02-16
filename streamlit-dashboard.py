import streamlit as st #need to install streamlit first, then save this file and run 'streamlit run streamlit-dashboard.py'
import pandas as pd
import datetime
import folium as fl
import streamlit_folium
import json
import requests
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="right-price")

#get the following variables: 
    #enter_date: yyyyy/nn/dd
    #enter_surface_apt
    #enter_num_rooms
header = st.container()
dashboard = st.container()

with header: 
    st.title('The Right Price')
    st.text('time 1556') #time stamp to check if streamlit web app is updated

with dashboard: 
    st.header('A new apartment comes into the market')
    st.subheader('What is the feature of the new property? ')
    
    #general information
    #adjustable features to further inout to the model
    enter_date = st.date_input('Date of entering the market: ', datetime.date(2019, 7, 6))
    enter_surface_apt = st.slider('The size (sq meters) of the apartment', min_value = 10, max_value = 155, value = 36, step = 1)
    enter_num_rooms = st.slider('The number of rooms in the apartment', min_value = 1, max_value = 5, value = 2, step = 1)
    #create 2 columns
    select_col, select2_col = st.columns(2)

    #here is more for user interface stuff. zoom in and out on diff regions and get coordinates
    #SEARCH by address/area
    select_col.markdown('**Search by address/area**')
    area = select_col.text_input('The area/address that you are looking into', '75 Rue de Monceau')
    location_area = geolocator.geocode(area)
    select_col.text('The full address is: ')
    select_col.write(location_area.address)
    select_col.text('The coordinates are: ')
    select_col.write((location_area.latitude, location_area.longitude))

    #SEARCH by clicking on the map
    select2_col.markdown('**Search by clicking on the map**')
    #get correct format for coordinates longlat
    coord = select2_col.text_input('The coordinates of the property', '48.8566,2.3522')
    lat_pred, long_pred = coord.split(',')
    lat_pred = float(lat_pred)
    long_pred = float(long_pred)
    find_coord = geolocator.reverse(coord)
    select2_col.text('The full address is: ')
    select2_col.write(find_coord.address)

    #map on the bottom. not yet found a way to retreive the longlat when clicking on the map. will need to clik on the map > copy paste the longlat above
    #define the map center and zoom level
    map_center = [48.8566, 2.3522]
    zoom_level = 10

    # define the department codes and their boundaries (circle) 
    departments = {
        '75': ([48.8585, 2.3475], 12),
        '77': ([48.6056, 2.807], 10),
        '78': ([48.8123, 2.1123], 10),
        '91': ([48.5265, 2.2645], 10),
        '92': ([48.8964, 2.2387], 11),
        '93': ([48.9112, 2.4699], 11),
        '94': ([48.7886, 2.4497], 11),
        '95': ([49.0452, 2.1614], 10)
    }
    
    #get the latitude and longitude of the area
    location_area = geolocator.geocode(area)
    if location_area is not None:
        lat = location_area.latitude
        long = location_area.longitude

        #update the map center and zoom level
        map_center = [lat, long]
        zoom_level = 15
    else:
        st.warning("Invalid address")
    

    #create the map object
    m = fl.Map(location=map_center, zoom_start=zoom_level)
    
    #add the department boundaries to the map
    for code, (center, zoom) in departments.items():
        fl.Marker(location=center, popup=code).add_to(m)
        #fl.Circle(location=center, radius=10000, color='blue', fill=False).add_to(m) #this is a circle around the center
    
    #update map center and marker where the new point is
    fl.Marker(location=map_center, popup='HERE', color='lightgray').add_to(m)
    m.add_child(fl.LatLngPopup())
    
    #add the click event to the map
    streamlit_folium.folium_static(m)

def get_insee_code(latitude, longitude):
    url = f'https://api-adresse.data.gouv.fr/reverse/?lat={latitude}&lon={longitude}'
    response = requests.get(url)
    data = json.loads(response.text)
    if 'features' in data and len(data['features']) > 0:
        properties = data['features'][0]['properties']
        if 'citycode' in properties:
            return properties['citycode']
    return None
enter_codinsee = int(get_insee_code(lat_pred, long_pred))

# for debugging purpose

#st.write(enter_date)
# st.write(enter_num_rooms)
# st.write(enter_surface_apt)
# st.write(lat_pred)
# st.write(long_pred)
# st.write(enter_codinsee)
#----------------------------------------------------------------------------------
# Note for hooking up model input and user input
# enter_date follows yyyy-mm-dd format. need to split to year, month and date
# enter_num_rooms is a format of int
# enter_surface_apt is a format of int
# lat_pred is a format of float
# long_pred is a format of float
# enter_codinsee is a format of int



