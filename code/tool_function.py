
import pandas as pd
import numpy as np
import datetime as dt
import json
import geopandas as gpd





def mutation_process(mutations):
    """
    mutation localized preprocessing
    """
    print('hi!')

    #### Geo dataframe
    mutations = gpd.GeoDataFrame(mutations, geometry=mutations.geometry)
    #### centroids
    mutations['centroid'] = mutations.geometry.centroid
    #### postcode 
    mutations['l_codinsee'] = mutations.first_idpar.str[:5]
    #### date data
    mutations.datemut = pd.to_datetime(mutations.datemut)
    mutations['month'] = mutations.datemut.dt.month
    mutations['year'] = mutations.datemut.dt.year
    mutations['day'] = mutations.datemut.dt.day
    
    return mutations

def niveau_center_connexion(mutations, niveau_centre_path='../data_to_connect/niveau_centre.xlsx'): 
   #### niveau center data
   mutations = mutations.reset_index()
   niveau_center = pd.read_excel(niveau_centre_path, header=4)
   mutations.coddep = mutations.coddep.astype('float').astype('int').astype('str')
   mutations = pd.merge(mutations, niveau_center[['codgeo', 'nivcentr']], how='left', left_on='l_codinsee', right_on='codgeo', right_index=False)
   
   niveau_center['coddep'] = niveau_center.codgeo.str[:2]
   niv_group = niveau_center.groupby('coddep').agg({'nivcentr':np.nanmedian}).reset_index()   
   mutations['nivcentr'] = mutations['nivcentr'].fillna(pd.merge(mutations[['coddep']], niv_group, on='coddep').nivcentr)

   del mutations['codgeo']
   #we consider that if no center level then 0
   # mutations.nivcentr = mutations.nivcentr.fillna(2)

   return mutations