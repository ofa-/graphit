graphes :
---------

- `réa` et `dc` : moyennes 7 jours glissants (jours précedents)

- `ligne grise` : 10% de la mortalité quotidienne toutes causes, \
   pour le département ou la zone (insee données 2018+2019, moyenne par mois)

- `tronçons rouges` sur métropole : « prédictor » = courbe réa décalée de x jours, \
   légèrement écrasée (facteur 0.885, offset 0.2)

- `lignes vertes` : regressions «linéaires» (échelle log) sur les tronçons de réa, \
   les billes vertes donnent le temps de doublement


données : Santé Publique France >
[data.gouv.fr][data.gouv.hospi] >
[nouveaux-covid19.csv][data]


[data]: https://www.data.gouv.fr/fr/datasets/r/6fadff46-9efd-4c53-942a-54aca783c30c
[data.gouv.hospi]: https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/
