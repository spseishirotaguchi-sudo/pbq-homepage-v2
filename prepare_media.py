"""Prepare reviewed p.b.q originals for the homepage, without generative edits."""
from pathlib import Path
from PIL import Image, ImageOps
import subprocess, json, io

ROOT = Path(__file__).parent
ASSETS = ROOT / 'public/assets'
RAW = Path('/Users/seishiro.t/p.b.q/映像素材')
videos = json.loads((ROOT / 'qa/oct13-clip-index.json').read_text())
records = []

def still(name, source, second=None, crop=None, maxsize=(1800,1800)):
    if second is not None:
        data = subprocess.check_output(['ffmpeg','-v','error','-ss',str(second),'-i',str(source),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
        im = Image.open(io.BytesIO(data)).convert('RGB')
    else:
        im = ImageOps.exif_transpose(Image.open(source)).convert('RGB')
    if crop: im = im.crop(crop)
    im.thumbnail(maxsize, Image.Resampling.LANCZOS)
    im.save(ASSETS/name, quality=91, method=6)
    records.append({'asset':name,'source':str(source),'second':second,'width':im.width,'height':im.height,'crop':crop})

still('basket-finish-1013.webp',videos[9]['path'],7.98)
still('basket-net-1013.webp',videos[9]['path'],8.55)
still('basket-smile-1013.webp',videos[10]['path'],73.8,crop=(2350,130,3840,2120))
still('basket-pass-1013.webp',videos[5]['path'],8.0)
still('basket-jump-1005.webp',RAW/'20261005/写真/IMG_0671.png')
still('basket-dribble-1005.webp',RAW/'20261005/写真/IMG_0668.png')
still('basket-break-1009.webp',RAW/'20261009/朝の部/写真/IMG_0745.png')
still('basket-teamplay-1013.webp',videos[3]['path'],26.0)
still('basket-defence-1005.webp',RAW/'20261005/写真/IMG_0677.png')

def segment(source, start, duration, output, mobile=False, pos=.5):
    vf = 'scale=1280:720:flags=lanczos,fps=24' if not mobile else f'scale=-2:1280:flags=lanczos,crop=720:1280:(iw-ow)*{pos}:0,fps=24'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',source,'-t',str(duration),'-an','-vf',vf,'-c:v','libx264','-preset','fast','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)

for mobile in (False,True):
    label = 'mobile' if mobile else 'desktop'
    parts=[]
    for i,(idx,start,duration,pos) in enumerate([(9,6.65,3.15,.64),(10,71.8,2.0,.98)]):
        out=ROOT/f'outputs/hero-{label}-{i}.mp4'
        segment(videos[idx]['path'],start,duration,out,mobile,pos)
        parts.append(out)
    listing=ROOT/f'outputs/hero-{label}-concat.txt'
    listing.write_text(''.join("file '"+str(p)+"'\n" for p in parts))
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(ASSETS/f'hero-v2-{label}.mp4')],check=True)

still('hero-v2-poster.webp',videos[9]['path'],7.95,maxsize=(1600,900))
(ROOT/'qa/media-selection.json').write_text(json.dumps({'stills':records,'hero_segments':[{'source':videos[9]['path'],'start':6.65,'end':9.8,'reason':'白シャツの選手のレイアップ。8.55秒でボールがネットを通過するフレームを確認。'},{'source':videos[10]['path'],'start':71.8,'end':73.8,'reason':'プレー中の笑顔。同じシュートへの反応としては扱わない独立した場面。'}]},ensure_ascii=False,indent=2))
print('Reviewed media prepared')
