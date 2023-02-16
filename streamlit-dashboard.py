import streamlit as st #need to install streamlit first, then save this file and run 'streamlit run streamlit-dashboard.py'
import pandas as pd
import datetime
import folium as fl
import streamlit_folium
import json
import requests
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="right-price")
from modules.tool_function import *
import xgboost as xgb
from pickle import load

# Load the model
model = xgb.XGBRegressor()
model.load_model('trained_xgb_model.json')

ct = load(open('scaler_X.pkl', 'rb'))
# load the scaler
scalery = load(open('scaler_Y.pkl', 'rb'))

feats = ['year',
 'month',
 'coddep',
 'libnatmut',
 'vefa',
 'nblot',
 'l_codinsee',
 'nbpar',
 'nbparmut',
 'nbsuf',
 'sterr',
 'nbvolmut',
 'nblocmut',
 'nblocmai',
 'nblocapt',
 'nblocdep',
 'nblocact',
 'sbati',
 'sbatmai',
 'sbatapt',
 'sbatact',
 'sapt1pp',
 'sapt2pp',
 'sapt3pp',
 'sapt4pp',
 'sapt5pp',
 'smai1pp',
 'smai2pp',
 'smai3pp',
 'smai4pp',
 'smai5pp',
 'libtypbien',
 'day',
 'smoyapt',
 'nivcentr',
 'population',
 'dens_pop',
 'salary',
 'inflation',
 'near_distance',
 'near_type',
 'near_number',
 'latitude',
 'longitude']



#get the following variables: 
    #enter_date: yyyyy/nn/dd
    #enter_surface_apt
    #enter_num_rooms
header = st.container()
dashboard = st.container()

#Caching the model for faster loading


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

import time


# st.success('Done!')

FIXED_FEATURES = {
    'libnatmut': "UN APPARTEMENT",
    'vefa': 1,
    'nblot': 2,
    'nbpar': 1,
    'nbparmut': 1,
    'nbsuf': 1,
    'sterr': 0,
    'nbvolmut': 0,
    'nblocmut': 2,
    'nblocmai': 0,
    'nblocdep': 0,
    'nblocact': 0,
    'sbatmai': 0,
    'sbatact': 0,
    'smai1pp': 0,
    'smai2pp': 0,
    'smai3pp': 0,
    'smai4pp': 0,
    'smai5pp': 0,
    'nblocapt': 0,
    'libtypbien': "UN APPARTEMENT",
    'sapt1pp': 0,
    'sapt2pp': 0,
    'sapt3pp': 0,
    'sapt4pp': 0,
    'sapt5pp': 0
}

features_3 = [
       'smoyapt'
]



@st.cache_data(show_spinner=False)
def format_input_format_model(input_date, sbatapt, num_room, long, lat, fixed_features = FIXED_FEATURES):
    features = fixed_features
    features['year'] = input_date.year
    features['month'] = input_date.month
    features['day'] = input_date.day
    features['sbatapt'] = float(sbatapt)

    tmp = f'sapt{str(num_room)}pp'
    features[tmp] = sbatapt

    features['longitude'] = float(long)
    features['latitude'] = float(lat)

    features['sbati'] = float(sbatapt)

    code_insee = str(get_insee_code(lat_pred, long_pred))
    features['coddep'] = int(code_insee[:2])
    features['l_codinsee'] = code_insee

    input_df = pd.DataFrame(data=features, index=[0])

    # To remove
    input_df['datemut'] = datetime.datetime(year=2019, month=5, day=5)

    input_df['smoyapt'] = input_df.sbatapt
    

    start_time = time.time()
    
    # nivcentr
    input_df = niveau_center_connexion(input_df)
    print(f'niv center: {len(input_df)}')

    # population
    input_df = pop_commune_year(input_df)

    # Inflation
    # input_df['inflation'] = get_inflation_rate(input_date)

    # dens_pop
    input_df['dens_pop'] = get_dens_commune(code_insee, input_date.year)
    print(f'dens: {len(input_df)}')

    input_df = gpd.GeoDataFrame(
      input_df, geometry=gpd.points_from_xy(input_df.longitude, input_df.latitude))  
    input_df['centroid'] = input_df.geometry

    
    
    # ‘near_distance’, ‘near_type’, ‘near_number’
    input_df = get_distances(input_df, dir='..', near=1, distance=1, radius=0.009)

    stop_time = time.time()
    print(f'time: {stop_time - start_time}')

    # Need clarification:
    input_df['inflation'] = 0.02
    input_df['salary'] = 13.258

    cols_to_remove = ['datemut', 'geometry', 'centroid', 'index']
    input_df.drop(cols_to_remove, axis=1, inplace=True)

    input_df['coddep'] = input_df['coddep'].astype(int)

    print(input_df.dtypes)

    print(input_df[feats])

    return input_df

def predict(input_df, feats):
    # prediction = model.predict(input_df)
    pred = model.predict(ct.transform(input_df[feats]))
    inv_pred = scalery.inverse_transform([pred]).ravel()
    inv_pred = [elt  if elt > 0 else 5000 for elt in inv_pred]
    return inv_pred[0]

    
if st.button('Predict Price'):
    with st.spinner('In progress...'):
        input_date = enter_date
        sbatapt = float(enter_surface_apt)
        num_room = int(enter_num_rooms)
        long = location_area.longitude
        lat = location_area.latitude

        start_time = time.time()
        input_df = format_input_format_model(
            input_date, 
            sbatapt=sbatapt, num_room=num_room, 
            long=long, lat=lat, 
            fixed_features = FIXED_FEATURES)
        prediction = predict(input_df, feats)
        stop_time = time.time()
        print(f'time: {stop_time - start_time}')

    st.success(f'The predicted value for your appartment is : {prediction} EUR')

# for debugging purpose
# 49.0452, 2.1614

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



