#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, json

filepath = sys.argv[1]
with open(filepath, 'r') as xml_file:
    xml = xml_file.read()

drawMap = False
if len(sys.argv) > 2:
    drawMap = True

filterallpages = False
minl = 0
typeparl = "senateur"
lastp = "all"
if "-2013" in filepath:
    filterallpages = True
    mint = 155
    maxt = 1190
    minl = 120
    l2 = 400
elif "-2014" in filepath:
    mint = 200
    maxt = 1100
    lastp = 12
    l2 = 300
l1 = 200
l3 = 475
with open("data/senateurs.json", 'r') as f:
    senateurs = [p["senateur"] for p in json.load(f)['senateurs']]

re_gpe = re.compile(r' (UMP|SOC)$')
re_app = re.compile(r'^\s*(app|ratt)[.\s]*', re.I)
clean_app = lambda x: re_app.sub('', x)

re_particule = re.compile(r"^(.*)\s+\((d[eu'\sla]+)\)\s*$")
clean_part = lambda x: re_particule.sub(r'\2 \1', x).replace("' ", "'").replace('  ', ' ')

re_clean_bal = re.compile(r'<[^>]+>')
re_clean_spaces = re.compile(r'\s+')
clean = lambda x: re_clean_spaces.sub(' ', re_clean_bal.sub('', x)).strip()

regexps = [(re.compile(r), s) for r, s in [
    (u'[àÀ]', 'a'),
    (u'[éÉèÈêÊëË]', 'e'),
    (u'[îÎïÏ[]', 'i'),
    (u'[ôÔöÔ]', 'o'),
    (u'[ùÙûÛüÜ]', 'u'),
    (u'[çÇ]', 'c'),
]]
def clean_accents(t):
    if not isinstance(t, unicode):
        t = t.decode('utf-8')
    for r, s in regexps:
        t = r.sub(s, t)
    return t
checker = lambda x: clean(clean_accents(x)).lower().strip()

def find_parl(nom, prenom, groupe):
    res = []
    prenom = checker(prenom)
    nom = checker(nom)
    nom = nom.replace("leborgn'", "le borgn'")
    nom = nom.replace("rihan-cypel", "rihan cypel")
    for parl in parls:
        if checker(parl['nom']) == "%s %s" % (prenom, nom) or (checker(parl['nom_de_famille']) == nom and checker(parl['prenom']) == prenom):
            return parl
        if (checker(parl['nom_de_famille']) == nom and parl['groupe_sigle'] == groupe) or (checker(parl['prenom']) == prenom and checker(parl['nom_de_famille']).startswith(nom)):
            res.append(parl)
    if not res:
        sys.stderr.write("Could not find %s %s %s\n" % (typeparl, prenom, nom))
        return None
    if len(res) > 1:
        sys.stderr.write("Found too many %s %s : %s\n" % (prenom, nom, res))
    return res[0]

def unif_partis(p):
    p = p.replace('et réalités', 'et Réalité')
    p = p.replace('Ecologie', 'Écologie')
    p = p.replace("Indépendants de la France de métropole et d'Outre ", "Les Indépendants de la France métropolitaine et d'Outre-")
    p = p.replace('écologie les', 'Écologie Les')
    for w in ['Français', 'Huiraatira', 'Réunion', 'Mouvement', 'Populaire', 'Indépendantiste', 'Martiniquais' ,'Ensemble', 'République', 'Unie', 'Socialisme', 'Outre-mer', 'Réalité']:
        p = p.replace(w.lower(), w)
    p = p.replace('Non déclaré', 'Non rattaché')
    p = p.replace('Aucun parti', 'Non rattaché')
    p = p.replace(' (URCID)', '')
    p = p.replace('Union de la majorité municipale', 'La politique autrement (Union de la majorité municipale)') if p.startswith('Union') else p
    p = p.replace('PSLE-Nouveau', 'PSLE Nouveau')
    p = p.replace("Tavini Huiraatira no te ao ma'ohi (Front de libération de Polynésie)", "Front de libération de la Polynésie - Tavini Huiraatira no te ao ma'ohi")
    p = p.replace('radicaux centristes', 'radicaux, centristes')
    return p

