"""Prepare raster media once for every renderer; never embed original redacted bytes."""
from io import BytesIO
from tempfile import TemporaryDirectory
from pathlib import Path
from PIL import Image, ImageDraw
from annotate_screenshot import annotate, validate_box
from spec import asset_path, SpecError

def prepare_image(screenshot, spec_path, number, accent, asset_root=None):
    path = asset_path(screenshot['path'], spec_path, asset_root)
    with Image.open(path) as source:
        if source.format not in ('PNG', 'JPEG', 'WEBP'):
            raise SpecError('Unsupported raster format')
        img = source.convert('RGB')
    if screenshot.get('width', img.width) != img.width or screenshot.get('height', img.height) != img.height:
        raise SpecError('Screenshot dimensions changed; recheck highlight evidence')
    for box in screenshot.get('redactions', []):
        x,y,w,h = validate_box(box, img.width, img.height)
        ImageDraw.Draw(img).rectangle((x,y,x+w-1,y+h-1), fill='black')
    if 'highlight' in screenshot:
        validate_box(screenshot['highlight'], img.width, img.height)
    if screenshot.get('highlight') and not screenshot.get('annotated'):
        validate_box(screenshot['highlight'], img.width, img.height)
        with TemporaryDirectory(prefix='watc-') as temp:
            clean, marked = Path(temp)/'clean.png', Path(temp)/'marked.png'
            img.save(clean)
            annotate(str(clean), str(marked), tuple(screenshot['highlight']), number, accent)
            with Image.open(marked) as result:
                img = result.copy()
    img.info.clear()  # Pillow may otherwise preserve EXIF while converting formats.
    output = BytesIO()
    img.save(output, format='PNG')
    return output.getvalue(), img.size
