# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import sys
from collections import defaultdict

csv_modif = csv.reader(open(sys.argv[1]))
csv_output = csv.writer(open("data/turnover.csv", 'w'))
collab = defaultdict(dict)

for modif in csv_modif:
	parlementaire = modif[1]
	collaborateur = modif[5]
	couple = (parlementaire, collaborateur)
	rawdata = modif[1:11]

	if couple not in collab:
		collab[couple]["raw_data"] = rawdata
		collab[couple]["entree"] = ""
		collab[couple]["sortie"] = ""

	if modif[0] == "AJOUT":
		collab[couple]["entree"] = modif[12]
	elif modif[0] == "SUPPRESSION":
		collab[couple]["sortie"] = modif[12]
		# print(collab[couple]["sortie"])
		newline = collab[couple]["raw_data"] + [collab[couple]["entree"], collab[couple]["sortie"]]
		csv_output.writerow(newline)
		collab.pop(couple, None)



	# print(collab[couple])