page = 0
topvals = {}
leftvals = {}
maxtop = 0
maxleft = 0
results = []
headers = ['nom', 'prénom', 'groupe', 'rattachement_parti', 'sexe', 'département', 'id_nos%ss' % typeparl, 'url_institution']
record = ["", "", "", "", "", "", "", ""]
re_line = re.compile(r'<page number|text top="(\d+)" left="(\d+)"[^>]*font="(\d+)">(.*)</text>', re.I)
for line in (xml).split("\n"):
    #print "DEBUG %s" % line
    if line.startswith('<page'):
        page += 1
    if not line.startswith('<text'):
        continue
    attrs = re_line.search(line)
    if not attrs or not attrs.groups():
        raise Exception("WARNING : line detected with good font but wrong format %s" % line)
    font = int(attrs.group(3))
    top = int(attrs.group(1))
    if top > maxtop:
        maxtop = top
    if not font in topvals:
        topvals[font] = []
    topvals[font].append(top)
    left = int(attrs.group(2))
    if left > maxleft:
        maxleft = left
    if not font in leftvals:
        leftvals[font] = []
    leftvals[font].append(left)
    if drawMap:
        continue
    #print "DEBUG %s %s %s %s" % (font, left, top, text)
    if ((page == 1 or filterallpages) and top < mint) or ((lastp == "all" or page == lastp) and top > maxt):
        continue
    if left < minl:
        continue
    text = attrs.group(4).replace("&amp;", "&")
    if left < l1:
        record[0] = clean_part(clean(text))
    elif left < l2:
        record[1] = clean(text)
        match = re_gpe.search(record[1])
        if match:
            record[1] = re_gpe.sub('', record[1]).strip()
            record[2] = match.group(1).strip()
    elif left < l3:
        if "<b>" in text:
            a = text.split(' <b>')
            record[2] = a[0]
            record[3] = a[1]
        else:
            record[2] = clean(text)
        record[2] = clean_app(record[2]).replace("Rassemblement-", "R").replace("ÉCOL.", 'ECOLO').replace('Ecolo', 'ECOLO')
    else:
        record[3] = clean(text)
    if record[3]:
        if not "".join(record[:2]):
            tmp = clean(record[3])
            record = results.pop()
            record[3] = "%s %s" % (clean(record[3]), tmp)
        record[3] = unif_partis(record[3])
        parl = find_parl(record[0], record[1], record[2])
        if parl:
            record[4] = parl.get('sexe').encode('utf-8')
            record[5] = parl.get('nom_circo').encode('utf-8')
            record[6] = parl.get('slug').encode('utf-8')
            record[7] = parl.get('url_institution', parl.get('url_an')).encode('utf-8')
        results.append(record)
        record = ["", "", "", "", "", "", "", ""]

if not drawMap:
    print ",".join(['"%s"' % h for h in headers])
    for i in results:
        for j in range(len(i)):
            i[j] = clean(i[j])
        print ",".join([str(i[a]) if isinstance(i[a], int) else "\"%s\"" % i[a].replace('"', '""') for a,_ in enumerate(i)])

else:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import cm

    fig = plt.figure(figsize=(8.5, 12))
    ax = fig.add_subplot(111)
    ax.grid(True, fillstyle='left')
    nf = len(leftvals)
    for font in leftvals:
        color = cm.jet(1.5*font/nf)
        ax.plot(leftvals[font], topvals[font], 'ro', color=color, marker=".")
        plt.figtext((font+1.)/(nf+1), 0.95, "font %d" % font, color=color)
    plt.xticks(np.arange(0, maxleft + 50, 50))
    plt.yticks(np.arange(0, maxtop + 50, 50))
    plt.xlim(0, maxleft + 50)
    plt.ylim(0, maxtop + 50)
    plt.gca().invert_yaxis()
    mappath = filepath.replace(".xml", ".png").replace("pdfs/", "pdfmaps/")
    fig.savefig(mappath)
    fig.clf()
    plt.close(fig)

