"""Canonical spec boundary. No network access or execution of input content."""
from __future__ import annotations
import copy
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
COLORS = {'red': '#FF4D4D', 'orange': '#FFB800', 'green': '#008060', 'blue': '#2563EB'}


class SpecError(ValueError):
    pass


def color(value):
    value = COLORS.get(str(value).lower(), value)
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        raise SpecError('Color must be red/orange/green/blue or #rrggbb')
    return value.upper()


def normalize(raw):
    if not isinstance(raw, dict):
        raise SpecError('Spec must be an object')
    import math
    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise SpecError('Non-finite numbers are not valid spec values')
        if isinstance(value, dict):
            for item in value.values(): finite(item)
        elif isinstance(value, list):
            for item in value: finite(item)
    finite(raw)
    spec = copy.deepcopy(raw)
    version = spec.get('schema_version', 1)
    if type(version) is not int or version not in (1, 2):
        raise SpecError(f'Unsupported schema_version: {version}')
    warnings = []
    if version == 1:
        warnings.append('Legacy spec migrated; evidence and privacy are not automatically verified.')
    spec['schema_version'] = 2
    language = spec.get('language', 'en')
    if not isinstance(language, str):
        raise SpecError('language must be a string')
    spec['language'] = {'english': 'en', 'thai': 'th'}.get(language, language)
    spec.setdefault('title', 'Tutorial')
    spec.setdefault('render', {})
    if not isinstance(spec['render'], dict):
        raise SpecError('render must be an object')
    spec['render'].setdefault('accent', color(spec.pop('color', '#2563EB')))
    spec['render']['accent'] = color(spec['render']['accent'])
    if not isinstance(spec.get('steps'), list):
        raise SpecError('steps must be an array')
    for index, step in enumerate(spec['steps'], 1):
        if not isinstance(step, dict):
            raise SpecError(f'Step {index} must be an object')
        step.setdefault('id', f'step-{index}')
        if 'number' in step and step['number'] != index:
            warnings.append(f"{step['id']}: display number normalized to {index}")
        step.pop('number', None)
        step.setdefault('title', '')
        step.setdefault('instruction', step.get('caption', step.get('description', '')))
        step.setdefault('target', {})
        step.setdefault('overlay', {})
        if not isinstance(step['target'], dict) or not isinstance(step['overlay'], dict):
            raise SpecError(f'Step {index}: target and overlay must be objects')
        if step.get('description') and step['description'] != step['instruction']:
            step['overlay'].setdefault('instruction', step['description'])
        for old, new in [('selector', 'selector'), ('selector_index', 'index')]:
            if old in step:
                step['target'].setdefault(new, step.pop(old))
        if 'tooltip_position' in step:
            step['overlay'].setdefault('placement', step.pop('tooltip_position'))
        if isinstance(step.get('screenshot'), str):
            step['screenshot'] = {'path': step['screenshot'], 'annotated': True}
        step.pop('caption', None)
        step.pop('description', None)
        step.setdefault('evidence', {'status': 'unverified', 'source': '', 'kind': 'user', 'supports': []})
    schema = json.loads((ROOT / 'schemas/tutorial.schema.json').read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(spec), key=lambda e: str(list(e.path)))
    if errors:
        raise SpecError('; '.join(f'{".".join(map(str, e.path)) or "spec"}: violates {e.validator}' for e in errors[:8]))
    ids = [s['id'] for s in spec['steps']]
    if len(ids) != len(set(ids)):
        raise SpecError('Step IDs must be unique')
    for index, step in enumerate(spec['steps']):
        evidence = step['evidence']
        if evidence['status'] == 'verified' and not evidence.get('source', '').strip():
            raise SpecError(f"{step['id']}: verified evidence needs a source")
        if evidence['status'] != 'verified':
            warnings.append(f"{step['id']}: evidence is {evidence['status']}")
        if not localized(spec, step, 'instruction').strip():
            raise SpecError(f"{step['id']}: localized instruction cannot be blank")
        for dep in step.get('depends_on', []):
            if dep not in ids[:index]:
                raise SpecError(f"{step['id']}: dependency must reference an earlier step: {dep}")
        if 'index' in step['target']:
            warnings.append(f"{step['id']}: legacy indexed selector requires live revalidation")
        if len(step['instruction']) > 240:
            warnings.append(f"{step['id']}: instruction is long; consider splitting the task")
    return spec, warnings


def load_spec(path):
    try:
        raw = json.loads(Path(path).read_text(encoding='utf-8'))
        return normalize(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise SpecError(str(exc)) from exc


def asset_path(value, spec_path, asset_root=None):
    base = Path(spec_path).resolve().parent
    path = Path(value)
    path = (base / path).resolve() if not path.is_absolute() else path.resolve()
    roots = [base] + ([Path(asset_root).resolve()] if asset_root else [])
    if not any(path.is_relative_to(root) for root in roots):
        raise SpecError('Asset is outside the spec directory; provide an explicitly approved --asset-root')
    if not path.is_file():
        raise SpecError(f'Asset not found: {path.name}')
    if path.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
        raise SpecError('Only local PNG, JPEG and WebP images are supported')
    return path


def localized(spec, step, key):
    locale = spec.get('locales', {}).get(spec['language'], {})
    return locale.get(step.get('i18n', {}).get(key, ''), step.get(key, ''))


def script_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def report(path, checks, warnings=()):
    result = {'checks': checks, 'warnings': list(warnings)}
    result['status'] = 'failed' if any(c['status'] == 'failed' for c in checks) else ('partial' if any(c['status'] == 'not_run' for c in checks) else 'passed')
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result
