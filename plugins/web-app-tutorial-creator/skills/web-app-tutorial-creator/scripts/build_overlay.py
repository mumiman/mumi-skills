#!/usr/bin/env python3
"""Generate the legacy single-file integration harness or a strict-CSP asset bundle."""
import argparse
import html
import json
from pathlib import Path
from spec import load_spec, script_json, report, ROOT, SpecError


def runtime_spec(spec):
    # Screenshots, local evidence paths and source metadata are not needed in a live app.
    return {**{k:spec[k] for k in ('title','language','render','locales','controls') if k in spec},
            'steps':[{k:s[k] for k in ('id','title','instruction','expected_result','target','overlay','i18n','optional') if k in s} for s in spec['steps']]}


def build_overlay(spec_path, output_path, external=False):
    spec, warnings = load_spec(spec_path)
    for step in spec['steps']:
        if not step['target'].get('selector'):
            raise SpecError(f"{step['id']}: live overlay needs a grounded selector; use a storyboard when only screenshots exist")
        if 'target' not in step['evidence'].get('supports', []):
            warnings.append(f"{step['id']}: selector evidence has not been established")
    config = runtime_spec(spec)
    css = (ROOT/'assets/overlay.css').read_text()
    runtime = (ROOT/'assets/overlay.js').read_text()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if external:
        # Separate assets let the host allow script-src/style-src 'self'. No inline handlers.
        prefix = out.stem
        js_name, css_name, init_name = prefix+'.runtime.js', prefix+'.css', prefix+'.init.js'
        (out.parent/js_name).write_text(runtime, encoding='utf-8')
        (out.parent/css_name).write_text(css, encoding='utf-8')
        bootstrap = 'WATC.configure('+script_json(config)+', {styleUrl: new URL('+script_json(css_name)+', document.currentScript.src).href});\n'
        bootstrap += 'document.getElementById("watc-start").addEventListener("click", () => WATC.start());\n'
        (out.parent/init_name).write_text(bootstrap, encoding='utf-8')
        scripts = f'<script src="{html.escape(js_name, quote=True)}"></script><script src="{html.escape(init_name, quote=True)}"></script>'
    else:
        scripts = '<script id="watc-script">'+runtime+'\nWATC.configure('+script_json(config)+', {css:'+script_json(css)+'});\ndocument.getElementById("watc-start").addEventListener("click", () => WATC.start());</script>'
    th=spec['language']=='th'
    explanation=('หน้าทดสอบการติดตั้ง ยังไม่มีส่วนติดต่อของแอปจริง ใช้ preview storyboard เพื่อทบทวนเนื้อหา' if th else 'Integration harness only. The real application is not present. Use the storyboard preview to review tutorial content.')
    title=html.escape(spec['title'])
    page=f'<!doctype html><html lang="{spec["language"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title></head><body><h1>{title}</h1><p>{explanation}</p><button id="watc-start" type="button">'+('เริ่มบทเรียน' if th else 'Start tutorial')+'</button>'+scripts+'</body></html>'
    out.write_text(page, encoding='utf-8')
    report(str(out)+'.qa.json',[
        {'name':'schema_and_safe_serialization','status':'passed'},
        {'name':'live_selectors_visibility_routes_keyboard_layout','status':'not_run','reason':'Requires authorized access to the real application in a browser.'}
    ],warnings)
    print(f'Saved -> {out}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec', required=True); p.add_argument('--output', required=True)
    p.add_argument('--external', action='store_true', help='Emit same-origin JS/CSS for strict CSP integration')
    args=p.parse_args()
    try: build_overlay(args.spec,args.output,args.external)
    except (SpecError,OSError) as exc: p.exit(2,f'Cannot build overlay: {exc}\n')

if __name__=='__main__': main()
