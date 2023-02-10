#!/bin/bash

set -x

DATA_URL=https://www.data.gouv.fr/fr/datasets/r
DATA_SET=6fadff46-9efd-4c53-942a-54aca783c30c

curl -sL $DATA_URL/$DATA_SET > data.csv

remove_outliers() {
sed -i '
	/"91";2020-09-18/ s_;76;_;;_
	/"59";2020-07-07/ s_;7;_;;_
	/"59";2020-07-08/ s_;16;_;;_
	/"95";2020-09-16/ s_;19;_;;_
	/"94";2022-09-07/ s_;38;_;;_
	/"[^0].";2023-02-08;/ s_\(-08;[^;]*;\)[^;]*;_\1;_
' data.csv
}

swap_monday_tuesday() {
sed -i '
	s/2022-12-26/XXX/
	s/2022-12-27/2022-12-26/
	s/XXX/2022-12-27/

	s/2023-01-16/XXX/
	s/2023-01-17/2023-01-16/
	s/XXX/2023-01-17/
' data.csv
}


fetch_departements() {
[ -f dep.csv ] || curl -s \
https://www.regions-et-departements.fr/fichiers/departements-francais.csv \
| sed '101,$ d' | sed '2,10 s/^/0/' \
| sed 's/Vandée/Vendée/' \
> dep.csv
}


remove_outliers
fetch_departements
swap_monday_tuesday
