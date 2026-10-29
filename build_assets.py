import os,re,json,shutil,glob
from PIL import Image, ImageDraw, ImageChops
Image.MAX_IMAGE_PIXELS=None
SRC='/home/claude/src'; OUT='/home/claude/site/assets'
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)

def nat(s): return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)',s)]
def uni(name):  # unzip left '#U062a' escapes in names -> real characters
    return re.sub(r'#U([0-9a-fA-F]{4})',lambda m:chr(int(m.group(1),16)),name)
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')

def save_web(im,path,maxside,q=82):
    im=im.copy()
    if im.mode not in('RGB','RGBA'): im=im.convert('RGBA' if 'A' in im.mode or im.mode=='P' else 'RGB')
    im.thumbnail((maxside,maxside),Image.LANCZOS)
    im.save(path,'WEBP',quality=q,method=5)

def logo(src,dst,trim=True,circle=False,plate=False):
    im=Image.open(src)
    if circle:
        im=im.convert('RGB'); bg=Image.new('RGB',im.size,(255,255,255))
        bb=ImageChops.difference(im,bg).convert('L').point(lambda v:255 if v>25 else 0).getbbox()
        im=im.crop(bb); s=min(im.size); im=im.crop((0,0,s,s))
        m=Image.new('L',(s*2,s*2),0); ImageDraw.Draw(m).ellipse((2,2,s*2-2,s*2-2),fill=255)
        m=m.resize((s,s),Image.LANCZOS); im=im.convert('RGBA'); im.putalpha(m)
    else:
        im=im.convert('RGBA')
        if trim:
            a=im.split()[3]; bb=a.point(lambda v:255 if v>8 else 0).getbbox()
            if bb:
                pad=int(max(bb[2]-bb[0],bb[3]-bb[1])*.04)
                im=im.crop((max(0,bb[0]-pad),max(0,bb[1]-pad),min(im.width,bb[2]+pad),min(im.height,bb[3]+pad)))
    im.thumbnail((700,700),Image.LANCZOS); im.save(dst,'WEBP',quality=90,method=5)

os.makedirs(OUT+'/logos'); os.makedirs(OUT+'/profile'); os.makedirs(OUT+'/feedback')
# profile images (from the original portfolio, unchanged)
shutil.copy('/home/claude/embedded/e00.jpg',OUT+'/profile/avatar.jpg')
shutil.copy('/home/claude/embedded/e01.jpg',OUT+'/profile/portrait.jpg')

CLIENTS=[ # folder, name, logo path, opts
 ("CH PROM","CH PROM","CH PROM/CH-PROM LOGO.png",{}),
 ("Designe Menu L'original Krousty","L'Original Krousty",'/home/claude/krousty_logo_big.png',{'circle':True}),
 ("Designe's CCBO","CCBO Wood Market","Designe's CCBO/logo.png",{}),
 ("Designe's MARKETPIZZA FLAYER'S","Market Pizza","Designe's MARKETPIZZA FLAYER'S/Logo MARKETPIZZA.png",{'plate':True,'trim':False}),
 ("Designe's Social Media Team Valar","Team Valar","Designe's Social Media Team Valar/Logo Valar Team.PNG",{}),
 ("FOOD FACTORY DESIGNE'S","Food Factory","FOOD FACTORY DESIGNE'S/WhatsApp Image 2026-04-09 at 11.08.48.jpeg",{'plate':True,'trim':False}),
 ("Famous Street Works","Famous Street","Famous Street Works/Logo-famous-Street.png",{}),
 ("Krousty Bwol Designe's","Krousty Bowl","Krousty Bwol Designe's/logo KB.png",{}),
 ("L'CINCO PIZZA Designe's","L'Cinzo Pizza","L'CINCO PIZZA Designe's/Logo-L'cinco.png",{}),
 ("MENU FARMERS","Farmer's Grill & Co","MENU FARMERS/Logo Farmers.png",{'plate':True,'trim':False}),
 ("POSTER'S LA FIEF DE PAPA FLAYER'S","Le Fief de Papa","POSTER'S LA FIEF DE PAPA FLAYER'S/IMG_8284.PNG",{'plate':True,'trim':False}),
 ("Poster's Maya Resturoent","Maya Restaurant","Poster's Maya Resturoent/logo maya_entier.png",{}),
 ("Wihda Post & Carousel","Wihda","Wihda Post & Carousel/Logo-Wihda.png",{}),
]
LOGO_NAMES=re.compile(r'logo',re.I)
IMG=('.jpg','.jpeg','.png','.webp')
out=[]
for folder,name,lp,o in CLIENTS:
    cs=slug(name); cdir=f'{OUT}/clients/{cs}'; os.makedirs(cdir)
    lpath=lp if lp.startswith('/') else f'{SRC}/{lp}'
    logo(lpath,f'{OUT}/logos/{cs}.webp',trim=o.get('trim',True),circle=o.get('circle',False))
    base=f'{SRC}/{folder}'
    # collect: top-level images (single-image projects) and sub-folders (multi-image projects)
    projects=[]
    entries=sorted(os.listdir(base),key=nat)
    def is_logo_file(fp):
        f=os.path.basename(fp)
        return fp==lpath or LOGO_NAMES.search(f) or f=='IMG_8284.PNG' or f.startswith('WhatsApp Image')
    def collect(d):
        r=[]
        for root,_,fs in os.walk(d):
            for f in fs:
                if f.lower().endswith(IMG): r.append(os.path.join(root,f))
        return sorted(r,key=lambda p:nat(os.path.relpath(p,d)))
    for e in entries:
        p=f'{base}/{e}'
        if os.path.isdir(p):
            files=collect(p)
            if files: projects.append((uni(e),files))
        elif e.lower().endswith(IMG) and not is_logo_file(p):
            projects.append((uni(os.path.splitext(e)[0]),[p]))
    pj=[]
    for i,(title,files) in enumerate(projects):
        pid=f'p{i+1:02d}'; imgs=[]
        for j,f in enumerate(files):
            fn=f'{pid}-{j+1:02d}'
            im=Image.open(f)
            save_web(im,f'{cdir}/{fn}.webp',2000,82)
            save_web(im,f'{cdir}/{fn}-t.webp',640,78)
            w,h=im.size
            imgs.append({'src':f'assets/clients/{cs}/{fn}.webp','thumb':f'assets/clients/{cs}/{fn}-t.webp','w':w,'h':h,'orig':os.path.basename(f)})
        pj.append({'id':pid,'rawTitle':title,'images':imgs})
    out.append({'id':cs,'name':name,'logo':f'assets/logos/{cs}.webp','plate':o.get('plate',False),'folder':folder,'projects':pj})
    print(name,len(pj),'projects',sum(len(p['images']) for p in pj),'images')

# independent works from the original portfolio (embedded images)
ind=[('e02','Smokey Nagata','Movie Poster'),('e08','The Lost Treasure','Movie Poster'),('e10','Orange County Homes Under $1M','YouTube Thumbnail'),('e15','Would You Pay $900K For This?','YouTube Thumbnail')]
json.dump(out,open('/home/claude/raw_clients.json','w'),ensure_ascii=False,indent=1)
