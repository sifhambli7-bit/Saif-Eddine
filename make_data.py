import json,re,os
from PIL import Image
raw=json.load(open('/home/claude/raw_clients.json'))
def cap(w): return w if re.search(r'\d',w) else (w[:1].upper()+w[1:].lower())
def clean(t):
    ar=bool(re.search(r'[\u0600-\u06FF]',t))
    t=re.sub(r'\.jpg','',t,flags=re.I); t=re.sub(r'[_]+',' ',t); t=re.sub(r'-+',' ',t); t=t.replace(',',' ').replace('.',' ')
    t=re.sub(r'\s+',' ',t).strip()
    if ar: return t
    ws=[w for w in t.split(' ')]
    drop={'designe','designes',"designe's",'design'}
    kept=[w for w in ws if w.lower() not in drop] or ws
    kept=[ 'Flyer' if w.lower()=='flayer' else w for w in kept]
    return ' '.join(cap(w) if not re.match(r'^[A-Z]{2,}$',w) or len(w)>4 else w for w in kept)
def cat(client,t):
    l=t.lower()
    if 'carousel' in l: return 'Carousel'
    if 'thumbnail' in l: return 'Thumbnail'
    if 'cover' in l: return 'Cover'
    if 'billboard' in l: return 'Billboard'
    if re.search(r'menu|ramadan|dessert|nems|etudiant',l): return 'Menu Design'
    if 'ورشة' in t: return 'Workshop Post'
    if 'منشور' in t: return 'Awareness Post'
    if 'podcast' in l: return 'Podcast Post'
    if 'workshop' in l: return 'Workshop Post'
    if client=="L'Original Krousty" and 'original' in l and 'flayer' not in l: return 'Menu Design'
    if re.search(r'flayer|flyer',l): return 'Flyer'
    if re.search(r'affiche|poster',l): return 'Poster'
    if client=='Maya Restaurant': return 'Event Poster'
    if client=='Famous Street' and l in('beef','big-+-originales','boisson','chicken','dessert','hot-dog','menu-enfant-+-salade','street-frise'): return 'Menu Visual'
    if client=='Team Valar': return 'Social Media'
    return None
TITLE_OVR={ # nicer titles, words taken from the file names
 'CH PROM':{'Billboard-Design-CH-PROM-02--':'Billboard Design 02','Cover-FACEBOOK-CH-PROM':'Facebook Cover','Designe-Affiche-ELOGIA---Invite-CH-PROM':'Affiche ELOGIA — Invite'},
 "L'Original Krousty":{'A5-DESSERT-&-NEMS-TANDERS-LORIGINAL-KROUSTY':'A5 Dessert & Nems Tanders',"DESIGNE'S-KROUSTY-ORIGINAL-01-":'Krousty Original 01',"DESIGNE'S-KROUSTY-ORIGINAL-02-":'Krousty Original 02',"DESIGNE'S-KROUSTY-ORIGINAL-03-":'Krousty Original 03','FLAYER-KROUSTY-ORIGINAL-PUB':'Krousty Original — Pub Flyer','Menu-Etudiant':'Menu Étudiant'},
 'CCBO Wood Market':{'01':'CCBO 01','Cover-FACEBOOK-CCBO-':'Facebook Cover','Designe-CCBO-AFFICHE-01':'Affiche 01'},
 'Food Factory':{'Flayer-Menu-Etudiant-Food-Factory-.':'Menu Étudiant — Flyer (Alt.)','Flayer-Menu-Etudiant-Food-Factory':'Menu Étudiant — Flyer'},
 'Famous Street':{'Big-+-originales':'Big + Originales','menu-enfant-+-salade':'Menu Enfant + Salade','street-frise':'Street Frise','hot-dog':'Hot Dog','Designe-Menu-Famous-Street_01':'Menu 01','Designe-Menu-Famous-Street_02':'Menu 02','Designe-Menu-Famous-Street_03':'Menu 03','Thumbnail-Famous-Street':'Thumbnail'},
 'Maya Restaurant':{'DESIGNE-MAYA-Hypnotiseur.-2--jpg':'Hypnotiseur','DESIGNE-MAYA-Saint-Valentin--Black-Valentine':'Saint-Valentin — Black Valentine','Designe-Music-AFRICA--9-16':'Music Africa','Designe-Music-anniversaire-dj-Karim-&-LA-final-de-la-CAN':'Anniversaire DJ Karim & Finale de la CAN','DESIGNE-FLAYER-EVENT-DJ':'Event DJ — Cosmic','menu-ramadan-maya-03-':'Menu Ramadan — Délices du Maya','flayer-match':'Flyer Match','Flayer-maya':'Flyer Maya'},
 "L'Cinzo Pizza":{"Menu-L'CINCO-PIZZA_01":"Menu 01","Menu-L'CINCO-PIZZA_02":"Menu 02"},
 "Farmer's Grill & Co":{'MENU-3-ECRON-BURGER-SMASH_01':'Menu 3 Écrans — Burger Smash 01','MENU-3-ECRON-BURGER-SMASH_02':'Menu 3 Écrans — Burger Smash 02','MENU-3-ECRON-BURGER-SMASH_03':'Menu 3 Écrans — Burger Smash 03'},
 'Krousty Bowl':{'Designe-Krousty-Bowl-FalFal':'Nouveauté Falafel','Designe-ouverture-KB-form-insta-':'Ouverture — 100 Premiers','Krousty-Bowl-Poster-Designe':'Menu Enfants'},
 'Le Fief de Papa':{'DESIGNE-FLAYER-A5-BERGUER-02-':'Flyer A5 Burger 02','DESIGNE-FLAYER-A5-BERGUER':'Flyer A5 Burger','DESIGNE-FLAYER-LE-FIEF-DE-PAPA-03':'Flyer 03','DESIGNE-FLAYER-LE-FIEF-DE-PAPA-04':'Flyer 04','DESIGNE-FLAYER-LE-FIEF-DE-PAPA-05':'Flyer 05'},
 'Team Valar':{'Design-Social-Media-Clan-Valar':'Social Media Clan Valar','DESIGNE-OF-3-WORKSHOP':'3 Workshops','Designe-of-player-in-Valar-03-':'Player in Valar 03','DESIGNE-WINNERS-3-CLUB':'Winners — 3 Club','DESIGNE-WORKSHOP-MENTAL':'Workshop Mental','DESIGNE-WORKSHOP-OF-CREATING-CONTENT':'Workshop of Creating Content','Valar-Corner-Podcast-02-':'Valar Corner Podcast 02','Valar-Corner-Podcast':'Valar Corner Podcast'},
 'Wihda':{f'WIHDA_W1_Post{i}_Carousel':f'Week 1 — Post {i} Carousel' for i in range(1,6)},
}
FS_FIRST=['Designe-Menu-Famous-Street_01','Designe-Menu-Famous-Street_02','Designe-Menu-Famous-Street_03','Thumbnail-Famous-Street']
clients=[]
for c in raw:
    projs=c['projects']
    if c['name']=='Famous Street':
        projs=[p for k in FS_FIRST for p in projs if p['rawTitle']==k]+[p for p in projs if p['rawTitle'] not in FS_FIRST]
    out=[]
    for p in projs:
        rt=p['rawTitle']; title=TITLE_OVR.get(c['name'],{}).get(rt) or clean(rt)
        if rt.startswith('Carousel Designe'): title='Carousel '+rt.split()[2]
        if c['name']=='Team Valar' and re.search(r'[\u0600-\u06FF]',rt): title=clean(rt).replace('.jpg 02',' 02').replace(' 01 2',' 01')
        if rt=='منشور-توعوي.jpg-02': title='منشور توعوي 02'
        if rt=='ورشة-التوعية-.01.2': title='ورشة التوعية 01'
        if rt=='ورشة-رحلة-صناعة-المحتوى-02-': title='ورشة رحلة صناعة المحتوى 02'
        if rt=='تصميم-ورشة--روكت-ليغ,-': title='تصميم ورشة روكت ليغ'
        if rt=='منشور-توعوي': title='منشور توعوي 01'
        out.append({'id':p['id'],'title':title,'category':cat(c['name'],rt),'rtl':bool(re.search(r'[\u0600-\u06FF]',title)),
                    'images':[{k:i[k] for k in('src','thumb','w','h')} for i in p['images']]})
    clients.append({'id':c['id'],'name':c['name'],'logo':c['logo'],'plate':c['plate'],'projects':out})
