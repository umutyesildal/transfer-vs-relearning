#!/usr/bin/env python3
"""Build a self-contained local HTML reviewer for an authoritative 64-row packet."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from transfer_vs_relearning.corpora.vngrs.d0_review import (
    read_jsonl_rows,
    review_packet_sha256,
)


def build_review_html(packet_path: str | Path, output_path: str | Path) -> Path:
    rows = read_jsonl_rows(packet_path)
    if len(rows) != 64 or len({row.get("stable_document_id") for row in rows}) != 64:
        raise ValueError("authoritative review packet must contain exactly 64 unique documents")
    required = {"stable_document_id", "selection_stratum", "excerpt", "text_sha256"}
    if any(not required.issubset(row) for row in rows):
        raise ValueError("review packet is missing mandatory display or identity fields")
    packet_hash = review_packet_sha256(rows)
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    page = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OSCAR 64 Doküman İncelemesi</title>
<style>
:root{{--bg:#f4f1e8;--paper:#fffdf7;--ink:#19231f;--muted:#66716b;--line:#d8d5ca;--good:#1f7a52;--bad:#b56a18;--danger:#a73535;--accent:#174f73}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,sans-serif}}
main{{max-width:980px;margin:32px auto;padding:0 18px}} header,.card,.toolbar{{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 8px 24px #19231f0b}}
header{{display:grid;gap:10px}} h1{{margin:0;font-size:clamp(24px,4vw,38px)}} .meta{{color:var(--muted);font-size:14px;overflow-wrap:anywhere}}
.progress{{height:12px;background:#e6e1d4;border-radius:99px;overflow:hidden}} .progress>div{{height:100%;background:var(--accent);transition:.2s}}
.toolbar{{margin:16px 0;display:flex;gap:10px;align-items:center;flex-wrap:wrap}} button,input,textarea{{font:inherit}} button{{border:1px solid var(--line);background:white;border-radius:10px;padding:9px 14px;cursor:pointer}} button:hover{{border-color:var(--accent)}} button.primary{{background:var(--accent);color:white;border-color:var(--accent)}}
input[type=text]{{min-width:240px;flex:1;padding:9px 12px;border:1px solid var(--line);border-radius:10px}} .card{{min-height:440px}}
.rowmeta{{display:flex;gap:8px;flex-wrap:wrap;color:var(--muted);font-size:13px}} .tag{{border:1px solid var(--line);border-radius:99px;padding:3px 9px}}
.excerpt{{white-space:pre-wrap;overflow-wrap:anywhere;margin:22px 0;padding:18px;background:#fff;border-left:4px solid var(--accent);border-radius:8px;min-height:190px}}
.choices{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}} .choice{{display:flex;align-items:center;gap:8px;border:2px solid var(--line);border-radius:12px;padding:13px;cursor:pointer}}
.choice:has(input:checked){{background:#eef5f1;border-color:var(--good)}} .choice.unsafe:has(input:checked){{background:#faeeee;border-color:var(--danger)}}
textarea{{width:100%;min-height:80px;margin-top:14px;padding:10px;border:1px solid var(--line);border-radius:10px;resize:vertical}}
.nav{{display:flex;justify-content:space-between;gap:10px;margin-top:16px}} .hint{{color:var(--muted);font-size:13px}} .hidden{{display:none}}
@media(max-width:650px){{.choices{{grid-template-columns:1fr}} main{{margin:12px auto}}}}
</style>
</head>
<body><main>
<header><h1>OSCAR doküman incelemesi</h1>
<div>Her kaydı yalnız görünen Türkçe metnin eğitim için kullanılabilirliğine göre işaretle.</div>
<div class="hint"><b>Kullanılabilir:</b> anlaşılır/doğal Türkçe içerik. <b>Kullanılamaz:</b> bozuk,
spam, yoğun şablon/menü veya anlamsız içerik. <b>Güvensiz:</b> kişisel veri ya da açıkça zararlı,
istismar edici veya eğitime alınmaması gereken hassas içerik.</div>
<div class="meta">Packet SHA-256: <span id="packetHash">{html.escape(packet_hash)}</span></div>
<div><span id="progressText"></span><div class="progress"><div id="progressBar"></div></div></div></header>
<div class="toolbar"><input id="reviewer" type="text" placeholder="İnceleyen kişi (zorunlu)"><button id="pending">İlk boş kayda git</button><button class="primary" id="export">Kararları JSONL indir</button></div>
<section class="card"><div class="rowmeta"><span class="tag" id="position"></span><span class="tag" id="stratum"></span><span class="tag" id="bytes"></span></div>
<div class="excerpt" id="excerpt"></div>
<div class="choices">
<label class="choice"><input type="radio" name="verdict" value="usable"> <b>1 · Kullanılabilir</b></label>
<label class="choice"><input type="radio" name="verdict" value="unusable"> <b>2 · Kullanılamaz</b></label>
<label class="choice unsafe"><input type="radio" name="verdict" value="unsafe"> <b>3 · Güvensiz</b></label>
</div>
<textarea id="notes" placeholder="İsteğe bağlı kısa not"></textarea>
<div class="nav"><button id="prev">← Önceki</button><span class="hint">Kısayol: 1/2/3, ←/→</span><button id="next">Sonraki →</button></div></section>
</main>
<script>
const docs={payload}; const packetHash={json.dumps(packet_hash)}; const key='vngrs-review-'+packetHash;
let state=JSON.parse(localStorage.getItem(key)||'{{"index":0,"answers":{{}},"reviewer":""}}');
const $=id=>document.getElementById(id); $('reviewer').value=state.reviewer||'';
function save(){{state.reviewer=$('reviewer').value;localStorage.setItem(key,JSON.stringify(state));}}
function render(){{const d=docs[state.index],a=state.answers[d.stable_document_id]||{{}};$('position').textContent=`${{state.index+1}} / ${{docs.length}}`;$('stratum').textContent=d.selection_stratum;$('bytes').textContent=`${{d.text_utf8_bytes.toLocaleString('tr-TR')}} byte`;$('excerpt').textContent=d.excerpt;$('notes').value=a.notes||'';document.querySelectorAll('[name=verdict]').forEach(x=>x.checked=x.value===a.verdict);const done=Object.values(state.answers).filter(x=>x.verdict).length;$('progressText').textContent=`${{done}} / ${{docs.length}} tamamlandı`;$('progressBar').style.width=`${{100*done/docs.length}}%`;$('prev').disabled=state.index===0;$('next').disabled=state.index===docs.length-1;save();}}
function setVerdict(v){{const id=docs[state.index].stable_document_id;state.answers[id]={{...(state.answers[id]||{{}}),verdict:v,notes:$('notes').value}};render();}}
document.querySelectorAll('[name=verdict]').forEach(x=>x.onchange=()=>setVerdict(x.value));$('notes').oninput=()=>{{const id=docs[state.index].stable_document_id;state.answers[id]={{...(state.answers[id]||{{}}),notes:$('notes').value}};save();}};$('reviewer').oninput=save;
$('prev').onclick=()=>{{if(state.index>0)state.index--;render();}};$('next').onclick=()=>{{if(state.index<docs.length-1)state.index++;render();}};
$('pending').onclick=()=>{{const i=docs.findIndex(d=>!state.answers[d.stable_document_id]?.verdict);if(i>=0)state.index=i;render();}};
document.onkeydown=e=>{{if(e.target.matches('input,textarea'))return;if(['1','2','3'].includes(e.key))setVerdict({{'1':'usable','2':'unusable','3':'unsafe'}}[e.key]);if(e.key==='ArrowLeft')$('prev').click();if(e.key==='ArrowRight')$('next').click();}};
$('export').onclick=()=>{{const reviewer=$('reviewer').value.trim();if(!reviewer)return alert('Lütfen inceleyen kişi alanını doldur.');const missing=docs.filter(d=>!state.answers[d.stable_document_id]?.verdict);if(missing.length)return alert(`${{missing.length}} kayıt henüz işaretlenmedi.`);const lines=docs.map(d=>JSON.stringify({{schema_version:1,stable_document_id:d.stable_document_id,review_packet_sha256:packetHash,verdict:state.answers[d.stable_document_id].verdict,reviewer,notes:state.answers[d.stable_document_id].notes||null}}));const blob=new Blob([lines.join('\n')+'\n'],{{type:'application/x-ndjson'}});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='human_review_decisions_'+packetHash.slice(0,12)+'.jsonl';a.click();URL.revokeObjectURL(a.href);}};
render();
</script></body></html>"""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(build_review_html(args.packet, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
