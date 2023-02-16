
import pandas as pd
import numpy as np
import datetime as dt
import json
import geopandas as gpd
from scipy.spatial import cKDTree
from shapely.geometry import Point, LineString
from shapely.geometry import Point
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt
import json
import os
import re


def mutation_process(mutations):
    """
    mutation localized preprocessing
    """
    print(f"\nOriginal shape mutation process {mutations.shape}")

    # to_int
    s_app = [f"sapt{i}pp" for i in range(1, 6)]
    s_maison = [f"smai{i}pp" for i in range(1, 6)]
    to_int = ["idmutation", "anneemut", "moismut", "coddep", "nblot", "nbpar", "nbparmut", 
              "nbsuf", "sterr", "nbvolmut", "nblocmut", "nblocapt", "nblocdep", "nblocact", 
              "sbati", "sbatact"] + s_app + s_maison   # to int since metres squared
    for col in to_int:
      mutations[col] = mutations[col].astype(int)

    # datetime
    mutations.datemut = pd.to_datetime(mutations.datemut)
    mutations.rename(columns={"anneemut": "year", "moismut": "month"}, inplace=True)
    mutations["day"] = mutations.datemut.dt.day

    # drop
    n_app = [f"nbapt{i}pp" for i in range(1, 6)]
    n_maison = [f"nbmai{i}pp" for i in range(1, 6)]
    others = ["Unnamed: 0.1",  "Unnamed: 0", "idmutinvar",
              "idopendata", "idnatmut", "codservch", "refdoc",
              "nbdispo", "nbcomm", "nbsection", "l_section", 
              "l_idpar", "l_idparmut", "l_idlocmut", "department_code", "codtypbien", "id"]   #'first_idpar' to erase? 
   
    to_drop = n_app + n_maison + others
    mutations.drop(columns=to_drop, axis=1, inplace=True)

    #### Postcode 
    mutations['l_codinsee'] = mutations.first_idpar.str[:5]

    # Dropping missing geometry
    mutations.dropna(axis=0, subset=["geometry", "valeurfonc"], inplace=True)

    #### Geo dataframe
    mutations = gpd.GeoDataFrame(mutations, geometry=mutations.geometry)
    #### centroids
    mutations['centroid'] = mutations.geometry.centroid
    mutations['area'] = mutations.geometry.area    
    print(f"Final shape mutation process {mutations.shape}\n")
    
    return mutations




def mutation_test_process(df):
    """
    mutation localized preprocessing
    """
    print('hi!')

    #### centroids
    # mutations['centroid'] = mutations.geometry.centroid
    #### postcode 
    df['first_idpar'] = df.l_idpar.apply(lambda x: eval(x)[0])
    df['l_codinsee'] = df.first_idpar.str[:5]
    #### date data
    df.datemut = pd.to_datetime(df.datemut)
    df['month'] = df.datemut.dt.month
    df['year'] = df.datemut.dt.year
    df['day'] = df.datemut.dt.day
    
    
    return df



