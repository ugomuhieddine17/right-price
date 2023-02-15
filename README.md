# right-price

# Useful features 
- coddep = department code
- l_codinsee = list des codes insee
- nblocapt = nombre d'sppartement ayant muté
- nbapt1pp -> nbapt5pp = nombre d'appartements avec X pièces
- sbatapt = surfacee des appartement
- sapt1pp -> sapt5pp = surface de l'ensemble des appartements avec X pièces


# Cadastre 
https://github.com/mastersigat/GeoPandas/blob/main/Cadastre.ipynb
données cadastrales:
- https://cadastre.data.gouv.fr/data/etalab-cadastre/2023-01-01/geojson/departements/
- https://files.data.gouv.fr
- THE ORIGINAL : http://doc-datafoncier.cerema.fr/dv3f/doc/variable/mutation/sapt3pp
- http://doc-datafoncier.cerema.fr/dv3f/doc/variable/mutation/geomparmut
- GOOD??? https://cerema.app.box.com/v/dvfplus-opendata/folder/178403559385



# Questions 
difference between l_idpar et l_idparmut ?
Un exemple de donnée d'entrée ?
How to seperate houses and apartments?
Why some mutations values less than 1000€ ?

We want only new built buildings : should we remove all the 'Adjudication',
       'Vente terrain à bâtir', 'Echange', 'Expropriation' ?

How to manage mutations having houses, apartments etc? HOW TO KEEP ONLY APARTMENTS?

There is some mutations with a surface of 0, how to manage this? 17% -> fill with the median of the given commune


Write the sources of the external data

What is the time line of the test set?


# 1st try: assumptions

for the training:
- Vefa = True (T: 9%, F: 91%)
- the 4 types of appartments ()

Write the soources of the external data
- Population by year and commune: https://www.insee.fr/fr/statistiques (popuations legales)

