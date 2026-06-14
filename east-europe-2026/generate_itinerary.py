#!/usr/bin/env python3
"""
동유럽 여행 일정 HTML 생성기
사용법: python generate_itinerary.py [data.yaml] [output.html]
       python generate_itinerary.py          # europe_2026.yaml → europe_2026.html
"""
import sys
import html as _html
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML이 없습니다. 설치: pip install pyyaml")

# ── constants ─────────────────────────────────────────────────────────────────
CITY_CODE  = {'prague':'pr','salzburg':'sa','vienna':'vi','budapest':'bu'}
ICON_MAP   = {
    'flight':('ico-fl','항공'), 'hotel':('ico-ht','숙소'),
    'sight': ('ico-sk','관광'), 'art':  ('ico-at','미술'),
    'nature':('ico-nt','자연'), 'music':('ico-mu','음악'),
    'spa':   ('ico-sp','온천'), 'boat': ('ico-bo','유람'),
    'drive': ('ico-dr','차량'), 'night':('ico-ny','야경'),
    'shop':  ('ico-sh','쇼핑'), 'cafe': ('ico-ca','카페'),
}
XFER_LABEL = {'flight':'항공','drive':'차량','train':'기차','bus':'버스'}

def e(s): return _html.escape(str(s)) if s is not None else ''
def cc(cid): return CITY_CODE.get(cid or '', '')

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """\
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --pr:#B03A3A;--pr-mid:#D45656;--pr-pale:#FDF2F2;
  --sa:#2E7D52;--sa-mid:#45A870;--sa-pale:#F0FAF5;
  --vi:#6B3FA0;--vi-mid:#8E5CC4;--vi-pale:#F5F0FB;
  --bu:#1A6699;--bu-mid:#2E86C1;--bu-pale:#EEF6FB;
  --text:#1F2D3D;--muted:#7B8A99;--border:#E5EAF0;--bg:#F3F5F8;--white:#fff
}
html{scroll-behavior:smooth}
body{font-family:-apple-system,'Noto Sans KR','Apple SD Gothic Neo',BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:var(--bg);color:var(--text);line-height:1.7;font-size:14px}

/* HERO */
.hero{background:linear-gradient(150deg,#0D1B2A 0%,#102845 55%,#0A2040 100%);
  color:#fff;padding:64px 24px 72px;text-align:center;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 80% 60% at 50% 0%,rgba(46,134,255,.12),transparent);pointer-events:none}
.hero::after{content:'';position:absolute;bottom:-1px;left:0;right:0;height:52px;
  background:var(--bg);clip-path:ellipse(55% 100% at 50% 100%)}
.hero-ey{font-size:11px;letter-spacing:4px;text-transform:uppercase;opacity:.5;margin-bottom:18px}
.hero h1{font-size:clamp(1.9rem,5vw,3.2rem);font-weight:800;letter-spacing:-.03em;line-height:1.1;
  margin-bottom:12px;background:linear-gradient(135deg,#fff 40%,#90C4E8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-sub{font-size:15px;opacity:.6;margin-bottom:52px}
.route{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;max-width:680px;margin:0 auto}
.route-stop{display:flex;flex-direction:column;align-items:center;gap:8px}
.route-dot{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:11px;font-weight:800;box-shadow:0 4px 16px rgba(0,0,0,.35);border:2px solid rgba(255,255,255,.2)}
.route-dot.pr{background:var(--pr)}.route-dot.sa{background:var(--sa)}
.route-dot.vi{background:var(--vi)}.route-dot.bu{background:var(--bu)}
.route-label{font-size:12px;font-weight:700;opacity:.9}
.route-nights{font-size:10px;opacity:.5;letter-spacing:.5px}
.route-line{flex:1;min-width:24px;max-width:56px;height:2px;margin-bottom:30px;position:relative;
  background:linear-gradient(90deg,rgba(255,255,255,.1),rgba(255,255,255,.3),rgba(255,255,255,.1))}
.route-line::after{content:'';position:absolute;right:-5px;top:-3px;
  border-left:7px solid rgba(255,255,255,.25);border-top:4px solid transparent;border-bottom:4px solid transparent}

/* FLIGHTS */
.fl-section{background:var(--white);border-bottom:1px solid var(--border);padding:28px 24px}
.fl-inner{max-width:860px;margin:0 auto}
.fl-label{font-size:10px;font-weight:800;letter-spacing:2px;text-transform:uppercase;
  color:var(--muted);margin-bottom:16px}
.fl-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.fc{border:1px solid var(--border);border-radius:14px;padding:20px 22px;position:relative;overflow:hidden}
.fc::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--bu),var(--bu-mid))}
.fc.ret::before{background:linear-gradient(90deg,var(--pr),var(--pr-mid))}
.fc-lbl{font-size:10px;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;
  color:var(--muted);margin-bottom:14px}
.fc-route{display:flex;align-items:center;margin-bottom:14px}
.fc-ep{flex:1}.fc-ep.r{text-align:right}
.fc-code{font-size:26px;font-weight:900;letter-spacing:-.03em;color:var(--text);line-height:1}
.fc-time{font-size:15px;font-weight:700;color:var(--text);margin-top:2px}
.fc-city{font-size:10px;color:var(--muted);margin-top:3px;line-height:1.4}
.fc-mid{min-width:72px;text-align:center;padding:0 6px}
.fc-fno{font-size:12px;font-weight:700;color:var(--text);margin-bottom:4px}
.fc-arrow{display:flex;align-items:center;gap:2px;color:var(--muted);font-size:13px}
.fc-arrow::before,.fc-arrow::after{content:'';flex:1;height:1px;background:var(--border)}
.fc-meta{display:flex;gap:14px;font-size:11px;color:var(--muted);
  border-top:1px solid var(--border);padding-top:12px;margin-top:2px}

/* STICKY NAV */
.city-nav{position:sticky;top:0;z-index:200;background:rgba(255,255,255,.96);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--border);
  box-shadow:0 2px 8px rgba(0,0,0,.06);display:flex;align-items:stretch;overflow-x:auto}
.city-nav::-webkit-scrollbar{display:none}
.nav-btn{padding:12px 18px;border:none;background:none;cursor:pointer;
  font-size:13px;font-weight:600;color:var(--muted);display:flex;align-items:center;gap:7px;
  white-space:nowrap;border-bottom:3px solid transparent;text-decoration:none;
  transition:color .15s,border-color .15s;font-family:inherit}
.nav-btn:hover{color:var(--text)}
.nav-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.nav-btn.pr .nav-dot{background:var(--pr)}.nav-btn.sa .nav-dot{background:var(--sa)}
.nav-btn.vi .nav-dot{background:var(--vi)}.nav-btn.bu .nav-dot{background:var(--bu)}
.nav-btn.pr.active{color:var(--pr);border-bottom-color:var(--pr)}
.nav-btn.sa.active{color:var(--sa);border-bottom-color:var(--sa)}
.nav-btn.vi.active{color:var(--vi);border-bottom-color:var(--vi)}
.nav-btn.bu.active{color:var(--bu);border-bottom-color:var(--bu)}
.nav-sp{flex:1}

/* OVERVIEW */
.overview{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;
  background:var(--border);margin-bottom:44px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.ov{background:var(--white);padding:20px 18px 18px;position:relative}
.ov::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.ov.pr::before{background:var(--pr)}.ov.sa::before{background:var(--sa)}
.ov.vi::before{background:var(--vi)}.ov.bu::before{background:var(--bu)}
.ov-city{font-size:10px;font-weight:800;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px}
.ov.pr .ov-city{color:var(--pr)}.ov.sa .ov-city{color:var(--sa)}
.ov.vi .ov-city{color:var(--vi)}.ov.bu .ov-city{color:var(--bu)}
.ov-dates{font-size:13px;font-weight:700;color:var(--text);margin-bottom:4px}
.ov-nights{font-size:11px;color:var(--muted);margin-bottom:8px}
.ov-hotel{font-size:11px;color:var(--muted);padding:4px 8px;background:var(--bg);
  border-radius:6px;display:block;margin-bottom:5px;text-decoration:none}
a.ov-hotel:hover{background:var(--border)}
.ov-tip{display:flex;align-items:center;gap:5px;font-size:11px;font-weight:600;
  padding:5px 8px;border-radius:6px;text-decoration:none;
  background:var(--sa-pale);color:var(--sa);margin-top:2px}
.ov-tip:hover{opacity:.8}

/* MAIN */
.wrap{max-width:860px;margin:0 auto;padding:0 20px 80px}
.sec-head{font-size:18px;font-weight:800;letter-spacing:-.02em;color:var(--text);
  margin-bottom:28px;display:flex;align-items:center;gap:10px}
.sec-head::before{content:'';display:block;width:4px;height:20px;background:var(--text);border-radius:2px}

/* TIMELINE */
.timeline{position:relative}
.timeline::before{content:'';position:absolute;left:52px;top:0;bottom:0;width:1px;background:var(--border)}
.day{display:grid;grid-template-columns:52px 1fr;margin-bottom:14px}
.day-meta{padding-top:18px;padding-right:18px;text-align:right;position:relative}
.day-num{font-size:20px;font-weight:900;line-height:1;color:var(--text)}
.day-wd{font-size:10px;color:var(--muted);font-weight:600}
.tl-dot{position:absolute;right:-5px;top:21px;width:9px;height:9px;border-radius:50%;
  border:2px solid var(--bg);z-index:2;background:var(--muted)}
.tl-dot.pr{background:var(--pr)}.tl-dot.sa{background:var(--sa)}
.tl-dot.vi{background:var(--vi)}.tl-dot.bu{background:var(--bu)}
.day-body{padding:14px 0 14px 26px}
.badge{display:inline-flex;align-items:center;padding:3px 10px;border-radius:99px;
  font-size:11px;font-weight:700;letter-spacing:.3px}
.badge.pr{background:var(--pr-pale);color:var(--pr)}.badge.sa{background:var(--sa-pale);color:var(--sa)}
.badge.vi{background:var(--vi-pale);color:var(--vi)}.badge.bu{background:var(--bu-pale);color:var(--bu)}
.day-head{display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap}
.day-ttl{font-size:15px;font-weight:700;color:var(--text)}
.day-cnt{font-size:11px;color:var(--muted);margin-left:auto}
.xfer{display:flex;align-items:center;gap:10px;background:var(--bg);
  border:1px dashed #CCD4DC;border-radius:9px;padding:9px 14px;
  margin-bottom:10px;font-size:12px;color:var(--muted)}
.xfer-type{font-weight:700;font-size:10px;letter-spacing:1px;text-transform:uppercase;
  padding:2px 7px;background:rgba(0,0,0,.06);border-radius:4px}
.xfer-route{display:flex;align-items:center;gap:6px;font-weight:700;font-size:13px;color:var(--text)}
.xfer-note{margin-left:auto;font-size:11px}
.acts{background:var(--white);border-radius:12px;border:1px solid var(--border);
  box-shadow:0 1px 4px rgba(0,0,0,.05);overflow:hidden}
.act{display:flex;align-items:flex-start;gap:11px;padding:11px 14px;
  border-bottom:1px solid var(--border)}
.act:last-child{border-bottom:none}
.act-ico{width:30px;height:30px;border-radius:8px;display:flex;align-items:center;
  justify-content:center;font-size:11px;flex-shrink:0;font-weight:700;letter-spacing:-.02em}
.ico-fl{background:#E8F4FB;color:#1A6699}.ico-ht{background:#FEF9E7;color:#9A7D0A}
.ico-sk{background:#FDF2F2;color:#B03A3A}.ico-at{background:#F5F0FB;color:#6B3FA0}
.ico-nt{background:#F0FAF5;color:#2E7D52}.ico-mu{background:#FEF0E7;color:#C0561A}
.ico-sp{background:#E8F4FB;color:#1A6699}.ico-bo{background:#EEF6FB;color:#1565C0}
.ico-dr{background:#F0F2F4;color:#5D6D7E}.ico-ny{background:#EEE8F8;color:#5B2C8E}
.ico-sh{background:#FEF9E7;color:#9A7D0A}.ico-ca{background:#F0FAF5;color:#2E7D52}
.act-body{flex:1}
.act-name{font-size:13px;font-weight:700;color:var(--text)}
.act-name a{color:inherit;text-decoration:none}
.act-name a:hover{text-decoration:underline;opacity:.8}
.act-desc{font-size:11px;color:var(--muted);margin-top:2px}
.act-tag{font-size:10px;font-weight:600;padding:2px 7px;border-radius:99px;
  background:var(--bg);color:var(--muted);align-self:center;white-space:nowrap;letter-spacing:.3px}
.act-tag.opt{background:#FEF9E7;color:#9A7D0A}
.act-tag.tbd{background:var(--vi-pale);color:var(--vi)}
.act-tag.time{background:var(--bu-pale);color:var(--bu)}

/* HIGHLIGHTS */
.hi-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(195px,1fr));gap:14px;margin-top:8px}
.hi-card{background:var(--white);border-radius:14px;border:1px solid var(--border);
  padding:20px 18px;box-shadow:0 1px 4px rgba(0,0,0,.04);position:relative;overflow:hidden}
.hi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px}
.hi-card.pr::before{background:var(--pr)}.hi-card.sa::before{background:var(--sa)}
.hi-card.vi::before{background:var(--vi)}.hi-card.bu::before{background:var(--bu)}
.hi-lbl{font-size:10px;font-weight:800;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px}
.hi-card.pr .hi-lbl{color:var(--pr)}.hi-card.sa .hi-lbl{color:var(--sa)}
.hi-card.vi .hi-lbl{color:var(--vi)}.hi-card.bu .hi-lbl{color:var(--bu)}
.hi-item{display:flex;align-items:center;gap:8px;padding:5px 0;
  font-size:13px;color:var(--text);border-bottom:1px solid var(--border)}
.hi-item:last-child{border-bottom:none}
.hi-item::before{content:'';width:5px;height:5px;border-radius:50%;flex-shrink:0}
.hi-card.pr .hi-item::before{background:var(--pr)}.hi-card.sa .hi-item::before{background:var(--sa)}
.hi-card.vi .hi-item::before{background:var(--vi)}.hi-card.bu .hi-item::before{background:var(--bu)}
.hi-name{flex:1}
.map-link{margin-left:4px;font-size:10px;font-weight:600;color:var(--muted);
  text-decoration:none;padding:2px 6px;border-radius:4px;background:var(--bg);
  flex-shrink:0;white-space:nowrap}
.map-link:hover{background:var(--border);color:var(--text)}

/* CROSS-NAV */
.hi-jump{font-size:10px;font-weight:700;color:var(--muted);text-decoration:none;
  padding:2px 8px;border-radius:99px;background:var(--bg);border:1px solid var(--border);
  white-space:nowrap;transition:all .15s;flex-shrink:0}
.hi-jump:hover{background:var(--border);color:var(--text)}
.hi-card-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.hi-back{font-size:10px;font-weight:700;color:var(--muted);text-decoration:none;
  padding:2px 8px;border-radius:99px;background:var(--bg);border:1px solid var(--border);
  white-space:nowrap;transition:all .15s}
.hi-back:hover{background:var(--border);color:var(--text)}

/* RESPONSIVE */
@media(max-width:640px){
  .overview{grid-template-columns:repeat(2,1fr)}
  .fl-grid{grid-template-columns:1fr}
  .timeline::before{left:40px}
  .day{grid-template-columns:40px 1fr}
  .day-num{font-size:16px}
  .day-body{padding-left:18px}
  .route-line{min-width:12px}
  .fc-code{font-size:20px}
}
@media(max-width:400px){.overview{grid-template-columns:1fr}}
"""

