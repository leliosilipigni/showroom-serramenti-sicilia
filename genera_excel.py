#!/usr/bin/env python3
import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
BASE='/data/showroom-serramenti-sicilia'
d=json.load(open(f'{BASE}/dati.json'))
PROV={'AG':'Agrigento','CL':'Caltanissetta','CT':'Catania','EN':'Enna','ME':'Messina','PA':'Palermo','RG':'Ragusa','SR':'Siracusa','TP':'Trapani'}
COLS=[('Prov.',6),('Provincia',13),('Azienda',38),('Città',18),('Indirizzo',34),('Telefono',20),('Email',32),('Sito',30),('Marchi trattati',44),('Specializzazione',40),('Note',34),('Già cliente',11),('Fonte',22)]
wb=Workbook(); ws=wb.active; ws.title='Rivenditori porte e finestre'
hf=PatternFill('solid',fgColor='1C3B5A'); hfont=Font(color='FFFFFF',bold=True,size=10)
alt=PatternFill('solid',fgColor='F4F7FA'); cli=PatternFill('solid',fgColor='D8F0DF'); riv=PatternFill('solid',fgColor='FBE4E1')
thin=Side(style='thin',color='D5DCE4'); bd=Border(left=thin,right=thin,top=thin,bottom=thin)
for i,(nm,lg) in enumerate(COLS,1):
    c=ws.cell(row=1,column=i,value=nm); c.fill=hf; c.font=hfont; c.border=bd
    c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
    ws.column_dimensions[get_column_letter(i)].width=lg
ws.row_dimensions[1].height=24
ord_=sorted(d,key=lambda a:(a['prov'] or 'ZZ',a['citta'],a['nome']))
for r,a in enumerate(ord_,2):
    vals=[a['prov'],PROV.get(a['prov'],''),a['nome'],a['citta'],a['indirizzo'],a['telefono'],a['email'],a['sito'],a.get('marchi',''),a['specializzazione'],a['note'],a['cliente'],a['fonte']]
    for i,v in enumerate(vals,1):
        c=ws.cell(row=r,column=i,value=v); c.border=bd; c.font=Font(size=10)
        c.alignment=Alignment(vertical='top',wrap_text=(i in (3,5,9,10,11,13)))
        if a['cliente']: c.fill=cli
        elif a.get('rivale'): c.fill=riv
        elif r%2==0: c.fill=alt
ws.freeze_panes='A2'; ws.auto_filter.ref=f'A1:{get_column_letter(len(COLS))}{len(ord_)+1}'
out=f'{BASE}/Rivenditori-Porte-Finestre-Sicilia.xlsx'; wb.save(out)
print(f"Excel: {out} · {len(ord_)} righe · con email {sum(1 for a in ord_ if a['email'])} · con marchi {sum(1 for a in ord_ if a.get('marchi'))}")
