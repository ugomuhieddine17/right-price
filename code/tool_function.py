
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

def pop_commune_year(mutations, pop_path='../data_to_connect/dep-com-pop/'): 
    #all dep that are considered
    dep = [75, 77, 78, 91, 92, 93, 94, 95]
    for d in dep: 
        for year in range(2017, 2013, -1):
            file_path = pop_path + 'dep' + str(d) + '-' + str(year) + '.xls'
            locals()[f'dep{d}_{year}'] = pd.read_excel(file_path, sheet_name='Communes' , index_col=None, usecols = "C:J", header = 7)

        for year in range(2020, 2017, -1):
            file_path = pop_path + 'dep' + str(d) + '-' + str(year) + '.xlsx'
            locals()[f'dep{d}_{year}'] = pd.read_excel(file_path, sheet_name=2 , index_col=None, usecols = "C:J", header = 7)
    #loop thru all dep and year to extract all commune pop
    for d in dep: 
        globals()[f'dep{d}_pop_dict'] = {}
        for year in range(2014, 2021):
            dep_year = locals()[f'dep{d}_{year}']
            dep_year_pop = {'commune': dep_year['Code département'].astype(str) + dep_year['Code commune'].apply(lambda x: f"{x:03d}").astype(str), 'population': dep_year['Population totale']}
            dep_year_pop = pd.DataFrame(dep_year_pop)
            globals()[f'dep{d}_pop_dict'][f'dep{d}_{year}_pop'] = dep_year_pop

    dep_commune_population = {**dep75_pop_dict, **dep77_pop_dict, **dep78_pop_dict, **dep91_pop_dict, **dep92_pop_dict, **dep93_pop_dict, **dep94_pop_dict, **dep95_pop_dict}
    
    dfs = []
    #loop thru population dictionary
    for key in dep_commune_population.keys():
        dept_num, year = key.split("_")[0][3:], key.split("_")[1]
        df = dep_commune_population[key]
        df['department'] = dept_num
        df['years'] = year
        dfs.append(df)
    population_by_year_commune = pd.concat(dfs, ignore_index=True)
    
    #reorder columns as commune, year, population
    population_by_year_commune = population_by_year_commune[['department','commune', 'years', 'population']]
    population_by_year_commune = population_by_year_commune.astype({'department':int,'commune':int, 'years':int})

    mutations = pd.merge(mutations.astype({'anneemut':int, 'l_codinsee':int}), population_by_year_commune, left_on=["l_codinsee", "anneemut"], right_on=["commune", "years"], how="left")
    mutations.drop(columns=['commune', 'years', 'department'], inplace=True)
    
    return mutations