# ── JavaScript ────────────────────────────────────────────────────────────────
JS = """\
(function(){
  var anchors={}, btns={};
  document.querySelectorAll('[data-city-anchor]').forEach(function(el){
    var cid=el.dataset.cityAnchor;
    if(!anchors[cid]) anchors[cid]=el;
  });
  document.querySelectorAll('.nav-btn[data-city]').forEach(function(b){
    btns[b.dataset.city]=b;
  });
  if(!Object.keys(anchors).length) return;
  var obs=new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting){
        var cid=en.target.dataset.cityAnchor;
        Object.values(btns).forEach(function(b){b.classList.remove('active')});
        if(btns[cid]) btns[cid].classList.add('active');
      }
    });
  },{rootMargin:'-15% 0px -70% 0px'});
  Object.values(anchors).forEach(function(el){obs.observe(el)});
})();
"""

# ── builders ─────────────────────────────────────────────────────────────────

def build_hero(meta, cities):
    stops = []
    for i, c in enumerate(cities):
        code = cc(c['id'])
        stops.append(f"""
      <div class="route-stop">
        <div class="route-dot {code}">{e(c['name_en'][:3].upper())}</div>
        <div class="route-label">{e(c['name_ko'])}</div>
        <div class="route-nights">{c['nights']}박 {c['nights']+1}일</div>
      </div>""")
        if i < len(cities) - 1:
            stops.append('<div class="route-line"></div>')
    return f"""
<div class="hero">
  <div class="hero-ey">{e(meta.get('duration',''))} · 가족 여행</div>
  <h1>{e(meta.get('title','동유럽 가족여행'))}</h1>
  <p class="hero-sub">{e(meta.get('dates_ko',''))}</p>
  <div class="route">{''.join(stops)}</div>
</div>"""


