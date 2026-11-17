#!/usr/bin/env python3
"""Static control inventory; never imports or executes scripts from the supplied file."""
import argparse
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

class Inventory(HTMLParser):
    def __init__(self):
        super().__init__(); self.controls=[]; self.attributes=Counter(); self.ignored=0

    def handle_starttag(self, tag, attrs):
        values=dict(attrs)
        for key in ('id','data-tour','data-testid','data-test','name'):
            if values.get(key): self.attributes[(key,values[key])]+=1
        if tag in ('button','a','input','select','textarea') or values.get('role') in ('button','tab','dialog'):
            if tag=='input' and values.get('type')=='hidden': return
            self.controls.append({'tag':tag,'attributes':{k:v for k,v in values.items() if k in ('id','data-tour','data-testid','data-test','name','type','role','aria-label')},'disabled':'disabled' in values})

def inventory(path):
    parser=Inventory(); parser.feed(Path(path).read_text(encoding='utf-8'))
    def quoted(value): return '"'+value.replace('\\','\\\\').replace('"','\\"').replace('\n','\\a ')+'"'
    for control in parser.controls:
        control['selectors']=[{'selector':'['+key+'='+quoted(value)+']','count':parser.attributes[(key,value)]} for key,value in control.pop('attributes').items() if key in ('id','data-tour','data-testid','data-test','name')]
        control['evidence_status']='source-only'
    return {'kind':'source','source':Path(path).name,'controls':parser.controls[:200],'truncated':len(parser.controls)>200,'limitations':['Static HTML cannot establish visibility, runtime selectors, routes or action outcomes.','JSX/Vue/Angular templates must be inspected by the agent; this parser is for HTML only.','No text values, scripts, credentials or URL queries collected.']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args()
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(inventory(args.html),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
