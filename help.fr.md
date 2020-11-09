graphes :
---------

données hospitalières quotidiennes, par département du patient :\
nombre quotidien de nouveaux décès et de nouvelles admissions en réanimation.

- `réa` et `dc` : moyennes 7 jours glissants (jours précedents)

- `ligne grise` : 50% de la mortalité quotidienne toutes causes, \
   pour le département ou la zone (insee données 2018+2019, moyenne par mois)

- `lignes vertes` : regressions «linéaires» sur les tronçons de réa, \
   les billes vertes donnent le temps de doublement

- `tronçons rouges` : « prédictor » = courbe réa décalée de x jours, \
   légèrement écrasée (facteur [0.885][ref.scaled.rea])


données : Santé Publique France >
[data.gouv.fr][data.gouv.hospi] >
[nouveaux-covid19.csv][data]


[data]: https://www.data.gouv.fr/fr/datasets/r/6fadff46-9efd-4c53-942a-54aca783c30c
[data.gouv.hospi]: https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/
[ref.scaled.rea]: https://github.com/ofa-/predictor/blob/master/predictor.py#L111-L114