def build_flights(flights):
    if not flights:
        return ''

    def card(f, label, extra_cls=''):
        dep_date = f.get('dep_date','')
        arr_date = f.get('arr_date','')
        date_info = dep_date
        if arr_date and arr_date != dep_date:
            date_info += f' → {arr_date}'
        return f"""
    <div class="fc {extra_cls}">
      <div class="fc-lbl">{e(label)}</div>
      <div class="fc-route">
        <div class="fc-ep">
          <div class="fc-code">{e(f.get('dep_airport',''))}</div>
          <div class="fc-time">{e(f.get('dep_time',''))}</div>
          <div class="fc-city">{e(f.get('dep_city',''))}</div>
        </div>
        <div class="fc-mid">
          <div class="fc-fno">{e(f.get('flight_no',''))}</div>
          <div class="fc-arrow">&#9992;</div>
        </div>
        <div class="fc-ep r">
          <div class="fc-code">{e(f.get('arr_airport',''))}</div>
          <div class="fc-time">{e(f.get('arr_time',''))}</div>
          <div class="fc-city">{e(f.get('arr_city',''))}</div>
        </div>
      </div>
      <div class="fc-meta">
        <span>{e(f.get('class',''))}</span>
        <span>수하물 {e(f.get('baggage',''))}</span>
        <span>{e(date_info)}</span>
      </div>
    </div>"""

    ob = flights.get('outbound', {})
    rt = flights.get('return', {})
    return f"""
<div class="fl-section">
  <div class="fl-inner">
    <div class="fl-label">항공편 정보</div>
    <div class="fl-grid">
      {card(ob, '가는 편')}
      {card(rt, '돌아오는 편', 'ret')}
    </div>
  </div>
</div>"""