def local(d,items):
    r=[]
    for n,(t,ca,w,h) in enumerate(items):
        pid=f'p{n+1:02d}'
        r.append({'id':pid,'title':t,'category':ca,'rtl':False,'images':[{'src':f'assets/clients/{d}/{pid}-01.webp','thumb':f'assets/clients/{d}/{pid}-01-t.webp','w':w,'h':h}]})
    return r
clients.append({'id':'crousty-ball','name':'Crousty Ball','logo':None,'plate':False,'projects':local('crousty-ball',[('Menu Étudiant','Menu Design',900,508),('Main Board','Menu Design',900,501),('Sauces & Sides','Menu Design',900,506)])})
clients.append({'id':'independent-works','name':'Independent Works','logo':None,'plate':False,'note':'Movie posters & YouTube thumbnails','projects':local('independent-works',[('Smokey Nagata','Movie Poster',700,874),('The Lost Treasure — Netflix','Movie Poster',700,875),('Orange County Homes Under $1M','YouTube Thumbnail',900,500),('Would You Pay $900K For This?','YouTube Thumbnail',900,500)])})
for c in clients:
    cats={}
    for p in c['projects']:
        if p['category']: cats[p['category']]=cats.get(p['category'],0)+1
    c['categories']=list(cats)
    c['count']=len(c['projects']); c['imageCount']=sum(len(p['images']) for p in c['projects'])
feedback=[
 {'id':'nazim','name':'Nazim','type':'text','lang':'en','quote':"I worked with Sif Eddine on several projects and had a great experience. He's professional creative reliable and always delivers quality work. Communication was smooth and I'd definitely recommend working with him.",'screenshot':'assets/feedback/nazim.webp','clientId':None},
 {'id':'valar-club','name':'Valar Club','type':'text','lang':'ar','quote':'والله خدمتك ماشاءالله مره سريعة ونتايج التصميم كانت حلوه وبالشكل المطلوب','screenshot':'assets/feedback/valar-club.webp','clientId':'team-valar'},
 {'id':'reda-noui','name':'Reda Noui','type':'video','video':'assets/feedback/reda-noui.mp4','poster':'assets/feedback/reda-noui.jpg','clientId':None},
 {'id':'walid-ezra','name':'Walid Ezra','type':'video','video':'assets/feedback/walid-ezra.mp4','poster':'assets/feedback/walid-ezra.jpg','clientId':None},
]
js='/* Portfolio data — generated by build_assets.py + make_data.py. Edit freely: add a client object to `clients`, or a feedback item to `feedback`. */\nwindow.PORTFOLIO='+json.dumps({'clients':clients,'feedback':feedback},ensure_ascii=False,indent=1)+';\n'
open('/home/claude/site/data.js','w',encoding='utf8').write(js)
print(len(clients),'clients;',sum(c['count'] for c in clients),'projects;',sum(c['imageCount'] for c in clients),'images')
for c in clients: print(c['name'],c['count'],c['categories'])
