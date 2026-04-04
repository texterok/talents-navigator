#!/usr/bin/env python3
"""Generate theme HTML pages from _ru.md source files."""
import os, re, html as html_mod

SRC = "/Users/i1pl/talents-navigator/cliftonstrengths"
OUT = "/Users/i1pl/talents-navigator/theme"

THEMES = [
    ("achiever","Achiever","Достижение","exec"),
    ("activator","Activator","Катализатор","infl"),
    ("adaptability","Adaptability","Приспособляемость","rel"),
    ("analytical","Analytical","Аналитик","strat"),
    ("arranger","Arranger","Организатор","exec"),
    ("belief","Belief","Убеждение","exec"),
    ("command","Command","Распорядитель","infl"),
    ("communication","Communication","Коммуникация","infl"),
    ("competition","Competition","Конкуренция","infl"),
    ("connectedness","Connectedness","Взаимосвязанность","rel"),
    ("consistency","Consistency","Последовательность","exec"),
    ("context","Context","Контекст","strat"),
    ("deliberative","Deliberative","Осмотрительность","exec"),
    ("developer","Developer","Развитие","rel"),
    ("discipline","Discipline","Дисциплинированность","exec"),
    ("empathy","Empathy","Эмпатия","rel"),
    ("focus","Focus","Сосредоточенность","exec"),
    ("futuristic","Futuristic","Будущее","strat"),
    ("harmony","Harmony","Гармония","rel"),
    ("ideation","Ideation","Генератор идей","strat"),
    ("includer","Includer","Включенность","rel"),
    ("individualization","Individualization","Индивидуализация","rel"),
    ("input","Input","Вклад","strat"),
    ("intellection","Intellection","Мышление","strat"),
    ("learner","Learner","Ученик","strat"),
    ("maximizer","Maximizer","Максимизатор","infl"),
    ("positivity","Positivity","Позитивность","rel"),
    ("relator","Relator","Отношения","rel"),
    ("responsibility","Responsibility","Ответственность","exec"),
    ("restorative","Restorative","Восстановление","exec"),
    ("self-assurance","Self-Assurance","Уверенность","infl"),
    ("significance","Significance","Значимость","infl"),
    ("strategic","Strategic","Стратегия","strat"),
    ("woo","Woo","Обаяние","infl"),
]

DOMAIN_LABELS = {"exec":"Исполнение","infl":"Влияние","rel":"Отношения","strat":"Стратегическое мышление"}
SECTION_ICONS = ["🧭","🔍","🔥","⚠️","🌿","🤝","🔗"]
SECTION_NUMS  = ["01","02","03","04","05","06","07"]

