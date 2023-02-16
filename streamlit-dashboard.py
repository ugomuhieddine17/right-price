import streamlit as st #need to install streamlit first, then save this file and run 'streamlit run streamlit-dashboard.py'
import pandas as pd
import datetime
import folium as fl
import streamlit_folium
import json

header = st.container()
model_training = st.container()

with header: 
    st.title('The Right Price')
    st.text('time 1924') #time stamp to check if streamlit web app is updated

with model_training: 
    st.header('A new apartment comes into the market')
    st.subheader('What is the feature of the new property? ')
    
    #create 2 columns
    select_col, select2_col = st.columns(2)
    
    #adjustable features to further inout to the model
    enter_date = select_col.date_input('Enter market date: ', datetime.date(2019, 7, 6))
    surface = select_col.slider('The size (sq meters) of the apartment', min_value = 10, max_value = 155, value = 36, step = 1)
    num_rooms = select_col.slider('The number of rooms in the apartment', min_value = 1, max_value = 5, value = 2, step = 1)

    commune = select2_col.text_input('The commune/department that you are looking into', 75101)
    long = select2_col.text_input('The longitude of the property', 48.8566)
    lat = select2_col.text_input('The latitude of the property', 2.3522)

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
        
    #create the map object
    m = fl.Map(location=map_center, zoom_start=zoom_level)
    #add the department boundaries to the map
    for code, (center, zoom) in departments.items():
        fl.Marker(location=center, popup=code).add_to(m)
        #fl.Circle(location=center, radius=10000, color='blue', fill=False).add_to(m) #this is a circle around the center
    m.add_child(fl.LatLngPopup())
    #add the click event to the map
    streamlit_folium.folium_static(m)
