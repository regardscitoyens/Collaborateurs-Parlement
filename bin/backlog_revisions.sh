#!/bin/bash

badcommits="\(bcb0b8de41ba7223fc12fd66f8b66b8b7b462be1\|7582589cc4b7c656489f506056c6cc3db4e2f72a\|a5809e68bb2326010d13e32bc025ddce650934c8\|bcb0b8de41ba7223fc12fd66f8b66b8b7b462be1\)"

stashed=false
if git diff | grep . > /dev/null; then
  git stash #> /dev/null 2>&1
  stashed=true
fi

for typ in depute senateur; do
  fil="data/liste_${typ}s_collaborateurs.csv"
  ofil=$(echo $fil | sed 's/\.csv/-totaux\.csv/')
  echo "date,commit,total_collabs" > $ofil.tmp
  git log --date-order --pretty=format:"%ci %H" $fil    |
    grep -v "$badcommits"                               |
    sort                                                |
    while read commit; do
      dat=$(echo $commit | awk '{print $1}')
      cid=$(echo $commit | awk '{print $4}')
      git checkout $cid > /dev/null 2>&1
      lines=$(cat $fil | grep -v '^"parlementaire' | wc -l)
      echo "$dat,$cid,$lines"
    done | uniq --check-chars=10 >> $ofil.tmp
  git checkout master > /dev/null 2>&1
done
if $stashed; then
  git stash pop #> /dev/null 2>&1
fi
for typ in depute senateur; do
  mv data/liste_${typ}s_collaborateurs-totaux.csv{.tmp,}
done