def build_city_nav(cities):
    btns = []
    for c in cities:
        code = cc(c['id'])
        btns.append(f"""
  <a class="nav-btn {code}" href="#{e(c['id'])}" data-city="{e(c['id'])}">
    <span class="nav-dot"></span>{e(c['name_ko'])}
    <span style="opacity:.45;font-weight:400;font-size:11px">{c['nights']}박</span>
  </a>""")
    return f"""
<nav class="city-nav">
  {''.join(btns)}
  <div class="nav-sp"></div>
</nav>"""


def build_overview(cities):
    cells = []
    for c in cities:
        code = cc(c['id'])
        hotel = c.get('hotel')
        hotel_url = c.get('hotel_map_url')
        if hotel and hotel_url:
            hotel_html = f'<a class="ov-hotel" href="{e(hotel_url)}" target="_blank">{e(hotel)}</a>'
        elif hotel:
            hotel_html = f'<span class="ov-hotel">{e(hotel)}</span>'
        else:
            hotel_html = '<span class="ov-hotel">숙소 미정</span>'

        tips_html = ''
        for tip in (c.get('tips') or []):
            if tip.get('type') == 'cafe':
                tips_html += f'<a class="ov-tip" href="{e(tip["url"])}" target="_blank">☕ {e(tip["name"])}</a>'

        cells.append(f"""
  <div class="ov {code}">
    <div class="ov-city">{e(c['name_en'])} · {e(c['name_ko'])}</div>
    <div class="ov-dates">{e(c['dates_ko'])}</div>
    <div class="ov-nights">{c['nights']}박 {c['nights']+1}일</div>
    {hotel_html}{tips_html}
  </div>""")
    return f'<div class="overview">{"".join(cells)}</div>'


