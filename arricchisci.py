#!/usr/bin/env python3
"""Arricchisce l'elenco showroom con email, sito e MARCHI TRATTATI emersi dalla ricerca.

Formato dati: PROV|parte del nome|email|sito|marchi
  - campo vuoto = non trovato (NON sovrascrive il dato esistente)
  - i marchi vanno nel campo `marchi`, nuovo
  - `rivale` = 1 se tratta un concorrente diretto di Lelio (Finstral, Oknoplast, Drutex, Schüco, Hörmann, Velux, Qfort, Domal...)
"""
import json, re, unicodedata

BASE = '/data/showroom-serramenti-sicilia'

DATI = r"""
PA|Greco Vetri e Infissi|vetrogreco@virgilio.it|https://grecovetrieinfissi.com/|
PA|Ser.Met di Buttitta|sermet.bagheria@gmail.com|https://ser-met.it/|
PA|Sicilinfissi|info@sicilinfissi.it|https://sicilinfissi.it/|
PA|Sovan Italian Doors|info@sovanitaliandoors.it|https://www.sovanitaliandoors.it/|DAKO (esclusivista Sicilia)
PA|Tamburello Serramenti|tamburello.serramenti@gmail.com|https://www.tamburelloserramenti.it/|profili ETA 640, MINIMAL
PA|Bonanno Serramenti|info@bonannoserramenti.it|https://www.bonannoserramenti.com/|
PA|Cascino Showroom|postmaster@cascino.it|https://www.cascino.it/|Listone Giordano (store ufficiale)
PA|D'Amico Piu||https://damicopiu.it/|
PA|Expocasa||https://expocasapalermo.it/|Finstral (Studio Partner), Garofoli, Gibus
PA|FMG Serramenti Giuliano|info@giulianosnc.it|https://www.serramentigiuliano.it/|
PA|Fanara Serramenti||https://www.fanaraserramenti.com/|Oknoplast (Premium Partner)
PA|MDS Serramenti|mds.marco@virgilio.it|https://www.serramentimds.com/|
PA|Mannino Porte e Finestre|manninoporteefinestre@gmail.com|https://www.manninoporteefinestre.it/|Finstral, Garofoli, Gibus
PA|N.C. Porte e Finestre|info@ncporteefinestre.it|https://ncporteefinestre.com/|
PA|Pantaleo Porte Corazzate||https://pantaleoportecorazzate.it/|Cisa, Fichet, Iseo, Mottura (sicurezza)
PA|Scaduto Serramenti|info@scadutoserramenti.eu|https://www.scadutoserramenti.eu/|
PA|TecnoInfissi|servizioclienti@tecnoinfissisrl.com|https://www.tecnoinfissisrl.com/|FerreroLegno, Schüco, Climage, FAELUX, Finnova
PA|Vitech Servizi|vitechimpianti@libero.it|https://www.vitechservizi.it/|Came, Faac, BFT (automazioni)
PA|Greco S.r.l.||https://grecosrl.it/|Finstral (Studio Partner), Garofoli
PA|Thermo Infissi|thermoinfissi.snc@libero.it|https://thermoinfissi.net/|Schüco, Reynaers, Hörmann
PA|EmmeHome|showroom@emmehome.it|https://www.emmehome.it/|Nurith, Henryglass
PA|Gruppo Aerre|info@gruppoaerre.it|https://www.gruppoaerre.it/|
CT|Di.Tec. di Contina|ditec@nti.it|https://ditecsas.it/|Ditec
CT|Pitonio Serramenti||https://www.infissicatania.eu/|Veka
CT|Lazzaro Infissi||https://www.lazzaroinfissi.it/|AF Luxury Windows
CT|PM Serramenti|pmserramenti@outlook.it|https://serramentipm.it/|Domal, Sapa
CT|Emme2 Infissi|emme2infissi@gmail.com|https://www.emme2infissi.com/|Oknoplast (Premium)
CT|Agosta Porte e Infissi||https://www.agostaporteinfissi.it/|Nusco
CT|Biondi Porte|info@biondiporte.com|https://biondiporte.com/|
CT|Bonforte Door|fbonforte@gmail.com|https://www.bonfortedoor.it/|Garofoli, Flessya
CT|Celi Serramenti|info@celiserramenti.it|https://www.celiserramenti.it/|Domal
CT|EkoWood Catania|ekowood@ekowood.it|https://www.ekowood.it/|EkoWood (marchio proprio)
CT|Mondial Chiave|mondialchiave@yahoo.com|https://mondialchiave.it/|
CT|Sirwood|sifomsrl@gmail.com|https://www.sirwood.it/|
CT|Spazio Casa Srl||https://spaziocasasrl.it/|Finstral (Studio Partner)
CT|Stylcasa Center||https://www.stylcasacenter.com/|Ferrero Legno, Fossati, Listone Giordano
CT|Zeroabita|info@zeroabita.it|https://zeroabita.it/|Finstral (Studio Partner)
CT|Cardillo Alluminio|info@cardillo.it|https://www.cardillo.it/|
CT|MPS Showroom||https://mpsedilizia.com/|Velux, Garofoli, Fossati, Tecnoscale
CT|Strano Serramenti|info@stranoserramenti.it|https://stranoserramenti.it/|
CT|Privitera Serramenti|info@priviteraserramenti.it|https://priviteraserramenti.it/|
CT|Finporte|finportect@tiscali.it|https://finportecatania.com/|
CT|Porte & Co. Store|info@porteco.store.it|https://porteco.store/|Bertolotto
CT|Pronta Porta Puglisi|prontaporta@yahoo.it|https://www.prontaporta.com/|
CT|FGS Automatismi|info@fgsautomatismi.it|https://fgsautomatismi.it/|Ditec, Aprimatic
ME|Nuova Fab|nuovafab@virgilio.it|https://www.nuovafab.com/|
ME|Santangelo Giuseppe|serrament.santangelo@libero.it|https://www.serramentisantangelo.com/|
ME|Santoro Group|info@santorogroup.eu|https://santorogroup.eu/|Schüco, Pivato, Oikos, Hansen
ME|Giglia Infissi|infissigiglia@gmail.com|https://infissigiglia.wixsite.com/infissigiglia|
ME|M.T. Infissi||https://mtinfissi.com/|Schüco, Hörmann, Reynaers, Alumil, Veka
ME|Metalsider|info@metalsidersrl.it|https://metalsidersrl.it/|
ME|Greco Serramenti|info@grecoserramenti.com|https://www.grecoserramenti.it/|Schüco (partner posa qualità)
ME|Tecnosystem|tecno_systemsrl@libero.it||
ME|Arte Infissi|arteinfissibombara@gmail.com|https://www.arteinfissibombara.it/|
ME|G&G Serramenti|serramentigeg@gmail.com|https://www.gegserramenti.com/|
ME|Marino Infissi|marinoinfissisrls@gmail.com||
ME|Serramenti Galletta|loretog@hotmail.it|https://www.serramentigalletta.com/|
ME|Serramenti Margherita|serramentimargherita@gmail.com||
ME|Zappia Giuseppe|portecorazzatezappia@gmail.com|https://www.zappiasicurezza.it/|
ME|Cirino Infissi|cirino.infissi@virgilio.it|https://cirinoinfissi.it/|
ME|TEC di Lazzaro|tecdilazzaro@inwind.it|https://tecdilazzaro.it/|Metra, Sapa, Original Systems
ME|Archiporte|info@archiporte.it|https://www.archiporte.it/|Bertolotto, Tecnoallumil
ME|Bucca Antonino|info@antoninobucca.com|https://www.antoninobucca.com/|
ME|Cannistra Infissi|info@cannistra.it|https://cannistra.it/|Domal, Sciuker, Veka, Technal
ME|Donia Serramenti|doniaserramenti@gmail.com|https://doniaserramenti.com/|
SR|Tutto Infissi Augusta|augusta@tuttoinfissigroup.it|https://tuttoinfissigroup.it/augusta/|Drutex (rivenditore ufficiale)
SR|Tutto Infissi Avola|avola@tuttoinfissigroup.it|https://tuttoinfissigroup.it/avola/|Drutex (rivenditore ufficiale)
SR|Tutto Infissi Siracusa|siracusa@tuttoinfissigroup.it|https://tuttoinfissigroup.it/siracusa/|Drutex (rivenditore ufficiale)
SR|Guardo Serramenti|info@guardoserramenti.it|https://www.guardoserramenti.it/|
SR|Martogli Project|info@martogli.it|https://www.martogligroup.it/|Oknoplast, Velux, Bertolotto, Oikos
SR|SG Serramenti|info@sgserramentifloridia.it|https://www.sgserramentifloridia.it/|
SR|TICO Design|ticodesign21@gmail.com|https://www.ticosrl.com/|Nikita
SR|R.S. Infissi|infissi.schembri@alice.it|https://www.rsinfissi.it/|
SR|Amore Infissi|amore.infissi@gmail.com|https://www.amoreinfissi.it/|
SR|ARTinfissi|info@art-infissi.com|https://www.art-infissi.com/|Fakro, Nusco, Gardesa, AGB, Alphacan, Bettio
SR|Cannata Serramenti|giuseppecannatasr@virgilio.it|https://www.cannataserramentisr.com/|
SR|Cataldo Spazio Casa|cataldospaziocasasrl@gmail.com|https://www.cataldospaziocasa.com/|
SR|Door Style|lorena87.mangiafico@gmail.com|https://www.doorstyle.it/|I Nobili
SR|Euroinfissi Siracusa|info@euroinfissisiracusa.it|https://www.euroinfissisiracusa.com/|
SR|Pisano Serramenti|info@pisanoserramenti.com|https://www.pisanoserramenti.com/|
SR|Porte d'Autore|porteautore@libero.it|https://www.portedautore.it/|HenryGlass
SR|Prato Infissi|infopratoinfissi@gmail.com|https://www.pratoinfissi-sr.com/|Metra
SR|Vetreria Giarratana|info@vetreriagiarratana.com|https://www.vetreriagiarratana.com/|Faraone, Kira, Flessya, Eikona
RG|Cubisystem|cubisystem66@gmail.com|https://cubisystem.it/|
RG|Milito Infissi|info@militoinfissilegno.com|https://www.militoinfissilegno.com/|
RG|MR Infissi|info@mrinfissi.it|https://www.mrinfissi.it/|Metra (show room autorizzato)
RG|Masetti|info@infissi-masetti.it|https://www.infissi-masetti.it/|
RG|Colombo Store|info@colombostore.design|https://www.colombostore.design/|WND
RG|Corrado Serramenti|corradoserramenti@gmail.com|https://corradoserramenti.it/|Korus
RG|Livia Infissi|info@liviainfissilg.it|https://www.liviainfissilg.it/|Qfort
RG|MP Infissi|pieromur94@gmail.com|https://www.mpinfissimodica.it/|
RG|Open Doors|info@open-doors.it|https://www.open-doors.it/|
RG|Infantino Arredi|info@infantinoarredisrl.it|https://www.infantinoarredisrl.it/|
RG|COMET dei F.lli Cappello|cometragusa@gmail.com|https://www.cometragusa.com/|Schüco, Metra
RG|Faser|info@faser.srl|https://www.faser.srl/|
RG|Infissi Bracchitta|info@infissibracchitta.it|https://infissibracchitta.it/|
RG|Meca Infissi|info@mecainfissi.it|https://www.mecainfissi.it/|
RG|Metalnova Ragusa|metalnovarg@tiscali.it|https://www.metalnovaragusa.it/|Schüco, Bertolotto
RG|Non Solo Porte|info@nonsoloporteragusa.it|https://nonsoloporteragusa.it/|Finstral, Velux, Hörmann, Garofoli
RG|Raialfs|raialfs@gmail.com|https://www.officineraialfs.com/|Fossati, Roger
RG|Scribano Serramenti|gi.scribano@tiscali.it|https://www.scribanoserramenti.it/|
TP|Centro Porte e Infissi|info@centroporteeinfissi.com|https://www.centroporteeinfissi.com/|Korus, Cosfer, Ermetika, Flessya, Oskura
TP|Ciacio Infissi|info@ciacioinfissi.com|https://www.ciacioinfissi.it/|Schüco, Velux, Garofoli, Lualdi, Griesser
TP|SCENARI by LegnoCasa|info@legnocasainfissi.com|https://www.legnocasainfissi.com/|
TP|Garofalo Infissi|info@garofaloinfissi.it|https://www.garofaloinfissi.it/|Biemme, Roto, Schüco, Hörmann, Cibiesse, Comas
TP|Osam Infissi|info@osam-infissi.it|https://www.osaminfissi.com/|
TP|GSM Sistemi|info@gsm-sistemi.it|https://gsm-sistemi.it/|Roto, Bettio, Fossati, Colò
TP|Ales Infissi|info@alesinfissi.it|https://alesinfissi.it/|Domal, Alsistem, Bettio, MV Line
TP|Domus Portae|info@domusportae.it|https://domusportae.it/|Finstral, Velux, Hörmann, Garofoli, Alias
TP|Parrinello M. & Angileri|parrinellosnc@tiscali.it|https://www.parrinelloinfissi.com/|Bertolotto
TP|AluMetal|alumetal_ds@yahoo.com||
TP|D'Aguanno Infissi|||Korus, Hörmann
TP|Fodera Infissi|foderainfissi@hotmail.com|https://foderainfissi.com/|Oknoplast
TP|Di Via Serramenti|info@diviaserramenti.com|https://www.diviaserramenti.com/|Biemme, Finstral, Velux, Garofoli, Scrigno
TP|Eureka Infissi|info@eurekainfissi.it|https://www.eurekainfissi.it/|Ferrero Legno, Nurith, Silvelox, MV Line
TP|House Evolution||https://www.houseevolutioninfissi.it/|Oknoplast (Premium Partner)
TP|La Grutta Infissi|infissilagrutta@yahoo.com|https://www.lagruttainfissi.it/|
TP|Messina Agostino|messinaagostino@libero.it|https://www.messinaagostinoinfissi.com/|
TP|Vitaggio Infissi|vitaggioinfissi@gmail.com|https://vitaggioinfissi.com/|Bertolotto, Domal, Alumil, Veka
AG|Saell Porte Infissi|info@saell.it|http://www.saell.axeleroweb.it|Nurith, Korus, Bertolotto, Isomax
AG|Grisafi Italserramenti|info@italserramenti.com|https://www.italserramenti.com/|
AG|Mediterranea Serramenti|info@mediterraneaserramenti.it|https://mediterraneaserramenti.it/|
AG|Porte d'Interni Giardina|info@giardinaporte.it|https://giardinaporte.it/|Dierre, Ermetika, Rema, Alpi, Scrigno
AG|Cacciatore Infissi|cacciatoreinfissi@tiscali.it|https://cacciatoreinfissi.it/|
AG|Centro Infissi di Canicatti|centroinfissisnc@alice.it|https://www.centroinfissisnc.it/|
AG|DM Porte|dmuloneporte@gmail.com||
AG|Li Calzi Infissi|info@licalziinfissi.it|https://www.licalziinfissi.it/|Infixo, Naco
AG|MSC Centro Sicurezza|info@msccentrosicurezza.it|https://www.msccentrosicurezza.com/|
AG|Porte Russo|porterussosrls@gmail.com|https://porterusso.it/|
AG|Alluminio Matina|ingrossoamhezion@gmail.com|https://www.alluminiomatina.com/|
AG|Novara Infissi|infissinovara@gmail.com|https://infissinovara.com/|
AG|Riportella Infissi|agustinriportella@alice.it|http://riportellainfissi.it|
AG|Bonaccolta Infissi|mbonaccolta@gmail.com|https://www.bonaccoltainfissi.com/|
AG|Prodalf Infissi|info@prodalf.com|https://www.prodalf.com/|ALsistem (partner ufficiale)
AG|Basile Infissi|cobainfissisrl@gmail.com|https://www.basileinfissi.com/|Twin Systems
AG|Bilello Infissi|bilellomichele@libero.it|https://www.bilelloinfissi.it/|Finstral (Studio Partner)
AG|Serramenti Pizzo|serramentipizzo@gmail.com|https://www.pizzoserramenti.it/|
CL|Nastasi Serramenti|info.nastasiserramenti@gmail.com|https://nastasiserramenti.it/|Qfort, Simar
CL|Bocchieri Costruzioni|info@bocchierialluminio.it|https://bocchierialluminio.it/|Dierre (esclusivista di zona)
CL|Montarredi Technical|info@montarreditechnicalservice.com|https://montarreditechnicalservice.com/|Ditec
CL|S&L Infissi Vara|essevara@virgilio.it|https://www.slvarainfissi.it/|
CL|Camilleri & Terranova|camillerieterranova@gmail.com|https://www.camillerieterranova.com/|
CL|Nuova Infissi Pirillo|infissi.pirillo@gmail.com|https://www.nuovainfissipirillo.it/|
CL|CasaEcoClima|piertanino.lobue@gmail.com|https://www.casaecoclima.it/|
CL|F.G. Metal|fgmetalsnc@gmail.com|https://www.fgmetal.it/|
CL|IN.VET. di Falzone|invetvetri@gmail.com|https://www.invetinfissievetri.it/|Saint-Gobain, Alsistem, Twin System
CL|System Infissi|systeminfissi@virgilio.it|https://www.systeminfissi.it/|Dierre, AGB, Alphacan, Sistem
CL|Teco Sistemi Casa|info@tecosistemicasa.it|https://tecosistemicasa.it/|Oknoplast, Scavolini
EN|Martesama Porte|info@martesamaporte.com|https://www.martesamaporte.com/|
EN|F.lli Barbagallo|infissi.barbagallo@gmail.com|https://www.infissibarbagallo.com/|
EN|Modafferi Infissi|info@modafferi.biz|https://www.modafferiinfissi.com/|
EN|Open Door|antoniolop@tiscalinet.it||Climage, Sidel
EN|AS Infissi di Sanfilippo|Aesseinfissi@hotmail.com|https://www.infissisanfilippo.com/|Flessya
EN|Soluzione Infissi|soluzioneinfissisrl@gmail.com|https://soluzioneinfissisrl.it/|Nikita
EN|Spazio Casa S.r.l.|spaziocasanicosia@virgilio.it|https://spaziocasasrl.it/|Finstral (partner dal 2002)
EN|Bielle|info@biellesrl.eu|https://biellesrl.eu/|
EN|Arena Costruzione Infissi|info@arenacostruzioneinfissi.it|https://www.arenacostruzioneinfissi.it/|Schüco, Kömmerling, Isomax, Sistem
EN|Sciammacca Infissi||https://sciammaccainfissi.it|Eikona
EN|R.D. Infissi|r.d.infissi@tin.it|https://rdinfissi.it|Schüco, Dierre, Metra, Eterma
"""

