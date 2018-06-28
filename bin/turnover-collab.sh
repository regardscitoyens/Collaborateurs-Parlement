#!/bin/bash

git log data/liste_deputes_collaborateurs.csv  | grep -B 100000 0257cc23296952862232f1e941635259e3df675a | grep commit | sed 's/commit //'  > data/turnover-collab.commits.csv.tmp

echo '"action","parlementaire","nom_parlementaire","prénom_parlementaire","sexe_parlementaire","collaborateur","nom_collaborateur","prénom_collaborateur","sexe_collaborateur","url_api_RC","url_institution","information complémentaire","date action"' > data/turnover-collab.ajoutsuppression.csv.tmp


PREVIOUSCOMMIT=$(tail -n 1 data/turnover-collab.commits.csv.tmp);
tac data/turnover-collab.commits.csv.tmp | while read COMMIT ; do
        DATECOMMIT=$(git log --date=iso $COMMIT  | grep Date: | head -n 1 | sed 's/Date: *//' )
	git diff $PREVIOUSCOMMIT $COMMIT data/liste_deputes_collaborateurs.csv | grep '^[-+]"' | sed 's/^\+/"AJOUT",/' | sed 's/^-/"SUPPRESSION",/' | sed "s/$/,\"$DATECOMMIT\"/"
	PREVIOUSCOMMIT=$COMMIT 
done >> data/turnover-collab.ajoutsuppression.csv.tmp

if ! test -f data/deputes.csv.tmp ; then
	curl https://www.nosdeputes.fr/deputes/csv | sed 's|/csv;|/xml;|' | sed 's/;/,"/' | sed 's/;/","/g' | sed 's/,"*/,"/g' | sed 's/"*,/",/g' > data/deputes.csv.tmp
fi

sed -i '' 's/"url_api_RC"/"url_nosdeputes_api"/' data/turnover-collab.ajoutsuppression.csv.tmp
csvjoin -c url_nosdeputes_api data/turnover-collab.ajoutsuppression.csv.tmp data/deputes.csv.tmp  > data/turnover-collab.ajoutsuppression-more.csv.tmp 2> /dev/null 

python bin/collab_mouvements.py data/turnover-collab.ajoutsuppression-more.csv.tmp "2018-06-29 00:00:00 +0200"
