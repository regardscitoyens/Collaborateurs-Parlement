#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, json

filepath = sys.argv[1]
with open(filepath, 'r') as xml_file:
    xml = xml_file.read()

drawMap = False
if len(sys.argv) > 2:
    drawMap = True

minl = 100
maxt = 730
l1 = 200
if "senateurs_collaborateurs" in filepath:
    mint = 150
    senateursfirst = True
elif "collaborateurs_senateurs" in filepath:
    mint = 130
    senateursfirst = False

with open("data/senateurs.json", 'r') as f:
    senateurs = [p["senateur"] for p in json.load(f)['senateurs']]

Mme = r"^M[.mle]+\s+"
clean_Mme = re.compile(Mme)

particule = r"d[euils'\s]+"
re_particule = re.compile(r"^(.*)\s+(%s)$" % particule)
clean_part = lambda x: re_particule.sub(r'\2 \1', x).replace("' ", "'").replace('  ', ' ')

re_clean_bal = re.compile(r'<[^>]+>')
re_clean_dash = re.compile(r'\s*-\s*')
re_clean_spaces = re.compile(r'\s+')
clean = lambda x: re_clean_spaces.sub(' ', re_clean_dash.sub('-', re_clean_bal.sub('', x))).strip()

regexps = [(re.compile(r), s) for r, s in [
    (u'[àÀâÂ]', 'a'),
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

reorder = lambda p: clean_part(checker("%s %s" % (p['nom_de_famille'], p['prenom'])))

maj = ur"A-ZÀÂÉÈÊËÎÏÔÖÙÛÜÇ"
re_name = re.compile(ur"(%s)((?:(?:%s)?[%s'\-]+\s+)+)([%s][a-zàâéèêëîïôöùûüç].*)$" % (Mme, particule, maj, maj))

def split_name(name):
    match = re_name.search(name.decode('utf-8'))
    if not match:
        sys.stderr.write("WARNING: could not split name %s\n" % name)
        return name, "", ""
    sexe = "H" if "." in match.group(1) else "F"
    nom = match.group(2).strip()
    prenom = match.group(3).strip()
    return nom, prenom, sexe

def split_collab(record):
    record[5], record[6], record[7] = split_name(record[4])

def find_parl(record):
    nom = checker(clean_Mme.sub('', record[0]))
    nom = nom.replace("conway-mouret", "conway mouret")
    nom = nom.replace("deromedi jacqueline", "deromedi jacky")
    nom = nom.replace("yonnet-salvator evelyne", "yonnet evelyne")
    record[1], record[2], record[3] = split_name(record[0])
    for parl in senateurs:
        if reorder(parl) == nom:
            record[0] = parl["nom"]
            #record[1] = parl["nom_de_famille"]
            #record[2] = parl["prenom"]
            #record[3] = parl["sexe"]
            record[8] = parl["url_nossenateurs_api"].replace('json', 'xml')
            record[9] = parl["url_institution"]
            return
    sys.stderr.write("Could not find %s\n" % nom)

# TODO Split collabs in nom/prénom/sexe

page = 0
topvals = {}
leftvals = {}
maxtop = 0
maxleft = 0
results = []
headers = ['sénateur', 'nom_sénateur', 'prénom_sénateur', 'sexe_sénateur', 'collaborateur', 'nom_collaborateur', 'prénom_collaborateur', 'sexe_collaborateur', 'url_api_nossénateurs', 'url_sénat']
record = ["", "", "", "", "", "", "", "", "", ""]
re_line = re.compile(r'<page number|text top="(\d+)" left="(\d+)"[^>]*font="(\d+)">(.*)</text>', re.I)
for line in (xml).split("\n"):
    #print >> sys.stderr, "DEBUG %s" % line
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
    if top < mint or top > maxt:
        continue
    if left < minl:
        continue
    text = attrs.group(4).replace("&amp;", "&")
    if left < l1:
        val = clean(text)
        idx = 0 if senateursfirst else 4
        if " Mme " in val:
            sys.stderr.write("WARNING: splitting %s\n" % val)
            idx2 = 4 if senateursfirst else 0
            record[idx], record[idx2] = val.split(" Mme ")
            record[idx2] = "Mme " + record[idx2]
            find_parl(record)
            split_collab(record)
            results.append(list(record))
            continue
        record[idx] = val
        if senateursfirst:
            find_parl(record)
        else:
            split_collab(record)
    else:
        idx = 4 if senateursfirst else 0
        record[idx] = clean(text)
        if not senateursfirst:
            find_parl(record)
        else:
            split_collab(record)
        results.append(list(record))

if not drawMap:
    print ",".join(['"%s"' % h for h in headers])
    for i in sorted(results, key=lambda x: "%s - %s" % (x[0].encode('utf-8'), x[4])):
        for j in range(len(i)):
            i[j] = clean(i[j])
            try:    i[j] = i[j].encode('utf-8')
            except: pass
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

