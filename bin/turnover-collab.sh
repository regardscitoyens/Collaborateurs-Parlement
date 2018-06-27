#!/bin/bash

git log data/liste_deputes_collaborateurs.csv  | grep -B 100000 40a32ae027452ef2a41072268440e45b174f2077 | grep commit | sed 's/commit //'  > data/turnover-collab.commits.csv.tmp

PREVIOUSCOMMIT=$(tail -n 1 data/turnover-collab.commits.csv.tmp);
tac data/turnover-collab.commits.csv.tmp | while read COMMIT ; do
        DATECOMMIT=$(git log 7cd556d9162b9d2e38a217ba84fbf9fb94df77c1  | grep Date: | head -n 1 | sed 's/Date: *//' )
	git diff $COMMIT $PREVIOUSCOMMIT data/liste_deputes_collaborateurs.csv | grep '^[-+]' | sed 's/^\+/"AJOUT",/' | sed 's/^-/"SUPPRESSION",/' | sed "s/$/,\"$DATECOMMIT\"/" 
done > data/turnover-collab.ajoutsuppression.csv.tmp

python bin/collab_mouvements.py data/turnover-collab.ajoutsuppression.csv.tmp
