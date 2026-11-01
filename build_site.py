from pathlib import Path
from html import escape
from PIL import Image
import json
import re
import subprocess

ROOT = Path(__file__).parent
DIST = ROOT / 'site'
ASSETS = ROOT / 'public/assets'
DIST.mkdir(exist_ok=True)
ORIGIN = 'https://pbq-fukuoka-20261022.s-taguchi323.chatgpt.site'
LINE = 'https://lin.ee/rdgWlbC'
INSTAGRAM = 'https://www.instagram.com/p.b.q_fukuoka/'

PHOTOS = [('photo-teamphoto.webp', '練習終わりの集合写真', '一緒に走った日の、最後の一枚。', 1400, 644), ('basket-jump-1005.webp', 'もう一度、空中へ。', '思いきり跳んで、ボールを運ぶ。', 1012, 1800), ('basket-dribble-1005.webp', 'もう1ゲーム。', 'ボールを持つと、また走りたくなる。', 1012, 1800), ('basket-smile-1013.webp', 'プレー中にも、笑顔。', 'こんなひとコマも、p.b.q。', 1348, 1800), ('basket-break-1009.webp', 'ひと休みしながら。', '朝の体育館で、少しひと息。', 1012, 1800), ('photo-group.webp', 'p.b.q初懇親会！', '体育館の外にも、話のつづき。', 1200, 675), ('basket-pass-1013.webp', '次のパスを。', '顔を上げて、仲間を探す。', 1800, 1013), ('basket-finish-1013.webp', 'ゴールへ向かって。', 'シュートが決まる、その手前。', 1800, 1013)]

FAQ = [
    ('どんな人が参加できますか？', '20代の社会人で、バスケ経験のある方が対象です。男女ともに歓迎しています。学生・未経験の方は対象外です。'),
    ('ブランクがあっても大丈夫ですか？', 'ブランクの長さは問いません。学生時代以来という方も、体験参加をお申し込みいただけます。'),
    ('一人で参加しても大丈夫ですか？', 'お一人でも、友達同士の参加も、どちらも大歓迎です。'),
    ('参加費はいくらですか？', 'バスケの参加費は1回500円です。参加する日ごとのお支払いで、事前決済はありません。親睦会などのイベントは、企画ごとに別途ご案内します。'),
    ('いつ、どこで活動していますか？', '福岡市内の体育館で、朝の部・夜の部を開催しています。日時と体育館は開催日によって異なるため、最新情報を公式LINEでご確認ください。'),
    ('キャンセルはできますか？', '当日でもキャンセル料は無料です。参加できなくなった場合は、申込み画面からキャンセル手続きをお願いします。'),
    ('何を持っていけばいいですか？', '運動できる服装、室内用のバスケットシューズ、飲み物、着替え、参加費をご用意ください。会場ごとの案内も公式LINEでご確認ください。'),
    ('LINEを追加すれば申込み完了ですか？', '友だち追加だけでは、参加申込みは完了しません。LINEの案内に沿って初回アンケートに回答し、希望する日程を選んで体験参加をお申し込みください。'),
]

NAV = [
 ('MESSAGE','p.b.qの想い','about.html',[('私たちの想い','about.html#message'),('大切にしていること','about.html#values')]),
 ('ACTIVITIES','活動紹介','activities.html',[('平日の朝からバスケ','activities.html#morning'),('平日の夜にもバスケ','activities.html#night'),('親睦会・イベント','activities.html#community')]),
 ('JOIN US','参加案内','join.html',[('対象・料金','join.html#conditions'),('参加までの流れ','join.html#process'),('よくある質問','join.html#faq')]),
 ('GOODS','グッズ販売','goods.html',[('p.b.qグッズ','goods.html')]),
 ('INSTAGRAM','Instagramの投稿','index.html#movies',[('投稿を見る','index.html#movies'),('Instagramを開く',INSTAGRAM)])
]



def arrow():
    return '<span class="arrow" aria-hidden="true">›</span>'


