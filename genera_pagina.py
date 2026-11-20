#!/usr/bin/env python3
"""Genera la pagina elenco degli show room di porte e finestre in Sicilia.

Deliverable C della skill territory-mapping: pagina autonoma, in italiano,
mobile-first, con KPI, filtri (provincia, priorita', gia' clienti) e ricerca.
Niente mappa: un elenco di prospect si usa filtrando, non guardando i pin.
Il template NON e' una f-string (le graffe di JS la romperebbero): si usano
segnaposto __NOME__ sostituiti in coda.
"""
import json, os

BASE = '/data/showroom-serramenti-sicilia'
elenco = json.load(open(f'{BASE}/dati.json'))
PROV = {'AG': 'Agrigento', 'CL': 'Caltanissetta', 'CT': 'Catania', 'EN': 'Enna',
        'ME': 'Messina', 'PA': 'Palermo', 'RG': 'Ragusa', 'SR': 'Siracusa', 'TP': 'Trapani'}

per_prov = {}
for a in elenco:
    per_prov[a['prov']] = per_prov.get(a['prov'], 0) + 1
prov_ord = [p for p in PROV if p in per_prov] + [p for p in per_prov if p not in PROV]

schede = []
for p in prov_ord:
    gruppo = [a for a in elenco if a['prov'] == p]
    if not gruppo:
        continue
    nome_p = PROV.get(p, p or 'Non determinata')
    righe = []
    for a in sorted(gruppo, key=lambda x: (x['priorita'], x['nome'])):
        badge = ''
        if a['cliente']:
            badge = '<span class="b cliente">GIA\' TUO CLIENTE</span>'
        elif a['priorita'] == 'A':
            badge = '<span class="b a">con sito</span>'
        elif a['priorita'] == 'C':
            badge = '<span class="b c">da verificare</span>'
        contatti = []
        if a['indirizzo']:
            contatti.append(f"<div class='r'><span class='k'>Indirizzo</span><span>{a['indirizzo']}</span></div>")
        if a['citta']:
            contatti.append(f"<div class='r'><span class='k'>Citt&agrave;</span><span>{a['citta']}</span></div>")
        if a['telefono']:
            tel = a['telefono'].replace(' ', '')
            contatti.append(f"<div class='r'><span class='k'>Telefono</span><span><a href='tel:{tel}'>{a['telefono']}</a></span></div>")
        if a['email']:
            contatti.append(f"<div class='r'><span class='k'>Email</span><span><a href='mailto:{a['email']}'>{a['email']}</a></span></div>")
        if a['sito']:
            sito = a['sito'] if a['sito'].startswith('http') else 'https://' + a['sito']
            contatti.append(f"<div class='r'><span class='k'>Sito</span><span><a href='{sito}' target='_blank' rel='noopener'>{a['sito']}</a></span></div>")
        if a['specializzazione']:
            contatti.append(f"<div class='r'><span class='k'>Specializzazione</span><span>{a['specializzazione']}</span></div>")
        if a.get('marchi'):
            stile = " style='color:#b5453a;font-weight:600'" if a.get('rivale') else ""
            contatti.append(f"<div class='r'><span class='k'>Marchi</span><span{stile}>{a['marchi']}</span></div>")
        if a['note']:
            contatti.append(f"<div class='r'><span class='k'>Note</span><span>{a['note']}</span></div>")
        righe.append(
            "<div class='card' data-prov='" + p + "' data-cliente='" + ('1' if a['cliente'] else '0') + "'"
            " data-pri='" + a['priorita'] + "'"
            " data-cerca=\"" + (a['nome'] + ' ' + a['citta'] + ' ' + a['indirizzo'] + ' ' + a['telefono'] + ' ' + a['sito'] + ' ' + a.get('marchi','') + ' ' + a.get('specializzazione','')).lower().replace('"', ' ') + "\">"
            "<div class='hd'><span class='nm'>" + a['nome'] + "</span>" + badge + "</div>"
            + ''.join(contatti) +
            (f"<div class='r'><span class='k'>Riscontro</span><span class='fonte'>{a['fonte']}</span></div>" if a['fonte'] else '') +
            "</div>")
    schede.append(f"<section class='grp' data-prov='{p}'><h2>{nome_p} <span class='cnt'>{len(gruppo)}</span></h2>{''.join(righe)}</section>")

