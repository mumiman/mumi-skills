import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from io import BytesIO
from PIL import Image
from docx import Document
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from spec import normalize, SpecError, script_json, asset_path
from build_docx import build_docx
from build_overlay import build_overlay
from build_preview import build_preview
from media import prepare_image
from inspect_html import inventory
from validate_spec import validate

ROOT=Path(__file__).resolve().parents[1]

class Generators(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)
        self.raw={'title':'คู่มือทดสอบ','language':'th','steps':[{'caption':'กด “New report”','selector':'#new-report'}]}
    def tearDown(self): self.tmp.cleanup()
    def write(self,raw=None):
        p=self.path/'steps.json';p.write_text(json.dumps(raw or self.raw,ensure_ascii=False));return p
    def image_spec(self):
        Image.new('RGB',(400,300),'white').save(self.path/'shot.png')
        spec,_=normalize(self.raw)
        spec['steps'][0]['screenshot']={'path':'shot.png','width':400,'height':300,'highlight':[100,100,120,40],'redactions':[[10,10,40,30]],'privacy_reviewed':True}
        return spec
    def test_legacy_migration(self):
        self.raw['steps'][0].update(number=7,description='Overlay text',selector_index=1)
        s,w=normalize(self.raw)
        self.assertEqual(s['language'],'th');self.assertEqual(s['steps'][0]['instruction'],'กด “New report”')
        self.assertEqual(s['steps'][0]['overlay']['instruction'],'Overlay text')
        self.assertEqual(s['steps'][0]['target']['index'],1);self.assertTrue(w)
        self.assertEqual(s['steps'][0]['evidence']['status'],'unverified')
    def test_schema_rejections(self):
        cases=[{'steps':[]},{'steps':[{'caption':'x'}],'color':'#x; background:red'},{'steps':[{'caption':'x','selector_index':-1}]},{'schema_version':3,'steps':[{'caption':'x'}]},{'steps':[{'caption':'x','target':{'timeout_ms':999999}}]}]
        for value in cases:
            with self.subTest(value=value),self.assertRaises(SpecError):normalize(value)
    def test_duplicate_ids_and_forward_dependency(self):
        with self.assertRaises(SpecError):normalize({'steps':[{'id':'a','caption':'x'},{'id':'a','caption':'y'}]})
        with self.assertRaises(SpecError):normalize({'steps':[{'id':'a','caption':'x','depends_on':['b']},{'id':'b','caption':'y'}]})
    def test_verified_needs_source(self):
        s,_=normalize(self.raw);s['steps'][0]['evidence']['status']='verified'
        with self.assertRaises(SpecError):normalize(s)
    def test_script_escape_and_literal_markers(self):
        attack='</script><script>globalThis.compromised=true</script> __TITLE__ & \u2028'
        self.raw['steps'][0]['caption']=attack
        p=self.write();out=self.path/'overlay.html';build_overlay(p,out)
        text=out.read_text();self.assertEqual(text.count('</script>'),1);self.assertNotIn('</script><script>globalThis',text)
        self.assertEqual(json.loads(script_json(attack)),attack)
        self.assertIn('__TITLE__',text)
    def test_external_bundle_no_inline_code(self):
        out=self.path/'external.html';build_overlay(self.write(),out,True)
        text=out.read_text();self.assertNotIn('onclick=',text);self.assertNotIn('<style',text);self.assertNotIn('<script>',text)
        self.assertTrue((self.path/'external.css').exists());self.assertTrue((self.path/'external.init.js').exists())
    def test_preview_never_executes_supplied_html(self):
        self.raw['steps'][0]['caption']='<img src=x onerror=alert(1)>'
        out=self.path/'preview.html';build_preview(self.write(),out)
        self.assertNotIn('<script',out.read_text());self.assertIn('&lt;img',out.read_text())
        self.assertIn('ไม่ได้จำลองการส่งข้อมูล',out.read_text())
    def test_redaction_reencoded_and_annotations(self):
        spec=self.image_spec();p=self.write(spec)
        data,dimensions=prepare_image(spec['steps'][0]['screenshot'],p,1,'#2563EB')
        image=Image.open(BytesIO(data));self.assertEqual(dimensions,(400,300));self.assertEqual(image.getpixel((20,20)),(0,0,0))
        self.assertNotEqual(image.getpixel((100,110)),(255,255,255))
    def test_geometry_rejected(self):
        for box in [[-1,0,20,20],[0,0,0,5],[390,0,20,20],[0,0,1,999]]:
            spec=self.image_spec();spec['steps'][0]['screenshot']['highlight']=box;p=self.write(spec)
            with self.assertRaises(SpecError):prepare_image(spec['steps'][0]['screenshot'],p,1,'#2563EB')
    def test_redaction_fractional_edges_cover_outward(self):
        spec=self.image_spec();shot=spec['steps'][0]['screenshot'];shot.pop('highlight');shot['redactions']=[[10.8,10.8,.1,.1]]
        data,_=prepare_image(shot,self.write(spec),1,'#2563EB')
        self.assertEqual(Image.open(BytesIO(data)).getpixel((10,10)),(0,0,0))
    def test_metadata_removed_from_reencoded_raster(self):
        spec=self.image_spec();shot=spec['steps'][0]['screenshot'];shot.pop('highlight');shot['path']='metadata.jpg'
        image=Image.new('RGB',(400,300),'white');exif=Image.Exif();exif[270]='PRIVATE_METADATA'
        image.save(self.path/'metadata.jpg',exif=exif,icc_profile=b'PRIVATE_ICC')
        data,_=prepare_image(shot,self.write(spec),1,'#2563EB')
        self.assertNotIn(b'PRIVATE',data);self.assertFalse(Image.open(BytesIO(data)).info)
    def test_nonfinite_and_wrong_language_fail_cleanly(self):
        for update in [{'render':{'dim':float('nan')}},{'language':[]},{'schema_version':True}]:
            with self.assertRaises(SpecError):normalize({**self.raw,**update})
    def test_annotated_image_still_validates_geometry(self):
        spec=self.image_spec();shot=spec['steps'][0]['screenshot'];shot['annotated']=True;shot['highlight']=[0,0,0,0]
        with self.assertRaises(SpecError):prepare_image(shot,self.write(spec),1,'#2563EB')
    def test_blank_controls_and_localized_instruction_rejected(self):
        for controls in [{'close':''},{'next':'  '},{'unknown':'x'}]:
            with self.assertRaises(SpecError):normalize({**self.raw,'controls':controls})
        s,_=normalize(self.raw);s['locales']={'th':{'i':' '}};s['steps'][0]['i18n']={'instruction':'i'}
        with self.assertRaises(SpecError):normalize(s)
    def test_privacy_scans_rendered_translation_and_override(self):
        s,_=normalize(self.raw);s['steps'][0]['evidence']={'kind':'source','status':'verified','source':'fixture','supports':['target']}
        for variant in ('locale','overlay','shared'):
            import copy
            case=copy.deepcopy(s)
            if variant=='locale':case['locales']={'th':{'i':'password: synthetic_test'}};case['steps'][0]['i18n']={'instruction':'i'}
            elif variant=='overlay':case['steps'][0]['overlay']['instruction']='token: synthetic_test'
            else:case['intro']='api_key: synthetic_test'
            self.assertEqual(validate(self.write(case),self.path/'qa.json',True),2)
    def test_changed_dimensions(self):
        spec=self.image_spec();spec['steps'][0]['screenshot']['width']=500;p=self.write(spec)
        with self.assertRaises(SpecError):prepare_image(spec['steps'][0]['screenshot'],p,1,'#2563EB')
    def test_path_and_symlink_guard(self):
        with tempfile.TemporaryDirectory() as outside:
            photo=Path(outside)/'private.png';Image.new('RGB',(20,20)).save(photo)
            (self.path/'link.png').symlink_to(photo)
            for path in [str(photo),'link.png']:
                with self.assertRaises(SpecError):asset_path(path,self.path/'steps.json')
            self.assertEqual(asset_path(str(photo),self.path/'steps.json',outside),photo.resolve())
    def test_missing_image_fails(self):
        spec=self.image_spec();spec['steps'][0]['screenshot']['path']='absent.png'
        with self.assertRaises(SpecError):build_docx(self.write(spec),self.path/'bad.docx')
        self.assertFalse((self.path/'bad.docx').exists())
    def test_docx_structure_thai_alt_text_numbering(self):
        spec=self.image_spec();spec['steps'][0]['expected_result']='เห็นแบบฟอร์ม'
        out=self.path/'guide.docx';build_docx(self.write(spec),out)
        doc=Document(out);self.assertEqual(len(doc.inline_shapes),1)
        self.assertIn('ขั้นตอนที่ 1','\n'.join(p.text for p in doc.paragraphs))
        with zipfile.ZipFile(out) as z:
            self.assertIsNone(z.testzip());xml=z.read('word/document.xml').decode()
            self.assertIn('TH Sarabun New',xml);self.assertIn('w:szCs',xml);self.assertIn('descr=',xml)
        report=json.loads(Path(str(out)+'.qa.json').read_text());self.assertEqual(report['status'],'partial')
    def test_tall_image_not_forced_to_minimum_width(self):
        Image.new('RGB',(100,2000),'white').save(self.path/'tall.png');self.raw['steps'][0]['screenshot']='tall.png'
        out=self.path/'tall.docx';build_docx(self.write(),out)
        self.assertLessEqual(Document(out).inline_shapes[0].height.inches,5.701)
    def test_strict_evidence_privacy_fails_legacy(self):
        self.assertEqual(validate(self.write(),self.path/'qa.json',True),2)
        self.assertEqual(validate(self.write(),self.path/'qa.json',False),0)
    def test_static_inventory_does_not_read_values(self):
        p=self.path/'app.html';p.write_text('<input id="safe" value="secret"><script>throw Error()</script><button data-tour="open">Open</button>')
        result=inventory(p);self.assertNotIn('secret',json.dumps(result));self.assertEqual(len(result['controls']),2)
    def test_runtime_bundle_excludes_private_source_paths(self):
        s,_=normalize(self.raw);s['steps'][0]['evidence']['source']='/private/project/notes.txt'
        out=self.path/'overlay.html';build_overlay(self.write(s),out);self.assertNotIn('/private/project',out.read_text())
    def test_locale_fallback_in_document(self):
        s,_=normalize(self.raw);s['locales']={'th':{'first':'คำแปลที่ตรวจแล้ว'}};s['steps'][0]['i18n']={'instruction':'first'}
        out=self.path/'localized.docx';build_docx(self.write(s),out)
        self.assertIn('คำแปลที่ตรวจแล้ว','\n'.join(p.text for p in Document(out).paragraphs))

if __name__=='__main__':unittest.main()