def build_xfer(xfer):
    label = XFER_LABEL.get(xfer.get('type','drive'), xfer.get('type',''))
    return f"""
  <div class="xfer">
    <span class="xfer-type">{e(label)}</span>
    <span class="xfer-route">
      <span>{e(xfer.get('from',''))}</span>
      <span style="color:var(--muted);margin:0 4px">&#8594;</span>
      <span>{e(xfer.get('to',''))}</span>
    </span>
    <span class="xfer-note">{e(xfer.get('note',''))}</span>
  </div>"""


def build_activity(act):
    atype = act.get('type','sight')
    ico_cls, ico_lbl = ICON_MAP.get(atype, ('ico-sk','관광'))
    name = act.get('name','')
    desc = act.get('desc','')
    tag  = act.get('tag')
    murl = act.get('map_url')

    name_inner = f'<a href="{e(murl)}" target="_blank">{e(name)}</a>' if murl else e(name)

    tag_html = ''
    if tag:
        if tag == '선택':   tcls = 'opt'
        elif tag == '미정': tcls = 'tbd'
        elif tag in ('20:10','13:40','오전'): tcls = 'time'
        else: tcls = ''
        tag_html = f'<span class="act-tag {tcls}">{e(tag)}</span>'

    desc_html = f'<div class="act-desc">{e(desc)}</div>' if desc else ''
    return f"""
    <div class="act">
      <div class="act-ico {ico_cls}">{e(ico_lbl)}</div>
      <div class="act-body">
        <div class="act-name">{name_inner}</div>
        {desc_html}
      </div>
      {tag_html}
    </div>"""


