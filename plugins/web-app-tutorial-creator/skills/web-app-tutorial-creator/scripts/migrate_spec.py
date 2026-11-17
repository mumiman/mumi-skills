"""Migrate without overwriting the input or inventing evidence."""
import argparse
import json
from pathlib import Path
from spec import load_spec, SpecError

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if Path(args.spec).resolve() == Path(args.output).resolve():
        parser.error('Migration requires a separate output file')
    try:
        spec, warnings = load_spec(args.spec)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        # Preserve asset resolution when moving the migrated spec.
        import os
        for step in spec['steps']:
            if step.get('screenshot'):
                old = Path(args.spec).resolve().parent / step['screenshot']['path']
                step['screenshot']['path'] = os.path.relpath(old, Path(args.output).resolve().parent)
        if spec.get('logo'):
            spec['logo'] = os.path.relpath(Path(args.spec).resolve().parent / spec['logo'], Path(args.output).resolve().parent)
        Path(args.output).write_text(json.dumps(spec, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        for warning in warnings: print('WARNING:', warning)
    except SpecError as exc:
        parser.exit(2, f'Invalid spec: {exc}\n')

if __name__ == '__main__': main()
