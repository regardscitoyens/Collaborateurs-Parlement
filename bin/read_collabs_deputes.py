#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re, json

with open(os.path.join("data", "deputes.json")) as f:
    parls = [p["depute"] for p in json.load(f)["deputes"]]

sexemanquants = {
  u"Elise MELLINGER": "Mme",
  u"Anne-Lise VERNIÈRES": "Mme"
}

prenomscomposes = [
  u"Andrée",
  u"Isabelle",
  u"Léa",
  u"Sébastien"
]

maj = ur"A-ZÀÂÉÈÊËÎÏÔÖÙÛÜÇ\-"
re_lower = re.compile(ur"^([%s])([%s]+)" % (maj, maj))
lower_one = lambda x: re_lower.sub(lambda x: x.group(1) + x.group(2).lower(), x)
lowerize = lambda x: " ".join([lower_one(w) for w in x.split(" ")])

headers = ['parlementaire', 'nom_parlementaire', 'prénom_parlementaire', 'sexe_parlementaire', 'collaborateur', 'nom_collaborateur', 'prénom_collaborateur', 'sexe_collaborateur', 'url_api_RC', 'url_institution', 'information complémentaire']
results = []
for d in parls:
    record = ["", "", "", "", "", "", "", "", "", "", ""]
    record[0] = d["nom"]
    record[1] = d["nom_de_famille"]
    record[2] = d["prenom"]
    record[3] = d["sexe"]
    record[8] = d["url_nosdeputes_api"].replace('json', 'xml')
    record[9] = d["url_an"]
    for c in d["collaborateurs"]:
        record[4] = c["collaborateur"]
        if record[4] in sexemanquants:
            record[4] = sexemanquants[record[4]] + " " + record[4]
        carr = lowerize(record[4]).split(" ")
        if carr[2] in prenomscomposes:
            record[5] = " ".join(carr[3:])
            record[6] = " ".join(carr[1:3])
        else:
            record[5] = " ".join(carr[2:])
            record[6] = carr[1]
        record[7] = "H" if carr[0] == "M." else "F"
        record[10] = ""
        results.append(list(record))

print ",".join(['"%s"' % h for h in headers])
for i in sorted(results, key=lambda x: ("%s %s - %s %s" % (x[1], x[2], x[5], x[6])).lower()):
    for j in range(len(i)):
        try:    i[j] = i[j].encode('utf-8')
        except: pass
    print ",".join([str(i[a]) if isinstance(i[a], int) else "\"%s\"" % i[a].replace('"', '""') for a,_ in enumerate(i)])
