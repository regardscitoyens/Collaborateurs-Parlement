#!/bin/bash

CACHE=$1
cd $(echo $0 | sed 's#/[^/]*$##')/..
mkdir -p pdfs pdfmaps data

if [ -z "$CACHE" ]; then
  echo "Downloading sources..." > /tmp/update_collabs_senat.tmp
  echo "--------------------------" >> /tmp/update_collabs_senat.tmp
  wget -q "http://www.nossenateurs.fr/senateurs/json" -O data/senateurs.json
  wget -q "http://www.senat.fr/pubagas/liste_senateurs_collaborateurs.pdf" -O pdfs/liste_senateurs_collaborateurs.pdf
  wget -q "http://www.senat.fr/pubagas/liste_collaborateurs_senateurs2.pdf" -O pdfs/liste_collaborateurs_senateurs2.pdf
  echo >> /tmp/update_collabs_senat.tmp
fi

source /usr/local/bin/virtualenvwrapper.sh
workon collabs

for pdffile in pdfs/*.pdf; do
  echo "Processing $pdffile..." >> /tmp/update_collabs_senat.tmp
  echo "--------------------------" >> /tmp/update_collabs_senat.tmp
  pdftohtml -xml "$pdffile" > /dev/null 2>> /tmp/update_collabs_senat.tmp
  xmlfile=$(echo $pdffile | sed 's/\.pdf$/.xml/')
  # draw maps
  ./bin/convert.py "$xmlfile" 1 2>> /tmp/update_collabs_senat.tmp
  csvfile=$(echo $pdffile | sed 's/\.pdf$/.csv/' | sed 's#pdfs/#data/#')
  ./bin/convert.py "$xmlfile" > "$csvfile" 2>> /tmp/update_collabs_senat.tmp
echo >> /tmp/update_collabs_senat.tmp
done

echo "Testing resulting CSVs..." >> /tmp/update_collabs_senat.tmp
echo "----------------------------" >> /tmp/update_collabs_senat.tmp
echo >> /tmp/update_collabs_senat.tmp

if diff data/liste_*.csv | grep . > /dev/null ; then
  echo "WARNING: differences between outputs from two sources:" >> /tmp/update_collabs_senat.tmp
  cat /tmp/update_collabs_senat.tmp
  diff data/liste_*.csv
  exit 1
else
  total=$((`cat data/liste_senateurs_collaborateurs.csv | wc -l` - 1))
  if [ "$total" -lt "300" ]; then
    echo "WARNING: something weird happened, stopping here for now..." >> /tmp/update_collabs_senat.tmp
    cat /tmp/update_collabs_senat.tmp
    exit 1
  fi
  echo "Everything fine, $total collaborateurs found in both sources" >> /tmp/update_collabs_senat.tmp
fi
echo >> /tmp/update_collabs_senat.tmp

if git status | grep "data/liste.*.csv" > /dev/null; then
  cat /tmp/update_collabs_senat.tmp
  git commit data pdfmaps pdfs -m "autoupdate"
  git push
fi

