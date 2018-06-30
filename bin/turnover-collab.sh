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
	curl -s https://www.nosdeputes.fr/deputes/csv | sed 's|/csv;|/xml;|' | csvformat -d ';' > data/deputes.csv.tmp
fi

sed 's/"url_api_RC"/"url_nosdeputes_api"/' data/turnover-collab.ajoutsuppression.csv.tmp | sed 's/xef/ï/g' | sed 's/xe8/è/g' | sed 's/xfc/ü/g' | sed 's/xf4/ô/g' | sed 's/xe9/é/g' | sed 's/xe7/ç/g' | sed 's/xeb/ë/g' | sed 's/xee/î/g' | sed 's/xe3/ã/g' | sed 's/Mme Rival Rival/Mme Leslie Rival/' | sed 's/M. Mehdi Walid Guillo/M. Mehdi Guillo/' | sed 's/Mme Mathilde Marie Durieu Dupradel/Mme Mathilde Marie Durieu Du pradel/' | sed 's/Mme Mathilde Durieu du Pradel/Mme Mathilde Marie Durieu Du pradel/' | sed 's/Mme MARION FRANCOIS/Mme Marion François/' | sed 's/M. Jérôme Hebert/M. Jérôme Hébert/' | sed 's/M. FREDERIC GENEY/M. Fredéric Geney/' | sed 's/Mme Gwenaelle Tschudin/Mme Gwenaëlle Tschudin/' | sed 's/M. REGIS VEZON/M. Régis Vezon/' | sed 's/M. François Benoit-Marquié/M. François Benoît-Marquié/' | sed 's/M. Lucay Sautron/M. Luçay Sautron/' | sed 's/M. FRANCOIS LAVIGNE/M. François Lavigne/' | sed 's/M. STEPHANE FEUTRY/M. Stéphane Feutry/' | sed 's/Mme Laurence De Saint-Sernin/Mme Laurence de Saint Sernin/' | sed 's/Mme Marie Andrée Molly/Mme Marie-Andrée Molly/' | sed 's/M. Clément Plouze-Nonville/M. Clément Plouze-Monville/' | sed 's/M. Frédéric Fraisse/M. Frédéric Fraysse/' | sed 's/Mme Layla Imoula/Mme Leyla Imoula/' | sed 's/Mme Léopoldine Chambon/Mme Lépoldine Chambon/' | sed 's/M. Marc Siffert Sirvent/M. Marc Siffert Servent/' | sed 's/M. Sthéphane Sandeyron/M. Stéphane Sandeyron/' | sed 's/M. Odile Mottet/Mme Odile Mottet/' | sed 's/M. Cyril Buffet/M. Cyrille Buffet/' | sed 's/M. Gaël Jeanson/Mme Gaëlle Masson/' | sed 's/Mme Isabelle Verot-Besnault 2/Mme Isabelle Verot-Besnault/' | sed 's/M. Camille Aspar/Mme Camille Aspar/' | sed 's/Mme Sandrine Scali/Mme Sandrine Scali-Agazzini/' | sed 's/Mme Eloïse Kambrun/Mme Eloïse Kambrun Favennec/' | sed 's/Mme Émilie Léa Marion Collas/Mme xc9milie Léa Marion Collas/' | sed "s/Mme Camilia M'Hamed-Said/Mme Camilia Hamed-Said/" | sed 's/Mme Eloïse Kambrun Favennec Favennec/Mme Eloïse Kambrun Favennec/' | sed 's/Mme Sandrine Scali-Agazzini-Agazzini/Mme Sandrine Scali-Agazzini/' | sed 's/Mme Marjorie Hagobian/Mme Marjorie Hagobian-Mazille/' | sed 's/M. Sébastien MOULINAT-KERGOAT/M. Sébastien Moulinat/' | sed 's/Mme Marjorie Hagobian-Mazille/Mme Marjorie Hagobian/' | sed 's/M. Anthony Marie De Lassée/M. Anthony De Lassée/' > data/turnover-collab.ajoutsuppression2.csv.tmp

csvjoin --datetime-format "%m/%d/%Y %I:%M %p" -c url_nosdeputes_api data/turnover-collab.ajoutsuppression2.csv.tmp data/deputes.csv.tmp  > data/turnover-collab.ajoutsuppression-more.csv.tmp 2> /dev/null

python bin/collab_mouvements.py data/turnover-collab.ajoutsuppression-more.csv.tmp "2018-06-29 00:00:00 +0200"
