#!/bin/bash

CACHE=$1
mkdir -p pdfs pdfmaps data

if [ -z "$CACHE" ]; then
  wget -q "http://www.nossenateurs.fr/senateurs/json" -O data/senateurs.json
  wget -q "http://www.senat.fr/pubagas/liste_senateurs_collaborateurs.pdf" -O pdfs/liste_senateurs_collaborateurs.pdf
  wget -q "http://www.senat.fr/pubagas/liste_collaborateurs_senateurs2.pdf" -O pdfs/liste_collaborateurs_senateurs2.pdf
fi

for pdffile in pdfs/*.pdf; do
  pdftohtml -xml "$pdffile" > /dev/null
  xmlfile=$(echo $pdffile | sed 's/\.pdf$/.xml/')
  # draw maps
  ./bin/convert.py "$xmlfile" 1
  csvfile=$(echo $pdffile | sed 's/\.pdf$/.csv/' | sed 's#pdfs/#data/#')
#  ./bin/convert.py "$xmlfile" > "$csvfile"
done