def adjustment_bati(mutations, thresh_sbati=9, thresh_valeur=5000):

  # Creation smoymai, smoyapt, smoyact and adjustment sbati

  original_shape = mutations.shape
  print(f"Shape before adjustment of bati: {original_shape}")

  df_surf = mutations[~((mutations.sbati ==0) & (mutations[['nblocmai', 'nblocapt', 'nblocact']].sum(axis=1) == 0))].copy()
  for (moy, col, nbloc) in zip(['smoymai', 'smoyapt', 'smoyact'], ["sbatmai", "sbatapt", "sbatact"], ['nblocmai', 'nblocapt', 'nblocact']):
    df_surf[moy] = np.where(df_surf[nbloc]!=0, df_surf[col]/df_surf[nbloc], 0)

  df_surf = df_surf.reset_index(drop=True)
  for (col, moy, nbloc) in zip(["sbatmai", "sbatapt", "sbatact"], ['smoymai', 'smoyapt', 'smoyact'], ['nblocmai', 'nblocapt', 'nblocact']):
    df_surf.loc[df_surf["sbati"]==0, col] = df_surf.groupby('l_codinsee')[moy].transform(np.nanmedian) * df_surf[nbloc]
  df_surf.loc[df_surf["sbati"]==0, "sbati"] = df_surf[['sbatmai', 'sbatapt', 'sbatact']].sum(axis=1)

  df_surf = df_surf.reset_index(drop=True)
  for (col, moy, nbloc) in zip(["sbatmai", "sbatapt", "sbatact"], ['smoymai', 'smoyapt', 'smoyact'], ['nblocmai', 'nblocapt', 'nblocact']):
    df_surf.loc[df_surf["sbati"]==0, col] = df_surf.groupby('l_codinsee')[moy].transform(np.nanmedian) * df_surf[nbloc]
  df_surf.loc[df_surf["sbati"]==0, 'sbati'] = df_surf[['sbatmai', 'sbatapt', 'sbatact']].sum(axis=1)

  for (moy, col, nbloc) in zip(['smoymai', 'smoyapt', 'smoyact'], ["sbatmai", "sbatapt", "sbatact"], ['nblocmai', 'nblocapt', 'nblocact']):
    df_surf[moy] = np.where(df_surf[nbloc]!=0, df_surf[col]/df_surf[nbloc], 0)

  # Filtering out 0 apartments
  mutations = df_surf[~(df_surf["nblocapt"]==0)].copy()

  # Filtering out small apartments and sensitive prices
  mutations = mutations[(mutations.sbati > thresh_sbati) & (mutations.valeurfonc>thresh_valeur)].copy()

  # We only want appartements
  # wanted_libtypbien = ["UN APPARTEMENT", "APPARTEMENT INDETERMINE", "DEUX APPARTEMENTS", 
                        # "BATI - INDETERMINE : Vefa sans descriptif", "BATI - INDETERMINE : Vente avec volume(s)"]  
  # mutations = mutations[mutations.libtypbien.isin(wanted_libtypbien)].copy()
  # print(f"\nUnique libtypes: {mutations['libtypbien'].unique()}\n")

  final_shape = mutations.shape
  print(f"Shape after adjustment of bati: {final_shape}, that is {final_shape[0]/original_shape[0]: .2%} of original observations\n")
  return mutations




def niveau_center_connexion(mutations): 
   dir = ".."
   niveau_centre_path = os.path.join(dir, "data_to_connect", "niveau_centre.xlsx")

   mutations = mutations.reset_index()
   niveau_center = pd.read_excel(niveau_centre_path, header=4)
   mutations = pd.merge(mutations, niveau_center[['codgeo', 'nivcentr']], how='left', left_on='l_codinsee', right_on='codgeo', right_index=False)
   
   mutations.coddep = mutations.coddep.astype('float').astype('int').astype('str')
   niveau_center['coddep'] = niveau_center.codgeo.str[:2]
   niv_group = niveau_center.groupby('coddep').agg({'nivcentr':np.nanmedian}).reset_index()   
   mutations['nivcentr'] = mutations['nivcentr'].fillna(pd.merge(mutations[['coddep']], niv_group, on='coddep').nivcentr)

   del mutations['codgeo']
   return mutations


def pop_commune_year(mutations): 
  
    dir = ".."
    pop_path = os.path.join(dir, "data_to_connect", "dep-com-pop/")

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

    mutations = pd.merge(mutations.astype({'year':int, 'l_codinsee':int}), population_by_year_commune, left_on=["l_codinsee", "year"], right_on=["commune", "years"], how="left")
    mutations.drop(columns=['commune', 'years', 'department'], inplace=True)
    
    return mutations




def density_commune(mutations): 
  dir = ".."
  name_file = "insee_rp_hist.xlsx"
  pop_path = os.path.join(dir, "data_to_connect")  
  file_path = os.path.join(pop_path, name_file)

  df = pd.read_excel(file_path, sheet_name='Data' , index_col=None, usecols = "A:D", header = 4)
  df = df.astype({'codgeo': str, 'an':int})
  df["dep"] = df["codgeo"].str[:2]

  df_fin = df[df["an"]==2019].copy()
  res = pd.merge(mutations.astype({'l_codinsee': str}), df_fin[["codgeo", "dens_pop"]], left_on=["l_codinsee"], right_on=["codgeo"], how="left")
  res.drop(columns="codgeo", inplace=True)
  return res