def button(text, href, style='dark', cls=''):
    if href == LINE:
        return f'<a class="button button--line {cls}" href="{href}">{line_icon()}<span>{text}</span></a>'
    if href == INSTAGRAM:
        return f'<a class="button button--instagram {cls}" href="{href}">{instagram_icon()}<span>{text}</span></a>'
    return f'<a class="button button--{style} {cls}" href="{href}"><span>{text}</span>{arrow()}</a>'


def line_icon():
    return '<img class="brand-service-icon" src="assets/line-brand.png" alt="" width="40" height="40">'


def brand():
    return '<span class="wordmark">p.b.q</span><span class="brand-caption">FUKUOKA<br>BASKETBALL COMMUNITY</span>'


def image(name, alt, width, height, cls='', eager=False):
    if (ASSETS/name).exists():
        width, height = Image.open(ASSETS/name).size
    priority = ' fetchpriority="high"' if eager else ''
    return f'<img class="{cls}" src="assets/{name}" alt="{escape(alt)}" width="{width}" height="{height}" loading="{"eager" if eager else "lazy"}" decoding="async"{priority}>'


def section_title(en, ja, intro=''):
    return f'<div class="section-heading"><div><p class="display-title" aria-hidden="true">{en}</p><h2>{ja}</h2></div>{f"<p class=section-intro>{intro}</p>" if intro else ""}</div>'


def faq_items(items=FAQ):
    return '<div class="faq-list">' + ''.join(f'<details><summary><span class="q">Q.</span><span class="faq-question">{q}</span><span class="plus" aria-hidden="true"></span></summary><div class="answer"><span>A.</span><p>{a}</p></div></details>' for q, a in items) + '</div>'


def header(home=False):
    groups = ''.join(f'<details class="nav-group" open><summary><span><b>{en}</b><small>{ja}</small></span><span class="nav-plus" aria-hidden="true"></span></summary><a class="nav-main" href="{href}">{ja}へ {arrow()}</a>'+''.join(f'<a href="{url}">− {label}</a>' for label, url in sub)+'</details>' for en, ja, href, sub in NAV)
    return f'''<a class="skip-link" href="#main">本文へ移動</a>
<header class="site-header {'site-header--home' if home else ''}"><a class="brand" href="index.html" aria-label="p.b.q ホーム">{brand()}</a><nav class="header-nav" aria-label="メインナビゲーション"><a href="about.html"><span>p.b.qの想い</span></a><a href="activities.html"><span>活動紹介</span></a><a href="join.html"><span>参加案内</span></a><a href="goods.html"><span>グッズ販売</span></a></nav><div class="header-actions">{button("LINEで体験参加",LINE,"line","header-entry")}<button class="menu-toggle" type="button" aria-label="メインメニューを開く" aria-haspopup="dialog" aria-controls="menu-dialog"><span></span><span></span><span></span></button></div></header>
<dialog class="menu-dialog" id="menu-dialog" aria-label="メインメニュー"><div class="menu-top"><a class="brand" href="index.html" aria-label="p.b.q ホーム">{brand()}</a><button class="close-button" data-close aria-label="メニューを閉じる">×</button></div><div class="menu-body"><nav class="menu-grid" aria-label="サイト内ナビゲーション"><a class="menu-top-link" href="index.html"><b>TOP</b><small>トップページ</small> →</a>{groups}</nav><aside class="menu-aside">{button('体験参加 / JOIN US', LINE, 'red')}{button('参加案内・料金', 'join.html')}{button('Instagramを見る', INSTAGRAM, 'outline')}<p>まずは、行けそうな日を見つけよう。<br>20代社会人・バスケ経験者のコミュニティ。</p></aside></div></dialog>
<noscript><nav class="no-js-nav">{''.join(f'<a href="{url}">{ja}</a>' for en, ja, url, sub in NAV)}</nav></noscript>'''


