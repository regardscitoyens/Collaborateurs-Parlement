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
mint = 130
maxt = 730
l1 = 200
parls_type = "senateurs"
parls_first = True
if "senateurs_collaborateurs" in filepath:
    mint = 150
elif "collaborateurs_senateurs" in filepath:
    parls_first = False
elif "deputes_collaborateurs" in filepath:
    parls_type = "deputes"
    minl = 50
    mint = 85
    maxt = 800
    l1 = 75
    l2 = 150
    l3 = 250
    l4 = 275
    l5 = 350
parl_type = parls_type.rstrip("s")

with open("data/%s.json" % parls_type, 'r') as f:
    parls = [p[parl_type] for p in json.load(f)[parls_type]]

Mme = r"^M[.mle]+\s+"
clean_Mme = re.compile(Mme)

re_clean_bal = re.compile(r'<[^>]+>')
re_clean_dash = re.compile(r'\s*-\s*')
re_clean_spaces = re.compile(r'\s+')
clean = lambda x: re_clean_spaces.sub(' ', re_clean_dash.sub('-', re_clean_bal.sub('', x))).strip()

regexps = [(re.compile(r), s) for r, s in [
    (u'[àÀâÂ]', 'a'),
    (u'[éÉèÈêÊëË]', 'e'),
    (u'[îÎïÏ]', 'i'),
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

reorder = lambda p: checker("%s %s" % (p['nom'].replace("%s " % p['prenom'], ""), p['prenom']))

maj = ur"A-ZÀÂÉÈÊËÎÏÔÖÙÛÜÇ"
particule = r"d[euils'\s]+"
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

def find_parl(record, splitted=False):
    nom = checker(clean_Mme.sub('', record[0]))
    nom = nom.replace("deromedi jacqueline", "deromedi jacky")
    nom = nom.replace("yonnet-salvator evelyne", "yonnet evelyne")
    nom = nom.replace("laufoaulu lopeleto", "laufoaulu robert")
    nom = nom.replace("azerot bruno", "azerot bruno nestor")
    nom = nom.replace("de la verpillere charles", "de la verpilliere charles")
    nom = nom.replace("debre bernard andre", "debre bernard")
    nom = nom.replace("destans jean", "destans jean-louis")
    nom = nom.replace("le borgn pierre-yves", "le borgn' pierre-yves")
    nom = nom.replace("vlody jean-jacques", "vlody jean jacques")
    nom = nom.replace("zimmermann marie jo", "zimmermann marie-jo")
    if not splitted:
        record[1], record[2], record[3] = split_name(record[0])
    for parl in parls:
        if reorder(parl) == nom:
            record[0] = parl["nom"]
            #record[1] = parl["nom_de_famille"]
            #record[2] = parl["prenom"]
            #record[3] = parl["sexe"]
            record[8] = parl["url_nos%s_api" % parls_type].replace('json', 'xml')
            record[9] = parl.get("url_institution", parl.get("url_an", ""))
            return
    sys.stderr.write("Could not find %s -> %s\n" % (record[0], nom.encode('utf-8')))

# Reorder xml lines
xml_ordered = ""
page_lines = []
re_ordline = re.compile(r'<(page|text) (?:top="(\d+)" left="(\d+)"[^>])?', re.I)
ordline = lambda l: [int(v or 0) if i else v for i, v in enumerate(re_ordline.search(l).groups())]
for line in (xml).split("\n"):
    if line.startswith('<text'):
        page_lines.append(line)
    elif line.startswith('</page'):
        xml_ordered += "\n".join(sorted(page_lines, key=ordline))
        page_lines = []

topvals = {}
leftvals = {}
maxtop = 0
maxleft = 0
results = []
headers = ['parlementaire', 'nom_parlementaire', 'prénom_parlementaire', 'sexe_parlementaire', 'collaborateur', 'nom_collaborateur', 'prénom_collaborateur', 'sexe_collaborateur', 'url_api_RC', 'url_institution']
record = ["", "", "", "", "", "", "", "", "", ""]
re_line = re.compile(r'<page number|text top="(\d+)" left="(\d+)"[^>]*font="(\d+)">(.*)</text>', re.I)
re_tosplit = re.compile(r'^(.*) ((?:M.|Mme) .*)$')
re_collabtosplit = re.compile(r'^\s*(M\.|Mme) (.+)$')
sexize = lambda val: "H" if val == "M." else "F"
for line in (xml_ordered).split("\n"):
    #print >> sys.stderr, "DEBUG %s" % line
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
    # Handle députés
    if parls_type == "deputes":
        val = clean(text)
        if left < l1:
            record[3] = val
        elif left < l2:
            record[2] = val
        elif left < l3:
            record[1] = val
            record[0] = record[3] + " " + record[1] + " " + record[2]
            find_parl(record, splitted=True)
            record[3] = sexize(record[3])
        elif left < l4:
            splitted = re_collabtosplit.search(val)
            if splitted:
                record[7] = splitted.group(1)
                record[6] = splitted.group(2)
            else:
                record[7] = val
        elif left < l5:
            record[6] = val
        else:
            record[5] = val
            record[4] = record[7] + " " + record[5] + " " + record[6]
            record[7] = sexize(record[7])
            results.append(list(record))
        continue
    # Handle sénateurs
    if left < l1:
        val = clean(text)
        idx = 0 if parls_first else 4
        tosplit = re_tosplit.search(val)
        if tosplit:
            sys.stderr.write("WARNING: splitting %s\n" % val)
            idx2 = 4 if parls_first else 0
            record[idx], record[idx2] = tosplit.groups()
            find_parl(record)
            split_collab(record)
            results.append(list(record))
            continue
        record[idx] = val
        if parls_first:
            find_parl(record)
        else:
            split_collab(record)
    else:
        idx = 4 if parls_first else 0
        record[idx] = clean(text)
        if not parls_first:
            find_parl(record)
        else:
            split_collab(record)
        results.append(list(record))

if not drawMap:
    print ",".join(['"%s"' % h for h in headers])
    for i in sorted(results, key=lambda x: ("%s %s - %s %s" % (x[1], x[2], x[5], x[6])).lower()):
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