def salary_connexion(mutations):

    dir = ".."
    name_file = "_Salaire net horaire moyen by Commune.xlsx"
    pop_path = os.path.join(dir, "data_to_connect")
    salary_path = os.path.join(pop_path, name_file)

    mut = mutations.copy()
    salaire = pd.read_excel(salary_path)
    salaire = salaire.drop(columns=['Unnamed: 0', 'LIBGEO'])
    salaire = salaire.melt('CODGEO', var_name='years', value_name='salary')
    salaire.years = '20'+ salaire.years.str[-2:]
    salaire.years = salaire.years.astype('int')

    test = pd.merge(mut.astype({'year':int, 'l_codinsee':str}), salaire.astype({'years':int, 'CODGEO':str}), 
                    how='left', left_on=['year', 'l_codinsee'], right_on=['years', 'CODGEO'])

    salaire['coddep'] = salaire.CODGEO.str[:2]
    sal_group = salaire.groupby('coddep').agg({'salary':np.nanmedian}).reset_index()   
    test['salary'] = test['salary'].fillna(pd.merge(test[['coddep']], sal_group, on='coddep').salary)
    del test['CODGEO']
    del test['years']

    return test 
  
  
def inflation_month(mutations):

    dir = "drive/MyDrive/Hackathon"
    #dir = ".."
    path = os.path.join(dir, "data_to_connect")
    file_path = os.path.join(path, 'inflation_rate.xlsx')

    inflation_df = pd.read_excel(file_path)
    inflation_df = inflation_df.melt(id_vars="Year", var_name="month", value_name="inflation")
    inflation_df.rename(columns={"month": "Mon"}, inplace=True)

    mutations["month_b"] = mutations["datemut"].dt.strftime("%b").copy()
    mutations = pd.merge(mutations, inflation_df, left_on=["year", "month_b"], right_on=["Year", "Mon"])
    mutations.drop(columns=["month_b", "Year", "Mon"], inplace=True)
    return mutations



def get_distances(mutations, near=1, distance=1, radius=0.08):
  ''' distance is manhattan (p parameter). distance computed on near while numbers of stations in neighborhoood depends on radius '''

  dir = "drive/MyDrive/Hackathon"
  #dir = ".."
  path = os.path.join(dir, "data_to_connect")
  file_path = os.path.join(path, 'emplacement-des-gares-idf.geojson')
  trains = gpd.read_file(file_path)
  avail_columns = trains.columns.tolist()

  mutations.set_geometry('centroid', inplace=True)
  ls_neigh = np.concatenate([np.array(geom.coords) for geom in trains.geometry.to_list()])
  candidates = np.concatenate([np.array(geom.coords) for geom in mutations.geometry.to_list()])

  ckd_tree = cKDTree(ls_neigh)
  dist, idx = ckd_tree.query(candidates, k=near, p=distance)  # Manhattan distance

  type_name = avail_columns.index("mode")
  mutations["near_distance"] = dist.astype(float)
  mutations["near_type"] = trains.iloc[idx.tolist(),  type_name].astype(str).tolist()
  
  nbs = ckd_tree.query_ball_point(candidates, r=radius, p=distance, return_length=True)  # return_length returns the number of points inside the radius instead of a list of the indices
  mutations["near_number"] = nbs.astype(int).tolist()

  return mutations

  
  


def inflation_rate_connexion(mutations, path='../data_to_connect/inflation_rate.xlsx'):
    def get_inflation_rate(date_, df):
        year = date_.year
        month = date_.strftime('%b')

        return df[df['Year'] == year].iloc[0, :][month]

    inflation_df = pd.read_excel(path)
    mutations['inflation_rate'] = mutations['datemut'].apply(lambda x: get_inflation_rate(x, inflation_df))
    return mutations