def footer():
    footer_nav = ''.join(f'<div><a class="footer-nav-title" href="{url}">{en}<small>{ja}</small></a>'+''.join(f'<a href="{href}">{label}</a>' for label, href in sub)+'</div>' for en, ja, url, sub in NAV)
    return f'''<section class="entry-section" id="entry"><div class="entry-ghost" aria-hidden="true">LET’S PLAY<br>TOGETHER.</div><div class="entry-inner"><p class="eyebrow">NEXT TIME, WITH YOU.</p><h2>「バスケがしたい。」<br>その気持ちから、<br>また、はじめよう。</h2><p>久しぶりのバスケも、初めての仲間も。<br>次はあなたと、体育館で。</p><a class="entry-secondary" href="join.html">参加条件・料金を確認する <span aria-hidden="true">↗</span></a><small>20代社会人・経験者対象 / バスケの参加費 1回500円</small></div></section>
<footer class="site-footer"><div class="footer-top"><div><a class="brand" href="index.html" aria-label="p.b.q ホーム">{brand()}</a><p>日常に、夢中になれる時間を。<br>福岡の20代社会人バスケコミュニティ。</p><div class="social-links">{button("Instagram",INSTAGRAM)}{button("公式LINE",LINE)}</div></div><a class="back-top" href="#page-top" aria-label="ページトップへ">↑<small>PAGE TOP</small></a></div><nav class="footer-grid" aria-label="フッターナビゲーション">{footer_nav}</nav><div class="footer-bottom"><span>PLAY BASKETBALL. ENJOY THE EVERYDAY.</span><a href="privacy.html">プライバシーについて</a><small>© p.b.q</small></div></footer>'''


def instagram_icon():
    return '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="1.7"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.7"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>'


def dialogs():
    return '''<dialog class="instagram-dialog" id="instagram-dialog" aria-label="Instagramの投稿"><button class="close-button" data-close aria-label="Instagram投稿を閉じる">×</button><iframe title="p.b.qのInstagram投稿" allow="autoplay; encrypted-media" referrerpolicy="strict-origin-when-cross-origin"></iframe><a class="instagram-dialog-link" target="_blank" rel="noopener noreferrer">Instagramで開く</a></dialog><dialog class="media-dialog" id="photo-dialog" aria-label="活動写真の拡大表示"><button class="close-button" data-close aria-label="写真を閉じる">×</button><figure><img id="lightbox-image" alt="" width="1100" height="825"><figcaption><strong id="lightbox-title"></strong><span id="lightbox-caption"></span></figcaption></figure><div class="lightbox-controls"><button class="round-control" id="photo-prev" aria-label="前の写真">←</button><p id="photo-count" aria-live="polite"></p><button class="round-control" id="photo-next" aria-label="次の写真">→</button></div></dialog>
'''


