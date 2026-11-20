#!/usr/bin/env python3
"""Unisce i risultati dei 9 agenti (show room porte e finestre per provincia) in dati.json.

Regole:
  - normalizza la provincia (gli agenti scrivono "Catania (CT)", "Trapani", "CT"...)
  - deduplica per nome normalizzato (lo stesso tendagista esce su piu' portali)
  - incrocia con i clienti GIA' in portafoglio e li marca (campo `cliente`)
  - nessun dato inventato: i campi vuoti restano vuoti
"""
import json, re, os, glob, csv

BASE = '/data/showroom-serramenti-sicilia'
RAW = f'{BASE}/raw'
PROV = {'AG': 'Agrigento', 'CL': 'Caltanissetta', 'CT': 'Catania', 'EN': 'Enna',
        'ME': 'Messina', 'PA': 'Palermo', 'RG': 'Ragusa', 'SR': 'Siracusa', 'TP': 'Trapani'}
SIGLA = {v.lower(): k for k, v in PROV.items()}


def norm(s):
    s = re.sub(r'[^A-Z0-9 ]', ' ', (s or '').upper())
    return re.sub(r'\s+', ' ', s).strip()


# parole di settore e parole comuni: NON bastano da sole a identificare un'azienda,
# altrimenti 'Infissi Costa' aggancia 'Infissi Cutrone' (falso positivo verificato)
GENERICI = {
    'TENDE', 'TENDA', 'TENDAGGI', 'TENDAGGIO', 'INFISSI', 'INFISSO', 'SERRAMENTI', 'SERRAMENTO',
    'PORTE', 'PORTA', 'FINESTRE', 'FINESTRA', 'PERGOLE', 'PERGOLA', 'PERGOLATI', 'PERGOTENDE',
    'VENEZIANE', 'ZANZARIERE', 'OSCURANTI', 'AVVOLGIBILI', 'TAPPARELLE', 'SCHERMATURE', 'SOLARI',
    'ARREDI', 'ARREDO', 'ARREDAMENTO', 'DESIGN', 'STORE', 'SHOWROOM', 'CENTRO', 'SERVICE',
    'GROUP', 'IMPRESA', 'DITTA', 'COSTRUZIONI', 'EDIL', 'EDILIZIA', 'DECOR', 'STILE', 'CASA',
    'HOME', 'NUOVA', 'NUOVO', 'FLLI', 'F', 'LLI', 'S', 'C', 'E', 'GLOBAL', 'ITALIA', 'SICILIA',
}


def parole(s):
    n = norm(s)
    for stop in ('SRL', 'SRLS', 'SNC', 'SAS', 'SPA', 'SRL', 'DI', 'DEL', 'DELLA', 'DELLO',
                 'DEI', 'DEGLI', 'E', 'C', '&', 'IL', 'LA', 'LO'):
        n = re.sub(rf'\b{stop}\b', ' ', n)
    return n.split()


def chiave(s):
    """chiave di deduplica: prime 3 parole significative, senza forma societaria"""
    return ' '.join(parole(s)[:3])


def chiavi_match(s):
    """chiavi per l'incrocio coi clienti.

    REGOLE (verificate sui falsi positivi reali):
    - niente parole di una sola lettera: 'PORTE D' faceva combaciare due aziende diverse
    - chiave di almeno 8 caratteri: 'M T' faceva combaciare M.T. Infissi con M.T. Tende
    - parole di settore escludibili: 'INFISSI COSTA' non deve agganciare 'INFISSI CUTRONE'
    """
    w = [x for x in parole(s) if len(x) > 1]
    if not w:
        return []
    k = []
    due = ' '.join(w[:2])
    if len(due) >= 8:
        k.append(due)
    if len(w[0]) >= 8 and w[0] not in GENERICI:
        k.append(w[0])
    return k


def provincia_di(p, citta=''):
    """normalizza la provincia: accetta sigla, nome intero, 'Nome (XX)', o la ricava dalla citta'"""
    p = (p or '').strip()
    m = re.search(r'\(([A-Z]{2})\)', p)
    if m and m.group(1) in PROV:
        return m.group(1)
    pu = norm(p)
    if pu in PROV:
        return pu
    for nome, sig in SIGLA.items():
        if nome in p.lower():
            return sig
    for sig, nome in PROV.items():
        if norm(nome) in norm(citta):
            return sig
    return ''


