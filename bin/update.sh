#!/bin/bash

CACHE=$1
cd $(echo $0 | sed 's#/[^/]*$##')/..
mkdir -p pdfs pdfmaps data

function download_json {
  curl -sL "$1" > "$2.tmp"
  if python -m json.tool "$2.tmp" > /dev/null; then
    mv "$2"{.tmp,}
  else
    rm -f "$2.tmp"
  fi
}

if [ -z "$CACHE" ]; then
  echo "Downloading sources..." > /tmp/update_collabs.tmp
  echo "--------------------------" >> /tmp/update_collabs.tmp
  download_json http://www.nossenateurs.fr/senateurs/json data/senateurs.json
  wget -q "http://www.senat.fr/pubagas/liste_senateurs_collaborateurs.pdf" -O pdfs/liste_senateurs_collaborateurs.pdf
  wget -q "http://www.senat.fr/pubagas/liste_collaborateurs_senateurs2.pdf" -O pdfs/liste_collaborateurs_senateurs2.pdf
  download_json http://www.nosdeputes.fr/deputes/json data/deputes.json
  wget -q "http://www2.assemblee-nationale.fr/static/collaborateurs/liste_deputes_collaborateurs.pdf" -O pdfs/liste_deputes_collaborateurs.pdf
  echo >> /tmp/update_collabs.tmp
fi

source /usr/local/bin/virtualenvwrapper.sh
workon collabs

for pdffile in pdfs/*deputes*.pdf pdfs/*senateurs*.pdf; do
  echo "Processing $pdffile..." >> /tmp/update_collabs.tmp
  echo "--------------------------" >> /tmp/update_collabs.tmp
  pdftohtml -xml "$pdffile" > /dev/null 2>> /tmp/update_collabs.tmp
  xmlfile=$(echo $pdffile | sed 's/\.pdf$/.xml/')
  # draw maps
  ./bin/convert.py "$xmlfile" 1 2>> /tmp/update_collabs.tmp
  csvfile=$(echo $pdffile | sed 's/\.pdf$/.csv/' | sed 's#pdfs/#data/#')
  ./bin/convert.py "$xmlfile" > "$csvfile" 2>> /tmp/update_collabs.tmp
  echo >> /tmp/update_collabs.tmp
done

echo "Testing resulting CSVs..." >> /tmp/update_collabs.tmp
echo "----------------------------" >> /tmp/update_collabs.tmp
echo >> /tmp/update_collabs.tmp

printlog=false
gitpush=false

total=$((`cat data/liste_deputes_collaborateurs.csv | wc -l` - 1))
if [ "$total" -lt "500" ]; then
  echo "WARNING: something weird happened, less than 500 collabs for AN" >> /tmp/update_collabs.tmp
  echo "stopping here for now..." >> /tmp/update_collabs.tmp
  printlog=true
else
  echo "Everything fine with AN, $total collaborateurs found" >> /tmp/update_collabs.tmp
  echo >> /tmp/update_collabs.tmp
  if git status | grep "data/liste.*deputes.*.csv" > /dev/null; then
    printlog=true
    git commit data/liste*deputes* pdfmaps/*deputes* pdfs/*deputes*.pdf -m "autoupdate députés" >> /tmp/update_collabs.tmp
    gitpush=true
  fi
fi

missing='"\(MARIE","Didier","H","Mme PENALVER Aline\)"'

if diff data/liste_*senateurs*.csv | grep -v "$missing" | grep "^[<>]" > /dev/null ; then
  echo "WARNING: differences between Sénat outputs from two sources:" >> /tmp/update_collabs.tmp
  diff data/liste_*senateurs*.csv | grep "^[<>]" >> /tmp/update_collabs.tmp
  printlog=true
else
  total=$((`cat data/liste_senateurs_collaborateurs.csv | wc -l` - 1))
  if [ "$total" -lt "300" ]; then
    echo "WARNING: something weird happened, less than 300 collabs for Sénat" >> /tmp/update_collabs.tmp
    echo "stopping here for now..." >> /tmp/update_collabs.tmp
    printlog=true
  else
    echo "Everything fine with Sénat, $total collaborateurs found in both sources" >> /tmp/update_collabs.tmp
    echo >> /tmp/update_collabs.tmp
    if git status | grep "data/liste.*senateurs.*.csv" > /dev/null; then
      printlog=true
      git commit data/liste*senateurs* pdfmaps/*senateurs* pdfs/*senateurs*.pdf -m "autoupdate sénateurs" >> /tmp/update_collabs.tmp
      gitpush=true
    fi
  fi
fi

if $gitpush; then
  git push >> /tmp/update_collabs.tmp
fi
if $printlog; then
  cat /tmp/update_collabs.tmp
fi