def page(title, content, file, home=False, description=None):
    description = description or '日常に、夢中になれる時間を。福岡市内で活動する20代社会人・バスケ経験者のコミュニティp.b.q。活動風景、参加方法、料金をご紹介します。'
    html = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} | p.b.q</title><meta name="description" content="{escape(description)}"><meta name="theme-color" content="#c01734"><link rel="canonical" href="{ORIGIN}/{'' if home else file}"><meta property="og:type" content="website"><meta property="og:title" content="{escape(title)} | p.b.q"><meta property="og:description" content="{escape(description)}"><meta property="og:image" content="{ORIGIN}/assets/photo-teamphoto.webp"><meta property="og:url" content="{ORIGIN}/{'' if home else file}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="assets/favicon-pbq.png" type="image/png" sizes="150x150"><link rel="preload" href="assets/fonts/ZenOldMincho.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script><script src="assets/analytics.js?v=20261101" data-measurement-id="G-R6ZDP89L27" data-pbq-site="hp" defer></script></head><body class="{'home-page' if home else 'inner-page'}" id="page-top">{header(home)}<main id="main">{content}</main>{footer()}{dialogs()}<script type="application/json" id="gallery-data">{json.dumps(PHOTOS,ensure_ascii=False)}</script></body></html>'''
    html = html.replace(' ↗','').replace('↗','')
    (DIST/file).write_text(html, encoding='utf-8')
    (ROOT/'public'/file).write_text(html, encoding='utf-8')


def sub_hero(en, ja, text):
    return f'<div class="sub-hero wrap"><nav class="breadcrumb" aria-label="現在位置"><a href="index.html">トップ</a><span aria-hidden="true">—</span><span>{ja}</span></nav><p class="sub-title display-title">{en}</p><h1>{ja}</h1><p class="sub-intro">{text}</p></div>'


def photo_card(i):
    name, title, caption, w, h = PHOTOS[i]
    return f'<figure class="photo-card {"is-landscape" if w > h else ""}"><a href="assets/{name}" class="photo-zoom" data-photo="{i}" aria-label="{title}の写真を拡大">{image(name,title,w,h)}<span class="zoom-symbol" aria-hidden="true">＋</span></a><figcaption><span class="photo-no">{i+1:02}</span><div><strong>{title}</strong><p>{caption}</p></div></figcaption></figure>'


def movies():
    items = [('play','もう一度、ボールを追う。','# バスケ # ゲームのひとコマ'),('team','パスがつながる、その瞬間。','# チーム # いつもの練習'),('practice','体育館の空気を、少しだけ。','# 福岡 # 社会人バスケ')]
    return '<div class="movie-grid">'+''.join(f'<article class="movie-card"><button class="movie-trigger" data-movie="{key}" data-title="{title}" aria-label="{title}の動画を再生"><img src="assets/{key}.webp" alt="" width="480" height="854" loading="lazy"><span class="play-icon" aria-hidden="true">▶</span><span class="play-label">PLAY VIDEO</span></button><p class="movie-tags">{tags}</p><h3>{title}</h3></article>' for key,title,tags in items)+'</div>'


values = [
 ('01','バスケ','basketball','また、バスケが<br>ある日々へ。','basket-dribble-1005.webp','20代の社会人バスケ経験者が、福岡市内の体育館に集まるp.b.q。ブランクの長さは問いません。もう一度シュートを打つ時間を、あなたの日常に。','activities.html#basketball','バスケの活動を見る'),
 ('02','イベント','events','バスケ以外でも、<br>楽しいと思える時間。','photo-group.webp','親睦会やイベントなど、バスケ以外の企画も行っています。いつもの仲間と、体育館とは違う場所で話す時間を。','activities.html#community','イベントについて見る'),
 ('03','サードプレイス','third place','「自分の居場所」と思える<br>コミュニティへ。','basket-conversation.webp','そんなコミュニティブランドへ、みんなと一緒に成長していきたい。家でも職場でもない場所で、気兼ねなく話したり、一緒に夢中になったり。p.b.qを、参加するみんなと育てていきたいと考えています。','about.html#values','p.b.qの想いを読む')
]


hero = '''<section class="hero-sequence" aria-label="p.b.qの紹介"><div class="hero-stage"><div class="hero-video-layer"><video class="hero-video" muted loop autoplay playsinline preload="metadata" poster="assets/hero-v2-poster.webp" aria-hidden="true"><source src="assets/hero-v2-mobile.mp4" media="(max-width:700px)" type="video/mp4"><source src="assets/hero-v2-desktop.mp4" type="video/mp4"></video><div class="hero-shade"></div></div><div class="hero-watermark" aria-hidden="true"><span>P.B.Q FUKUOKA</span><b>STILL IN PLAY.</b></div><h1 class="hero-title"><span>日常に、</span><span>夢中になれる</span><span>時間を。</span></h1><p class="hero-location">FUKUOKA / BASKETBALL COMMUNITY</p><div class="hero-photo-montage" aria-hidden="true"><figure><img src="assets/basket-smile-1013.webp" alt="" width="825" height="1100"><span>PEOPLE.</span></figure><figure><img src="assets/basket-jump-1005.webp" alt="" width="1000" height="1779"><span>PLAY.</span></figure><figure><img src="assets/basket-dribble-1005.webp" alt="" width="675" height="1200"><span>P.B.Q.</span></figure></div><a class="scroll-cue" href="#message"><span>SCROLL</span><i></i></a><button class="hero-pause" aria-label="背景動画を一時停止">Ⅱ</button></div></section>'''
message = '''<section class="message-section" id="message"><div class="message-ghost" aria-hidden="true">PLAY.<br>CONNECT.</div><div class="message-copy" data-preserve-breaks><p class="eyebrow">OUR MESSAGE</p><h2>やっぱり好きだ、<br>私もバスケ。</h2><p>仕事をして、家に帰る。<br>その日常に、もうひとつ楽しみを。</p><p>久しぶりにシュートを打ったり、<br>初めましてのチームメイトとお話ししてみたり、<br>決まったシュートに、みんなで声を上げて喜んだり。</p><p>p.b.qは、福岡の20代社会人が集まる<br>バスケ経験者のためのコミュニティです。</p><p>上手くいく日も、いかない日も。<br>「また来たい」と思える時間を、<br>一緒につくっていきたい。</p>'''+button('p.b.qについて','about.html','white')+'</div></section>'
orbits = '<div class="value-visual"><div class="orbit-set"><svg class="orbit-lines" viewBox="0 0 600 520" aria-hidden="true"><ellipse class="orbit-ring ring--0" cx="300" cy="165" rx="190" ry="122" transform="rotate(-28 300 165)"/><ellipse class="orbit-ring ring--1" cx="205" cy="320" rx="190" ry="122" transform="rotate(-28 205 320)"/><ellipse class="orbit-ring ring--2" cx="395" cy="320" rx="190" ry="122" transform="rotate(-28 395 320)"/></svg>'+''.join(f'<a class="orbit orbit--{i} {"is-active" if i==0 else ""}" href="#value-{i+1}" data-orbit="{i}"><span class="orbit-label">{v[1]}</span></a>' for i,v in enumerate(values))+'<span class="orbit-logo wordmark" aria-hidden="true">p.b.q</span></div></div>'

value_articles=''.join(f'''<article class="value-article" id="value-{i+1}" data-value="{i}"><p class="value-index">{v[0]} {v[1]}</p><h3>{v[3]}</h3>{image(v[4],v[1]+'の活動風景',1200,675)}<p>{v[5]}</p>{button(v[7],v[6])}</article>''' for i,v in enumerate(values))
value_html='<section class="values-section wrap" id="values">'+section_title('P.B.Q COMMUNITY','p.b.qで過ごす、3つの時間。')+'<div class="values-layout">'+orbits+'<div class="value-articles">'+value_articles+'</div></div></section>'
stories='<section class="stories-section wrap" id="activities">'+section_title('OUR ACTIVITIES','平日の朝も、夜も。バスケの外でも。','バスケを中心に、日常のなかで集まる時間を。<br>開催日時と会場は、公式LINEでご案内しています。')
for num,tag,title,desc,img in [
    ('01','MORNING BASKETBALL','平日の朝からバスケ','朝からバスケで身体を動かし、充実した一日のスタートを切りたい。','basket-dribble-1005.webp'),
    ('02','NIGHT BASKETBALL','平日の夜にもバスケ','仕事終わりに、仕事以外で出会った仲間と身体を動かす。仕事疲れを運動疲れに変えて、家でぐっすり眠る。','basket-teamplay-1013.webp'),
    ('03','OFF THE GYM','p.b.qの仲間と、<br>距離をグッと縮める。','バスケ以外にも、親睦会やイベント企画を行っています。家と職場の往復から、抜け出そう。','photo-group.webp')]:
    stories+=f'<article class="story-card"><div class="story-copy"><p class="speech-tag">{tag}</p><div class="story-title"><span>{num}</span><h3>{title}</h3></div><p class="story-desc">{desc}</p><dl><div><dt>活動</dt><dd>{"バスケットボール" if num!="03" else "親睦会・交流イベント"}</dd></div><div><dt>ご案内</dt><dd>日時・場所・申込みは公式LINEへ</dd></div></dl></div>{image(img,title.replace("<br>",""),1200,900)}</article>'
stories+='</section>'
movie_html='<section class="movies-section wrap instagram-section" id="movies">'+section_title('P.B.Q CHANNEL','Instagramで見る、p.b.q。','いつもの練習も、バスケの外の時間も。<br>p.b.qのInstagram投稿をお届けします。')+'<div class="instagram-widget"><div class="instagram-profile"><a href="'+INSTAGRAM+'" class="instagram-profile-icon" aria-label="p.b.qのInstagram"><img src="assets/instagram-avatar.jpg" alt="" width="56" height="56" loading="lazy" decoding="async"></a><div><a href="'+INSTAGRAM+'"><strong>p.b.q_fukuoka</strong></a><p>福岡の20代社会人バスケコミュニティ / p.b.q</p></div></div><div class="instagram-feed" id="instagram-feed" aria-label="p.b.qのInstagram投稿" aria-busy="true"><div class="instagram-loading" role="status">Instagramの投稿を読み込んでいます。</div></div><div class="instagram-feed-footer"><p id="instagram-feed-status" class="feed-status" aria-live="polite"></p>'+button('Instagramをフォローする',INSTAGRAM)+'</div></div></section>'

faq_home='<section class="section wrap home-faq" id="faq">'+section_title('FAQ','よくある質問。')+faq_items(FAQ[:4])+button('ほかの質問を見る','join.html#faq','outline','faq-more')+'</section>'

page('日常に、夢中になれる時間を。',hero+message+value_html+stories+movie_html+faq_home,'index.html',True)

about=sub_hero('MESSAGE','p.b.qについて','また、バスケがある日々へ。')
about_message=(ROOT/'content/about-message.txt').read_text(encoding='utf-8').strip()
about_paragraphs=''.join('<p>'+escape(p).replace('\n','<br>')+'</p>' for p in about_message.split('\n\n'))
about+='<section class="inner-section wrap" id="message"><div class="white-panel"><p class="display-title">OUR MESSAGE</p><h2>日常に、夢中になれる時間を。</h2><div class="prose about-story" data-preserve-breaks>'+about_paragraphs+'</div></div></section>'
about+='<section class="inner-section wrap" id="values">'+section_title('WHAT WE VALUE','一緒に楽しむために。')+'<div class="principle-grid">'+''.join(f'<article><span>{i:02}</span><h3>{h}</h3><p>{p}</p></article>' for i,(h,p) in enumerate([('経験より、今の一歩を。','ブランクの長さより、もう一度やってみたいという気持ちを。経験者が、今の自分のペースで楽しめる活動を目指します。'),('一人の参加を、ひとつの出会いに。','友達と一緒でなくても参加できること。バスケを通じて、自然に言葉を交わせる時間を大切にします。'),('みんなと育てる、サードプレイス。','家でも職場でもない、気兼ねなく集まれる場所へ。安全やマナーに気を配り、お互いを尊重しながら、参加するみんなとコミュニティを育てていきます。')],1))+'</div></section>'
about+='<div class="wide-photo wrap">'+image('photo-teamphoto.webp','練習終わりの集合写真',1400,644)+'</div><section class="inner-section wrap" id="outline">'+section_title('COMMUNITY PROFILE','活動概要。')+'<dl class="overview">'+''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k,v in [('コミュニティ名','p.b.q'),('活動内容','バスケットボール / 親睦会などの交流企画'),('活動エリア','福岡市内の体育館。会場は開催日ごとにご案内します。'),('バスケの参加対象','20代社会人・バスケ経験者 / 男女歓迎'),('バスケの参加費','1回500円。親睦会などのイベントは別途ご案内します。'),('開催日・お問い合わせ',f'<a href="{LINE}">公式LINEで確認する ↗</a>')])+'</dl></section>'
page('p.b.qについて',about,'about.html')

activities=sub_hero('ACTIVITIES','活動紹介','朝も、夜も。体育館の外でも。<br>バスケを中心に集まる、p.b.qの時間。')
activities+='<section class="inner-section wrap" id="basketball"><p class="eyebrow red-text">BASKETBALL</p><h2 class="inner-heading">やっぱり好きだ、私もバスケ。</h2><p class="prose">福岡市内の体育館で、バスケの練習・ゲームを行っています。部活以来、何年ぶりという方も歓迎です。開催日時と体育館は、公式LINEでご確認ください。</p></section>'
for ident,en,h,body,img in [('morning','MORNING','平日の朝からバスケ','朝からバスケで身体を動かし、充実した一日のスタートを切りたい。開催日時と体育館は、公式LINEでご確認ください。','basket-dribble-1005.webp'),('night','NIGHT','平日の夜にもバスケ','仕事終わりに、仕事以外で出会った仲間と身体を動かす。仕事疲れを運動疲れに変えて、家でぐっすり眠る。開催日時と体育館は、公式LINEでご確認ください。','basket-teamplay-1013.webp'),('community','COMMUNITY','親睦会・交流イベント','バスケ以外にも、親睦会やイベント企画を行っています。家と職場の往復から、抜け出そう。開催情報、対象、参加費、申込み方法は企画ごとにご案内します。','photo-group.webp')]:
    activities+=f'<section class="activity-detail wrap" id="{ident}"><div>{image(img,h,1200,900)}</div><div><p class="display-title">{en}</p><h2>{h}</h2><p>{body}</p></div></section>'
page('活動紹介',activities,'activities.html')

gallery=sub_hero('OUR MOMENTS','p.b.qの雰囲気を一部お届け！','ボールを追う瞬間も、ふとしたひと休みも。<br>p.b.qの、いつもの風景です。')
gallery+='<section class="inner-section wrap" id="gallery"><p class="gallery-instruction">写真をタップすると、大きく表示できます。</p><div class="gallery-grid">'+''.join(photo_card(i) for i in range(len(PHOTOS)))+'</div></section>'
page('写真で見るp.b.q',gallery,'gallery.html')

join=sub_hero('JOIN US','参加案内','久しぶりのバスケでも、一人の参加でも。<br>まずは、行けそうな日を見つけよう。')
join+='<section class="inner-section wrap" id="conditions"><div class="white-panel"><p class="display-title">WHO CAN JOIN?</p><h2>参加について。</h2><dl class="overview"><div><dt>対象</dt><dd>20代社会人・バスケ経験者<br><small>男女歓迎。学生・未経験の方は対象外です。</small></dd></div><div><dt>ブランク・一人参加</dt><dd>どちらも歓迎しています。ブランクの長さは問いません。</dd></div><div><dt>活動場所</dt><dd>福岡市内の体育館。日程ごとに会場をご案内します。</dd></div></dl><div class="fee-block" id="fee"><span>バスケの参加費</span><p>1回 <strong>500</strong> 円</p><small>参加する日ごとのお支払い / 事前決済なし</small></div><div class="cancel-note"><strong>当日でもキャンセル料無料。</strong><p>参加できなくなった場合は、必ずキャンセル手続きをお願いします。</p></div><p class="event-fee-note">※ 親睦会などのイベントは、参加条件・料金を企画ごとにご案内します。</p></div></section>'
join+='<section class="inner-section wrap" id="process">'+section_title('HOW TO JOIN','体験参加までの流れ。')+'<ol class="process-list">'+''.join(f'<li><span>{i:02}</span><div><h3>{h}</h3><p>{p}</p></div></li>' for i,(h,p) in enumerate([('公式LINEを追加する','下のボタンからp.b.qの公式LINEを追加し、届く案内をご確認ください。'),('初回アンケートに回答する','案内に沿って初回アンケートに回答します。参加に必要な情報をご登録ください。'),('希望の日程を選んで申し込む','参加できる日時と体育館を確認し、体験参加を申し込みます。申込み完了の案内をご確認ください。')],1))+'</ol>'+button('公式LINEで練習日を見る',LINE,'red')+'<p class="small-note">LINE追加だけでは申込みは完了しません。</p></section>'
join+='<section class="inner-section wrap" id="faq">'+section_title('FAQ','よくある質問。')+faq_items()+'</section>'
page('参加案内・料金',join,'join.html')

privacy=sub_hero('PRIVACY','プライバシーについて','このWebサイトの情報の取扱いについて。')
privacy+='<section class="inner-section wrap"><div class="white-panel prose"><h2>本サイトについて</h2><p>参加申込みやお問い合わせは、p.b.q公式LINEでご案内します。アクセス解析のために、次の情報を取り扱います。</p><h2>アクセス解析について</h2><p>p.b.qは、ホームページや参加案内を改善するためにGoogle アナリティクス（GA4）を利用しています。Cookieなどの技術を使い、アクセス元、閲覧ページ、スクロール到達率、公式LINE・Instagramへのリンクのクリックなどを計測し、Googleに送信します。</p><p>氏名、メールアドレス、電話番号、LINEのユーザーID、アンケートの回答内容やLINEでの会話は、このアクセス解析に送信しません。広告のパーソナライズとGoogleシグナルは使用しません。</p><p>詳しくは<a href="https://policies.google.com/technologies/partner-sites?hl=ja" target="_blank" rel="noopener noreferrer">Googleのサービスを使用するサイトやアプリから収集した情報のGoogleによる使用</a>をご確認ください。</p><h2>アクセス解析の停止・再開</h2><p>下のボタンから、このブラウザでの今後の計測を停止・再開できます。設定はサイトごとに保存されるため、HP・LPの両方で停止したい場合は、それぞれのページで設定してください。ブラウザのプライバシー設定でGPCが有効な場合も、計測を停止します。</p><button type="button" class="button button--dark" data-analytics-toggle aria-pressed="false">アクセス解析を停止する</button><p data-analytics-status role="status">JavaScriptが有効な場合、このブラウザの設定を表示します。</p><p>Googleが提供する<a href="https://tools.google.com/dlpage/gaoptout?hl=ja" target="_blank" rel="noopener noreferrer">Google アナリティクス オプトアウト アドオン</a>も利用できます。</p><h2>外部サービスについて</h2><p>公式LINEやInstagramなどへのリンクを押すと、各サービスのページへ移動します。移動先での情報の取扱いは、それぞれのサービスの案内をご確認ください。Instagram欄では、p.b.qが連携したアカウントの公開投稿を表示します。閲覧者のInstagramへのログインや連携は不要です。公開基盤におけるアクセス情報の取扱いは、基盤提供者の方針に従います。</p><h2>写真・映像について</h2><p>掲載している写真と映像はp.b.qの実際の活動のものです。掲載内容についてのお問い合わせは、公式LINEまでご連絡ください。</p>'+button('公式LINEで問い合わせる',LINE,'outline')+'</div></section>'
page('プライバシーについて',privacy,'privacy.html')

goods=sub_hero('PBQ GOODS','グッズ販売','練習で使えるものから、思い出を残すものまで。')
goods+='<section class="inner-section wrap"><div class="goods-preparing"><p class="eyebrow">COMING SOON</p><h2>現在準備中です。</h2><p>p.b.qのグッズ販売を準備しています。<br>取り扱うアイテムや販売方法は、こちらでご案内します。</p></div></section>'
page('グッズ販売',goods,'goods.html')

not_found = sub_hero('PAGE NOT FOUND','ページが見つかりませんでした。','URLが変更されたか、ページが見つかりません。')
not_found += '<section class="inner-section wrap">'+button('トップページへ戻る','index.html','red')+'</section>'
page('ページが見つかりませんでした',not_found,'404.html')
(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n')
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{ORIGIN}/{"" if p=="index.html" else p}</loc></url>' for p in ['index.html','about.html','activities.html','gallery.html','join.html','goods.html','privacy.html'])+'</urlset>')
Image.open(ASSETS/'instagram-avatar.jpg').save(ASSETS/'favicon-pbq.png')

font_path=ROOT/'qa/ZenOldMincho-Regular.ttf'
if font_path.exists():
    from fontTools import subset
    text=''.join(p.read_text(encoding='utf-8') for p in DIST.glob('*.html'))
    chars=''.join(sorted(set(re.sub('<[^>]+>','',text)+'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz→←↑↗×−＋Ⅱ▶')))
    options=subset.Options(); options.flavor='woff2'; options.layout_features=['*']
    font=subset.load_font(str(font_path),options)
    sub=subset.Subsetter(options=options); sub.populate(text=chars); sub.subset(font)
    subset.save_font(font,str(ASSETS/'fonts/ZenOldMincho.woff2'),options)
print('7ページ + 404 / サイト生成完了')

for metadata in ['robots.txt','sitemap.xml']:
    (ROOT/'public'/metadata).write_text((DIST/metadata).read_text())

subprocess.run(["node", str(ROOT/"scripts/typeset-html.mjs")], check=True)
