#!/usr/bin/env python3
"""Validate content/evidence/media. Never claim browser or document visual checks."""
import argparse
import re
from spec import load_spec, report, SpecError, localized
from media import prepare_image

def validate(path, output, strict=False, asset_root=None):
    checks=[]; warnings=[]
    try:
        spec, warnings=load_spec(path)
        checks.append({'name':'schema','status':'passed'})
        sensitive = re.compile(r'(?i)(?:bearer\s+[a-z0-9._-]{12,}|(?:password|api[_ -]?key|token)\s*[:=]\s*\S+|\b[^\s@]+@[^\s@]+\.[^\s@]+)')
        shared = [spec['title'], spec.get('intro',''), *spec.get('prerequisites', []), *spec.get('controls', {}).values()]
        if any(sensitive.search(text) for text in shared):
            checks.append({'name':'shared_content_privacy','status':'failed' if strict else 'not_run','details':['Potential sensitive content; review before sharing.']})
        for index,step in enumerate(spec['steps'],1):
            problems=[]
            evidence=step['evidence']
            if evidence['status']!='verified' or 'target' not in evidence['supports']: problems.append('Target evidence missing or not verified')
            if step['target'].get('selector') and evidence['kind'] not in ('source','browser'): problems.append('Selector cannot be grounded in screenshots or descriptions alone')
            if step.get('expected_result') and 'outcome' not in evidence['supports']: warnings.append(step['id']+': expected result is not verified')
            if step.get('screenshot'):
                shot=step['screenshot']
                prepare_image(shot,path,index,spec['render']['accent'],asset_root)
                if not shot.get('privacy_reviewed'): problems.append('Screenshot privacy review is required')
                if shot.get('highlight') and ('width' not in shot or 'height' not in shot): problems.append('Highlight needs original image dimensions')
            displayed=[localized(spec,step,key) for key in ('title','instruction','expected_result','troubleshooting')]
            displayed.append(step.get('overlay',{}).get('instruction',''))
            displayed.append(step.get('screenshot',{}).get('alt',''))
            if any(sensitive.search(text) for text in displayed): problems.append('Potential sensitive text; review and redact before sharing')
            checks.append({'name':step['id']+':evidence_privacy','status':'failed' if strict and problems else 'not_run' if problems else 'passed','details':problems})
        checks.extend([{'name':'live_browser','status':'not_run','reason':'Requires real app access and authorized browser tools.'},{'name':'docx_visual','status':'not_run','reason':'Requires a rendered output and page inspection.'}])
    except (SpecError,OSError,ValueError) as exc:
        checks.append({'name':'spec_or_media','status':'failed','reason':str(exc)})
    result=report(output,checks,warnings)
    return 2 if result['status']=='failed' else 0

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',required=True);parser.add_argument('--report',required=True);parser.add_argument('--strict',action='store_true');parser.add_argument('--asset-root')
    args=parser.parse_args()
    raise SystemExit(validate(args.spec,args.report,args.strict,args.asset_root))
if __name__=='__main__':main()