RIVALI = ('finstral', 'oknoplast', 'drutex', 'schüco', 'schuco', 'hörmann', 'hormann',
          'velux', 'qfort', 'domal', 'reynaers', 'kommerling', 'kömmerling')


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '')).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]', '', s.lower())


def contiene(nome_full, frammento):
    return norm(frammento) in norm(nome_full)


d = json.load(open(f'{BASE}/dati.json'))
per_nome = {}
for a in d:
    per_nome.setdefault(norm(a['nome'])[:18], a)

agg = {'email': 0, 'sito': 0, 'marchi': 0, 'rivale': 0, 'non_trovati': []}
for riga in DATI.strip().split('\n'):
    parti = riga.split('|')
    if len(parti) < 5:
        continue
    prov, fram, email, sito, marchi = parti[0], parti[1], parti[2], parti[3], parti[4]
    # trova l'azienda: match per sottostringa normalizzata sulla provincia giusta
    a = None
    for x in d:
        if x['prov'] == prov and contiene(x['nome'], fram):
            a = x
            break
    if a is None:
        agg['non_trovati'].append(f'{prov} {fram}')
        continue
    if email and not a.get('email'):
        a['email'] = email; agg['email'] += 1
    if sito and not a.get('sito'):
        a['sito'] = sito; agg['sito'] += 1
    if marchi:
        a['marchi'] = marchi; agg['marchi'] += 1
        if any(r in marchi.lower() for r in RIVALI):
            a['rivale'] = 1; agg['rivale'] += 1
for a in d:
    a.setdefault('marchi', '')
    a.setdefault('rivale', 0)

json.dump(d, open(f'{BASE}/dati.json', 'w'), ensure_ascii=False, indent=1)
print(f"arricchimento applicato su {len(d)} aziende")
print(f"   email aggiunte      : {agg['email']}")
print(f"   siti aggiunti       : {agg['sito']}")
print(f"   marchi inseriti     : {agg['marchi']}")
print(f"   di cui con concorrente: {agg['rivale']}")
print(f"   totale con email    : {sum(1 for a in d if a['email'])}/{len(d)}")
print(f"   totale con marchi   : {sum(1 for a in d if a['marchi'])}/{len(d)}")
if agg['non_trovati']:
    print(f"   NON ABBINATI ({len(agg['non_trovati'])}): {agg['non_trovati']}")
