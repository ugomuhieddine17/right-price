
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

    mutations = mutations[['idmutation', 'idmutinvar', 'idopendata',
       'idnatmut', 'codservch', 'refdoc', 'datemut',
       'coddep', 'libnatmut', 'vefa', 'valeurfonc', 'nbdispo', 'nblot',
       'nbcomm', 'l_codinsee', 'nbsection', 'l_section', 'nbpar', 'l_idpar',
       'nbparmut', 'l_idparmut', 'nbsuf', 'sterr', 'nbvolmut', 'nblocmut',
       'l_idlocmut', 'nblocmai', 'nblocapt', 'nblocdep', 'nblocact',
       'nbapt1pp', 'nbapt2pp', 'nbapt3pp', 'nbapt4pp', 'nbapt5pp', 'nbmai1pp',
       'nbmai2pp', 'nbmai3pp', 'nbmai4pp', 'nbmai5pp', 'sbati', 'sbatmai',
       'sbatapt', 'sbatact', 'sapt1pp', 'sapt2pp', 'sapt3pp', 'sapt4pp',
       'sapt5pp', 'smai1pp', 'smai2pp', 'smai3pp', 'smai4pp', 'smai5pp',
       'codtypbien', 'libtypbien', 'department_code', 'first_idpar',
       'geometry']].copy()

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
   niveau_center = pd.read_excel(niveau_centre_path, header=4)
   mutations = pd.merge(mutations, niveau_center[['codgeo', 'nivcentr']], how='left', left_on='l_codinsee', right_on='codgeo', right_index=False)
   del mutations['codgeo']
   #we consider that if no center level then 0
   mutations.nivcentr = mutations.nivcentr.fillna(0)

   return mutations


def inflation_rate_connexion(mutations, path):
    def get_inflation_rate(date_, df):
        year = date_.year
        month = date_.strftime('%b')

        return df[df['Year'] == year].iloc[0, :][month]

    inflation_df = pd.read_excel(path)
    mutations['inflation_rate'] = mutations['datemut'].apply(lambda x: get_inflation_rate(x, inflation_df))
    return mutations