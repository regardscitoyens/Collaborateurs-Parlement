# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import sys
import math
from dateutil.parser import parse
from collections import defaultdict

csv_modif = csv.reader(open(sys.argv[1]))
header = next(csv_modif)
csv_output = csv.writer(open("data/turnover.csv", 'w'))
newheaders = header[1:11] + ["entree", "sortie", "nombredejours"]
csv_output.writerow(newheaders)
collab = defaultdict(dict)

def writecollab(unecollab):
	parsed_entree = parse(unecollab["entree"])
	nbdejours = ""
	if unecollab["sortie"] != "":
		parsed_sortie = parse(unecollab["sortie"])
		nbdejours = parsed_sortie - parsed_entree
		nbdejours = str(math.floor(nbdejours.total_seconds()/60/60/24))
	newline = unecollab["raw_data"] + [unecollab["entree"], unecollab["sortie"], nbdejours]
	csv_output.writerow(newline)

couple_contrats = defaultdict(list)

def validcollab(couple):
	couple_contrats[couple].append(collab[couple])


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
		if collab[couple]["entree"] != "":
			print("ERROR: Réembauche d'un collab déjà en poste")
			print(modif)
		collab[couple]["entree"] = modif[12]

	elif modif[0] == "SUPPRESSION":
		if collab[couple]["sortie"] != "":
			print("ERROR: Fin d'un contrat jamais commencé")
			print(modif)
		if collab[couple]["entree"] == "":
			print("ERROR: Collaborateur embauché à la législature précédente")
			print(modif)
			collab[couple]["entree"] = "2017-06-21 00:00:00 +0200"
		collab[couple]["sortie"] = modif[12]

		# À chaque fin de contrat, l'information est versée dans un .csv de façon à s'assurer que 
		# les données ne soient pas écrasée en cas de réembauche du collab par le même parlementaire
		validcollab(couple)
		collab.pop(couple, None)

for couple in collab:
	validcollab(couple)

for couple in couple_contrats:
	if len(couple_contrats[couple]) > 1:
		for i  in range(len(couple_contrats[couple]) - 1, 0, -1):
			datediff = parse(couple_contrats[couple][i]["entree"]) - parse(couple_contrats[couple][i-1]["sortie"])
			if (datediff.total_seconds()/60/60/24 < 7):
				couple_contrats[couple][i-1]["sortie"] = couple_contrats[couple][i]["sortie"]
				couple_contrats[couple][i]["deleted"] = True
for couple in couple_contrats:
	for collaboration in couple_contrats[couple]:
		if "deleted" not in collaboration:
			writecollab(collaboration)