# --- clienti gia' in portafoglio (per marcare i prospect) ---
clienti_noti = {}
for f, campi in [('/data/followup-clienti/clienti.json', ('nome', 'rag', 'cliente')),
                 ('/data/cruscotto-appuntamenti/clienti.json', ('rag', 'nome')),
                 ('/data/configuratore-cherubini/data/clienti.json', ('nome',))]:
    if not os.path.exists(f):
        continue
    d = json.load(open(f))
    if isinstance(d, dict):
        d = d.get('clienti', list(d.values()))
    for r in d:
        for c in campi:
            v = r.get(c) if isinstance(r, dict) else None
            if v:
                for kk in chiavi_match(v):
                    clienti_noti.setdefault(kk, str(v))
                break

# --- raccolta ---
aziende = {}
scarti = []
for f in sorted(glob.glob(f'{RAW}/*.json')):
    try:
        d = json.load(open(f))
    except Exception as e:
        scarti.append((os.path.basename(f), f'JSON non leggibile: {e}'))
        continue
    lista = d.get('aziende', d if isinstance(d, list) else [])
    prov_file = provincia_di(d.get('provincia', ''))
    for a in lista:
        nome = (a.get('nome') or '').strip()
        if not nome:
            continue
        k = chiave(nome)
        prov = provincia_di(a.get('provincia', ''), a.get('citta', '')) or prov_file
        r = {
            'nome': nome,
            'citta': (a.get('citta') or '').strip(),
            'prov': prov,
            'indirizzo': (a.get('indirizzo') or '').strip(),
            'telefono': (a.get('telefono') or '').strip(),
            'email': (a.get('email') or '').strip(),
            'sito': (a.get('sito') or '').strip(),
            'specializzazione': (a.get('specializzazione') or '').strip(),
            'note': (a.get('note') or '').strip(),
            'fonte': (a.get('fonte') or '').strip(),
            'cliente': next((clienti_noti[kk] for kk in chiavi_match(nome) if kk in clienti_noti), ''),
            'provincia_agente': d.get('provincia', ''),
        }
        if k in aziende:
            v = aziende[k]
            for campo in ('citta', 'prov', 'indirizzo', 'telefono', 'email', 'sito',
                          'specializzazione', 'note', 'fonte'):
                if not v[campo] and r[campo]:
                    v[campo] = r[campo]
            if r['nome'] not in v['nome']:
                v['nome'] = v['nome'] if len(v['nome']) >= len(r['nome']) else r['nome']
        else:
            aziende[k] = r

elenco = sorted(aziende.values(), key=lambda x: (x['prov'] or 'ZZ', x['citta'], x['nome']))
for a in elenco:
    a['priorita'] = 'A' if (a['sito'] or a['email']) else ('B' if a['telefono'] else 'C')

json.dump(elenco, open(f'{BASE}/dati.json', 'w'), ensure_ascii=False, indent=1)

# --- report ---
per_prov = {}
for a in elenco:
    per_prov[a['prov'] or '(non determinata)'] = per_prov.get(a['prov'] or '(non determinata)', 0) + 1
print(f"SHOW ROOM PORTE E FINESTRE SICILIA: {len(elenco)} aziende uniche")
for p in sorted(per_prov):
    print(f"   {PROV.get(p, p):<20} {per_prov[p]:>4}")
print(f"\n   con sito o email : {sum(1 for a in elenco if a['priorita']=='A')}")
print(f"   con telefono     : {sum(1 for a in elenco if a['priorita']=='B')}")
print(f"   da verificare    : {sum(1 for a in elenco if a['priorita']=='C')}")
gia = [a for a in elenco if a['cliente']]
print(f"   GIA' TUOI CLIENTI: {len(gia)}")
for a in gia:
    print(f"      {a['nome'][:44]:<44} = {a['cliente']}")
if scarti:
    print(f"\n   file con problemi: {scarti}")
print(f"\nsalvato {BASE}/dati.json")
