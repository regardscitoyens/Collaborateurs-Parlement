#!/bin/bash

CACHE=$1
mkdir -p pdfs pdfmaps data

if [ -z "$CACHE" ]; then
  echo "Downloading sources..."
  echo "--------------------------"
  wget -q "http://www.nossenateurs.fr/senateurs/json" -O data/senateurs.json
  wget -q "http://www.senat.fr/pubagas/liste_senateurs_collaborateurs.pdf" -O pdfs/liste_senateurs_collaborateurs.pdf
  wget -q "http://www.senat.fr/pubagas/liste_collaborateurs_senateurs2.pdf" -O pdfs/liste_collaborateurs_senateurs2.pdf
  echo
fi

for pdffile in pdfs/*.pdf; do
  echo "Processing $pdffile..."
  echo "--------------------------"
  pdftohtml -xml "$pdffile" > /dev/null
  xmlfile=$(echo $pdffile | sed 's/\.pdf$/.xml/')
  # draw maps
  ./bin/convert.py "$xmlfile" 1
  csvfile=$(echo $pdffile | sed 's/\.pdf$/.csv/' | sed 's#pdfs/#data/#')
  ./bin/convert.py "$xmlfile" > "$csvfile"
echo
done

echo "Testing resulting CSVs..."
echo "----------------------------"
echo

sort data/liste_senateurs_collaborateurs.csv > data/liste_senateurs_collaborateurs.sort
sort data/liste_collaborateurs_senateurs2.csv > data/liste_collaborateurs_senateurs2.sort
if diff data/liste_*.sort | grep .; then
  echo "WARNING: differences between outputs from two sources, see above"
else
  total=$((`cat data/liste_senateurs_collaborateurs.csv | wc -l` - 1))
  echo "Everything fine, $total collaborateurs found in both sources"
fi
echo
rm -f data/liste_*.sort