chips_prov = ''.join(
    f"<button class='chip' data-f='{p}'>{PROV.get(p, p)} <b>{per_prov[p]}</b></button>" for p in prov_ord)

TEMPLATE = r'''<!DOCTYPE html><html lang="it"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Show room porte e finestre — Sicilia</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f2f5f8;color:#1f2937;font-size:15px;line-height:1.45}
header{background:#0f2a4a;color:#fff;padding:14px 16px 12px;position:sticky;top:0;z-index:20;box-shadow:0 2px 8px rgba(0,0,0,.15)}
h1{font-size:17px;font-weight:800;letter-spacing:.2px}
.sub{font-size:11.5px;color:#9fb6d1;margin-top:2px}
.kpi{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}
.kpi div{background:rgba(255,255,255,.11);border-radius:7px;padding:5px 10px;font-size:11px;color:#cfe0f2}
.kpi b{display:block;font-size:16px;color:#fff;font-weight:800}
.wrap{padding:10px 12px 40px;max-width:900px;margin:0 auto}
.ric{width:100%;padding:11px 13px;border:1.5px solid #d6dee8;border-radius:9px;font-size:15px;margin-bottom:9px}
.ric:focus{outline:none;border-color:#1d4e89}
.chips{display:flex;gap:5px;overflow-x:auto;padding-bottom:7px;-webkit-overflow-scrolling:touch}
.chip{flex:0 0 auto;background:#fff;border:1.5px solid #d6dee8;border-radius:16px;padding:6px 12px;font-size:12.5px;color:#1f2937;cursor:pointer;white-space:nowrap}
.chip.on{background:#1d4e89;border-color:#1d4e89;color:#fff}
.chip b{font-weight:800;opacity:.75}
.filtri{display:flex;gap:6px;margin:2px 0 10px;flex-wrap:wrap}
.tg{background:#fff;border:1.5px solid #d6dee8;border-radius:8px;padding:6px 11px;font-size:12.5px;cursor:pointer}
.tg.on{background:#15803d;border-color:#15803d;color:#fff}
.grp{margin-bottom:16px}
.grp h2{font-size:13px;text-transform:uppercase;letter-spacing:.6px;color:#0f2a4a;margin:12px 0 7px;padding-bottom:5px;border-bottom:2px solid #d6dee8;display:flex;justify-content:space-between;align-items:center}
.cnt{background:#1d4e89;color:#fff;font-size:11px;padding:1px 8px;border-radius:10px;letter-spacing:0}
.card{background:#fff;border-radius:10px;padding:11px 13px;margin-bottom:7px;box-shadow:0 1px 3px rgba(15,42,74,.07)}
.card .hd{display:flex;justify-content:space-between;gap:8px;align-items:flex-start;margin-bottom:5px}
.nm{font-weight:700;font-size:14.5px;color:#0f2a4a}
.b{font-size:9.5px;font-weight:800;padding:2px 7px;border-radius:9px;white-space:nowrap;letter-spacing:.3px}
.b.cliente{background:#dcfce7;color:#15803d}
.b.a{background:#dbeafe;color:#1d4e89}
.b.c{background:#fef3c7;color:#92400e}
.r{display:flex;gap:8px;font-size:13px;padding:1.5px 0;border-bottom:1px solid #f4f6f9}
.r:last-child{border-bottom:none}
.k{color:#9ca3af;flex:0 0 92px;font-size:11.5px;padding-top:1px}
.r a{color:#1d4e89;text-decoration:none}
.fonte{color:#9ca3af;font-size:11.5px}
.vuoto{text-align:center;color:#9ca3af;padding:30px;font-size:14px}
footer{text-align:center;font-size:11px;color:#9ca3af;padding:14px}
@media(max-width:420px){.k{flex:0 0 78px}}
</style></head><body>
<header>
  <h1>Show room porte e finestre</h1>
  <div class="sub">Elenco prospect serramenti &middot; ELLESSE RAPPRESENTANZE</div>
  <div class="kpi">
    <div><b>__TOT__</b>aziende</div>
    <div><b>__NPROV__</b>province</div>
    <div><b>__NCLI__</b>gi&agrave; clienti</div>
    <div><b>__NSITO__</b>con sito</div>
  </div>
</header>
<div class="wrap">
  <input class="ric" id="ric" type="search" placeholder="Cerca per nome, citt&agrave;, telefono, marchio...">
  <div class="chips" id="chips"><button class="chip on" data-f="*">Tutte <b>__TOT__</b></button>__CHIPS__</div>
  <div class="filtri">
    <button class="tg" id="tgCli">Solo gi&agrave; clienti</button>
    <button class="tg" id="tgA">Con sito o email</button>
  </div>
  <div id="out">__SCHEDE__</div>
  <div class="vuoto" id="vuoto" style="display:none">Nessun risultato con questi filtri.</div>
</div>
<footer>Dati da fonti pubbliche (PagineGialle, registri imprese, siti aziendali).<br>I campi vuoti sono informazioni non trovate: vanno verificati in visita.</footer>
<script>
var prov='*', soloCli=false, soloA=false;
function applica(){
  var q=document.getElementById('ric').value.toLowerCase().trim();
  var vis=0;
  document.querySelectorAll('.card').forEach(function(c){
    var ok = (prov==='*' || c.dataset.prov===prov)
          && (!soloCli || c.dataset.cliente==='1')
          && (!soloA || c.dataset.pri==='A')
          && (q==='' || c.dataset.cerca.indexOf(q)>-1);
    c.style.display = ok?'':'none';
    if(ok) vis++;
  });
  document.querySelectorAll('.grp').forEach(function(s){
    var n=s.querySelectorAll('.card:not([style*="none"])').length;
    s.style.display = n?'':'none';
    var b=s.querySelector('.cnt'); if(b) b.textContent=n;
  });
  document.getElementById('vuoto').style.display = vis?'none':'';
}
document.getElementById('ric').addEventListener('input',applica);
document.querySelectorAll('.chip').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.chip').forEach(function(x){x.classList.remove('on')});
    b.classList.add('on'); prov=b.dataset.f; applica();
  });
});
document.getElementById('tgCli').addEventListener('click',function(){
  soloCli=!soloCli; this.classList.toggle('on',soloCli); applica();});
document.getElementById('tgA').addEventListener('click',function(){
  soloA=!soloA; this.classList.toggle('on',soloA); applica();});
</script></body></html>'''

html = (TEMPLATE
        .replace('__TOT__', str(len(elenco)))
        .replace('__NPROV__', str(len([p for p in per_prov if p])))
        .replace('__NCLI__', str(sum(1 for a in elenco if a['cliente'])))
        .replace('__NSITO__', str(sum(1 for a in elenco if a['priorita'] == 'A')))
        .replace('__CHIPS__', chips_prov)
        .replace('__SCHEDE__', ''.join(schede)))

out = f'{BASE}/index.html'
open(out, 'w', encoding='utf-8').write(html)
assert '__' not in [m for m in ['__TOT__', '__CHIPS__', '__SCHEDE__'] if m in html], 'segnaposto non sostituiti'
print(f"pagina: {out}  {os.path.getsize(out):,} byte")
print(f"   {len(elenco)} aziende, {len(prov_ord)} province, "
      f"{sum(1 for a in elenco if a['cliente'])} gia' clienti, "
      f"{sum(1 for a in elenco if a['priorita']=='A')} con sito/email")
