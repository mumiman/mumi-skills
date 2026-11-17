#!/usr/bin/env python3
"""Build an offline evidence storyboard; never execute supplied HTML/JS."""
import argparse
import base64
import html
from pathlib import Path
from media import prepare_image
from spec import load_spec, localized, report, SpecError


def build_preview(spec_path, output_path, asset_root=None):
    spec, warnings=load_spec(spec_path)
    esc=html.escape
    th=spec['language']=='th'
    cards=[]
    for i,step in enumerate(spec['steps'],1):
        evidence=step['evidence']
        card=f'<section><p class="meta">{i} / {len(spec["steps"])}</p><h2>{esc(localized(spec,step,"title"))}</h2><p>{esc(localized(spec,step,"instruction"))}</p>'
        if step.get('screenshot'):
            shot=step['screenshot']
            data,_=prepare_image(shot,spec_path,i,spec['render']['accent'],asset_root)
            card+=f'<figure><img src="data:image/png;base64,{base64.b64encode(data).decode()}" alt="{esc(shot.get("alt") or localized(spec,step,"instruction"),quote=True)}"></figure>'
            if not shot.get('privacy_reviewed'): warnings.append(f'{step["id"]}: screenshot privacy review required before sharing')
        else:
            card+='<p class="meta">'+('ไม่มีภาพหลักฐานสำหรับขั้นตอนนี้' if th else 'No screenshot evidence supplied for this step.')+'</p>'
        if localized(spec,step,'expected_result'):
            card+='<p><strong>'+('ผลที่คาดหวัง: ' if th else 'Expected result: ')+'</strong>'+esc(localized(spec,step,'expected_result'))+'</p>'
        # Do not disclose local source paths in portable previews.
        card+=f'<p class="meta">Evidence: {esc(evidence["kind"])} / {esc(evidence["status"])}. '+('ผลที่คาดหวังยังไม่ได้ตรวจยืนยัน' if th and 'outcome' not in evidence['supports'] else 'Outcome not verified.' if 'outcome' not in evidence['supports'] else '')+'</p></section>'
        cards.append(card)
    banner=('ตัวอย่างบทเรียนจากหลักฐานที่ให้มา ไม่ใช่แอปที่ใช้งานจริง และไม่ได้จำลองการส่งข้อมูล' if th else 'Evidence storyboard, not the live application. No application actions or submissions are simulated.')
    css='body{font:17px/1.6 Tahoma,"Noto Sans Thai",system-ui,sans-serif;color:#17202b;background:#f5f6f8;margin:0;padding:24px}main{max-width:900px;margin:auto}section{background:white;padding:24px;margin:20px 0;border:1px solid #d5dce5;border-radius:10px}h1{font-size:28px}h2{font-size:20px}.meta{font-size:14px;color:#475569}img{max-width:100%;height:auto}figure{margin:18px 0}p{overflow-wrap:anywhere}@media(max-width:480px){body{padding:12px}section{padding:16px}}'
    page=f'<!doctype html><html lang="{spec["language"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src data:; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>{esc(spec["title"])}</title><style>{css}</style></head><body><main><h1>{esc(spec["title"])}</h1><p>{banner}</p><p>{esc(spec.get("intro",""))}</p>'+''.join(cards)+'</main></body></html>'
    Path(output_path).parent.mkdir(parents=True,exist_ok=True)
    Path(output_path).write_text(page,encoding='utf-8')
    report(str(output_path)+'.qa.json',[{'name':'schema_media_and_escaped_html','status':'passed'},{'name':'browser_visual_review','status':'not_run','reason':'Open this storyboard in a browser and inspect all images and Thai wrapping.'}],warnings)
    print(f'Saved -> {output_path}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',required=True); p.add_argument('--output',required=True); p.add_argument('--asset-root')
    args=p.parse_args()
    try:build_preview(args.spec,args.output,args.asset_root)
    except (SpecError,OSError,ValueError) as exc:p.exit(2,f'Cannot build preview: {exc}\n')
if __name__=='__main__':main()
