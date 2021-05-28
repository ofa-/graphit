graphes :
---------

données hospitalières quotidiennes, cumuls des hôpitaux du département :
nombre quotidien de nouveaux décès et nouvelles admissions en réanimation.

- `réa` et `dc` : moyennes 7 jours glissants (moyenne centrée)

- `lignes grises` : 25% et "bruit" de la mortalité quotidienne toutes causes,
   pour le département ou la zone (insee données 2018+2019, moyenne par mois)

- `lignes vertes` : regressions exponentielles sur les tronçons de réa,
   les billes vertes donnent le temps de doublement (ou de division par deux)

- `lignes rouges` : regressions exponentielles sur les tronçons de dc


données : Santé Publique France >
[data.gouv.fr][data.gouv.hospi] >
[nouveaux-covid19.csv][data]


[data]: https://www.data.gouv.fr/fr/datasets/r/6fadff46-9efd-4c53-942a-54aca783c30c
[data.gouv.hospi]: https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/