def read_md(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def inline_md(s):
    s = html_mod.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return s

def md_to_html(text):
    lines = text.split("\n")
    out = []
    in_ul = False
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows: return
        h = '<table class="maturity-table"><thead>'
        headers = [c.strip() for c in table_rows[0].strip("|").split("|")]
        h += "<tr>" + "".join(f"<th>{inline_md(c)}</th>" for c in headers) + "</tr></thead><tbody>"
        for row in table_rows[2:]:
            cells = [c.strip() for c in row.strip("|").split("|")]
            if not any(cells): continue
            h += "<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in cells) + "</tr>"
        h += "</tbody></table>"
        out.append(h)
        table_rows.clear()
        in_table = False

    def flush_ul():
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("|"):
            if not in_table:
                flush_ul()
                in_table = True
            table_rows.append(line)
            i += 1; continue
        elif in_table:
            flush_table()

        if stripped.startswith("> "):
            flush_ul()
            out.append(f'<blockquote class="md-quote">{inline_md(stripped[2:])}</blockquote>')
            i += 1; continue

        if stripped.startswith("#### "):
            flush_ul()
            out.append(f'<h4>{inline_md(stripped[5:])}</h4>')
            i += 1; continue

        if stripped.startswith("### "):
            flush_ul()
            out.append(f'<h3>{inline_md(stripped[4:])}</h3>')
            i += 1; continue

        m = re.match(r'^[-*]\s+(.+)$', line)
        if m:
            if not in_ul:
                out.append('<ul class="marker-list">')
                in_ul = True
            out.append(f'<li>{inline_md(m.group(1))}</li>')
            i += 1; continue

        m2 = re.match(r'^\d+\.\s+(.+)$', stripped)
        if m2:
            flush_ul()
            out.append(f'<li>{inline_md(m2.group(1))}</li>')
            i += 1; continue

        if stripped:
            flush_ul()
            out.append(f'<p>{inline_md(stripped)}</p>')
        else:
            flush_ul()
        i += 1

    flush_ul()
    flush_table()
    return "\n".join(out)

def extract_sections(md_text):
    parts = re.split(r'^## \d+[\.\s]', md_text, flags=re.MULTILINE)
    titles = re.findall(r'^## \d+[\.\s]+(.+)', md_text, re.MULTILINE)
    sections = []
    for i, title in enumerate(titles):
        body = parts[i+1] if i+1 < len(parts) else ""
        body = re.split(r'^## ', body, flags=re.MULTILINE)[0]
        sections.append((title.strip(), body.strip()))
    return sections

def get_definition(body):
    for line in body.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("**Источники") and not line.startswith("---"):
            line = re.sub(r'^\*\*[^*]+\*\*:?\s*', '', line)
            line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            return line[:280]
    return ""

CSS = """
:root{--bg:#FAFAF7;--bg-card:#FFFFFF;--bg-accent:#F0EDE6;--bg-hl:#E8F4E8;
  --text:#1A1A1A;--text2:#5A5A5A;--text3:#8A8A8A;
  --accent:#2D6A4F;--al:#40916C;--all:#D8F3DC;
  --amber:#B5651D;--amb-bg:#FFF3E0;
  --red:#C44536;--red-bg:#FDECEA;
  --exec:#6D28D9;--exec-bg:#F0ECFF;
  --infl:#C2590A;--infl-bg:#FFF3E8;
  --rel:#0B7A55;--rel-bg:#E6F7F0;
  --strat:#1856C7;--strat-bg:#EBF1FF;
  --border:#E5E2DB;--bl:#F0EDE6;
  --sh:0 1px 3px rgba(0,0,0,.04);--sh2:0 4px 12px rgba(0,0,0,.06);
  --r:12px;--rs:8px;--rl:16px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);line-height:1.7;font-size:15px;-webkit-font-smoothing:antialiased}
.page{max-width:800px;margin:0 auto;padding:28px 20px 60px}
.hero{text-align:center;padding:44px 28px 36px;margin-bottom:32px;background:linear-gradient(135deg,#F8FFF8 0%,#F0EDE6 100%);border-radius:var(--rl);border:1px solid var(--border);position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-50px;right:-50px;width:180px;height:180px;background:radial-gradient(circle,var(--all) 0%,transparent 70%);opacity:.6}
.hero-domain{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;padding:5px 14px;border-radius:100px;margin-bottom:16px}
.hero-domain.exec{color:var(--exec);background:var(--exec-bg)}
.hero-domain.infl{color:var(--infl);background:var(--infl-bg)}
.hero-domain.rel{color:var(--rel);background:var(--rel-bg)}
.hero-domain.strat{color:var(--strat);background:var(--strat-bg)}
.hero h1{font-family:'DM Serif Display',serif;font-size:52px;font-weight:400;letter-spacing:-1px;margin-bottom:6px;position:relative}
.hero-sub{font-family:'DM Serif Display',serif;font-size:18px;font-style:italic;color:var(--text2);margin-bottom:18px}
.hero-def{font-size:14px;color:var(--text2);max-width:540px;margin:0 auto;line-height:1.75;position:relative}
.section{margin-bottom:12px}
.section-header{display:flex;align-items:center;gap:12px;padding:16px 20px;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r);cursor:pointer;user-select:none;transition:all .2s;box-shadow:var(--sh)}
.section-header:hover{border-color:var(--al);box-shadow:var(--sh2)}
.section-header.open{border-radius:var(--r) var(--r) 0 0;border-bottom-color:var(--bl);background:linear-gradient(to right,#F8FFF8,var(--bg-card))}
.section-icon{width:36px;height:36px;display:flex;align-items:center;justify-content:center;font-size:18px;background:var(--bg-accent);border-radius:var(--rs);flex-shrink:0}
.section-header.open .section-icon{background:var(--all)}
.section-title-group{flex:1}
.section-num{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--text3);margin-bottom:1px}
.section-title{font-family:'DM Serif Display',serif;font-size:18px;color:var(--text)}
.section-chevron{width:20px;height:20px;transition:transform .3s;color:var(--text3);flex-shrink:0}
.section-header.open .section-chevron{transform:rotate(180deg);color:var(--accent)}
.section-body{display:none;padding:24px 20px 28px;background:var(--bg-card);border:1px solid var(--border);border-top:none;border-radius:0 0 var(--r) var(--r);box-shadow:var(--sh)}
.section-body.open{display:block;animation:sd .25s ease}
@keyframes sd{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
h3{font-family:'DM Serif Display',serif;font-size:17px;font-weight:400;color:var(--text);margin:24px 0 10px}
h3:first-child{margin-top:0}
h4{font-size:13px;font-weight:700;color:var(--accent);margin:16px 0 6px;text-transform:uppercase;letter-spacing:.5px}
p{margin-bottom:12px;color:var(--text2);font-size:14px;line-height:1.7}
strong{color:var(--text);font-weight:600}
em{font-style:italic}
blockquote.md-quote{border-left:3px solid var(--al);padding:10px 16px;margin:12px 0;background:var(--all);border-radius:0 var(--rs) var(--rs) 0;font-style:italic;color:var(--text2);font-size:14px}
ul.marker-list{list-style:none;margin:10px 0 16px}
ul.marker-list li{padding:8px 0 8px 24px;position:relative;color:var(--text2);font-size:14px;border-bottom:1px solid var(--bl)}
ul.marker-list li:last-child{border-bottom:none}
ul.marker-list li::before{content:'';position:absolute;left:0;top:15px;width:7px;height:7px;background:var(--all);border:2px solid var(--accent);border-radius:50%}
table.maturity-table{width:100%;border-collapse:separate;border-spacing:0;margin:12px 0 20px;font-size:13px;border-radius:var(--rs);overflow:hidden;border:1px solid var(--border)}
table.maturity-table thead th{padding:10px 14px;text-align:left;font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.8px}
table.maturity-table thead th:first-child{background:var(--bg-accent);color:var(--text2)}
table.maturity-table thead th:nth-child(2){background:var(--red-bg);color:var(--red)}
table.maturity-table thead th:nth-child(3){background:var(--bg-hl);color:var(--accent)}
table.maturity-table td{padding:10px 14px;border-bottom:1px solid var(--bl);color:var(--text2);vertical-align:top;line-height:1.5;font-size:13px}
table.maturity-table tr:last-child td{border-bottom:none}
table.maturity-table td:first-child{font-weight:600;color:var(--text);background:#FDFCFA}
@media(max-width:600px){
  .page{padding:20px 14px 40px}
  .hero{padding:32px 16px 28px}
  .hero h1{font-size:40px}
  .section-header{padding:14px 16px}
  .section-body{padding:18px 16px 22px}
}
"""

JS = """
function toggleSection(id){
  var s=document.getElementById(id);
  var h=s.querySelector('.section-header');
  var b=s.querySelector('.section-body');
  h.classList.toggle('open');
  b.classList.toggle('open');
}
"""

def build_html(slug, en_name, ru_name, domain, sections):
    dlabel = DOMAIN_LABELS[domain]
    definition = get_definition(sections[0][1]) if sections else ""

    secs_html = ""
    for idx, (title, body) in enumerate(sections):
        icon = SECTION_ICONS[idx] if idx < len(SECTION_ICONS) else "📌"
        num  = SECTION_NUMS[idx]  if idx < len(SECTION_NUMS) else f"0{idx+1}"
        oc = " open" if idx == 0 else ""
        content = md_to_html(body)
        secs_html += f"""
  <div class="section" id="s{idx+1}">
    <div class="section-header{oc}" onclick="toggleSection('s{idx+1}')">
      <div class="section-icon">{icon}</div>
      <div class="section-title-group">
        <div class="section-num">Раздел {num}</div>
        <div class="section-title">{html_mod.escape(title)}</div>
      </div>
      <svg class="section-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
    </div>
    <div class="section-body{oc}">{content}</div>
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{en_name} — {ru_name} · CliftonStrengths</title>
<base target="_parent">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="page">
  <div class="hero">
    <div class="hero-domain {domain}">{dlabel}</div>
    <h1>{en_name}</h1>
    <div class="hero-sub">{ru_name}</div>
    <p class="hero-def">{html_mod.escape(definition)}</p>
  </div>
{secs_html}
</div>
<script>{JS}</script>
</body>
</html>"""

def main():
    os.makedirs(OUT, exist_ok=True)
    ok = 0
    for slug, en_name, ru_name, domain in THEMES:
        md_path = os.path.join(SRC, f"{slug}_ru.md")
        if not os.path.exists(md_path):
            print(f"SKIP {slug}")
            continue
        md = read_md(md_path)
        sections = extract_sections(md)
        page = build_html(slug, en_name, ru_name, domain, sections)
        out_path = os.path.join(OUT, f"{slug}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)
        ok += 1
        print(f"OK   {slug}.html ({len(sections)} sections)")
    print(f"\nDone: {ok}/{len(THEMES)}")

if __name__ == "__main__":
    main()