def build_timeline(days, cities_map):
    # track first day per city and prev city
    city_first = {}
    prev_cid   = None
    for d in days:
        cid = d.get('city_id')
        if cid and cid not in city_first:
            city_first[cid] = d.get('day_num')
        d['_prev'] = prev_cid
        if cid:
            prev_cid = cid

    parts = []
    for d in days:
        cid   = d.get('city_id')
        code  = cc(cid)
        dnum  = d.get('day_num','')
        wday  = d.get('weekday','')
        title = d.get('title','')
        xfer  = d.get('transfer')
        prev  = d.get('_prev')

        try:
            dt = datetime.strptime(d.get('date',''), '%Y-%m-%d')
            date_lbl = str(dt.day)
        except ValueError:
            date_lbl = ''

        # anchor on first day of each city
        anchor = ''
        if cid and city_first.get(cid) == dnum:
            anchor = f' id="{e(cid)}" data-city-anchor="{e(cid)}"'

        # badges
        if xfer and prev:
            prev_name = cities_map.get(prev, {}).get('name_ko','')
            cur_name  = cities_map.get(cid,  {}).get('name_ko','') if cid else ''
            badges = (f'<span class="badge {cc(prev)}">{e(prev_name)}</span>'
                      f'<span style="color:var(--muted);font-size:13px;padding:0 2px">&#8594;</span>'
                      + (f'<span class="badge {code}">{e(cur_name)}</span>' if cid else ''))
        elif cid:
            badges = f'<span class="badge {code}">{e(cities_map.get(cid,{}).get("name_ko",""))}</span>'
        else:
            badges = ''

        acts_html = ''.join(build_activity(a) for a in d.get('activities', []))

        parts.append(f"""
  <div class="day"{anchor}>
    <div class="day-meta">
      <div class="day-num">{date_lbl}</div>
      <div class="day-wd">{e(wday)}</div>
      <div class="tl-dot {code}"></div>
    </div>
    <div class="day-body">
      <div class="day-head">
        {badges}
        <span class="day-ttl">{e(title)}</span>
        <span class="day-cnt">DAY {dnum}</span>
        {f'<a class="hi-jump" href="#hi-{e(cid)}">볼거리 ↓</a>' if cid else ''}
      </div>
      {build_xfer(xfer) if xfer else ''}
      <div class="acts">{acts_html}</div>
    </div>
  </div>""")

    return '<div class="timeline">' + ''.join(parts) + '</div>'


def build_highlights(cities):
    cards = []
    for c in cities:
        code = cc(c['id'])
        items = []
        for h in (c.get('highlights') or []):
            murl = h.get('map_url')
            map_btn = f'<a class="map-link" href="{e(murl)}" target="_blank">지도</a>' if murl else ''
            items.append(f'<div class="hi-item"><span class="hi-name">{e(h["name"])}</span>{map_btn}</div>')
        cards.append(f"""
  <div class="hi-card {code}" id="hi-{e(c['id'])}">
    <div class="hi-card-head">
      <div class="hi-lbl">{e(c['name_en'])} · {e(c['name_ko'])}</div>
      <a class="hi-back" href="#{e(c['id'])}">↑ 일정으로</a>
    </div>
    {''.join(items)}
  </div>""")
    return (f'<h2 class="sec-head" style="margin-top:52px">도시별 주요 볼거리</h2>'
            f'<div class="hi-grid">{"".join(cards)}</div>')


# ── main assembler ────────────────────────────────────────────────────────────

def build_html(data):
    meta    = data.get('meta', {})
    flights = data.get('flights', {})
    cities  = data.get('cities', [])
    days    = data.get('days', [])
    cities_map = {c['id']: c for c in cities}

    title = e(meta.get('title', '동유럽 가족여행'))
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} · 2026년 9월</title>
  <style>{CSS}</style>
</head>
<body>
{build_hero(meta, cities)}
{build_flights(flights)}
{build_city_nav(cities)}
{build_overview(cities)}
<div class="wrap">
  <h2 class="sec-head">일정표</h2>
  {build_timeline(days, cities_map)}
  {build_highlights(cities)}
</div>
<script>{JS}</script>
</body>
</html>"""


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    inp = sys.argv[1] if len(sys.argv) > 1 else 'europe_2026.yaml'
    out = sys.argv[2] if len(sys.argv) > 2 else 'europe_2026.html'
    data = yaml.safe_load(Path(inp).read_text('utf-8'))
    Path(out).write_text(build_html(data), 'utf-8')
    print(f"생성 완료 -> {out}")
