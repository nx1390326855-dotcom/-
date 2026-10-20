#!/usr/bin/env python3
"""Validate archive, official schemas, native layers, and current render reports."""
from pathlib import Path
import argparse,collections,hashlib,json,zipfile
from jsonschema import Draft7Validator
from PIL import Image

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--schema-dir',type=Path,required=True)
args=parser.parse_args()
target=HERE/'直播答题与红包奖励.sketch'
preview=HERE/'双手机展示.png'
layout=json.loads((HERE/'排版检查结果.json').read_text())
assert len(layout)==3 and all(r['textWidthOverflow']==0 for r in layout)
assert sum(r['textLayersChecked'] for r in layout)==142
for name,size in [('答题页',(780,1512)),('奖励弹窗',(780,1512)),('双手机展示',(1239,1152))]:
    with Image.open(HERE/(name+'.png')) as im:
        assert im.size==size
        im.verify()

# Embed the current presentation preview; replace to avoid duplicate ZIP entries.
temporary=target.with_suffix('.sketch.tmp')
with zipfile.ZipFile(target) as source, zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as out:
    for name in source.namelist():
        if name!='previews/preview.png':out.writestr(name,source.read(name))
    out.write(preview,'previews/preview.png')
temporary.replace(target)

def walk(n):
    yield n
    for c in n.get('layers',[]):yield from walk(c)

with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(set(z.namelist()))
    validated=[]
    for name in z.namelist():
        if not name.endswith('.json'):continue
        kind='page' if name.startswith('pages/') else name[:-5]
        schema=json.loads((args.schema_dir/(kind+'.schema.json')).read_text())
        Draft7Validator(schema).validate(json.loads(z.read(name)))
        validated.append(kind)
    document=json.loads(z.read('document.json'))
    page=json.loads(z.read(next(n for n in z.namelist() if n.startswith('pages/') and n.endswith('.json'))))
    nodes=list(walk(page));counts=collections.Counter(n['_class'] for n in nodes)
    assert counts['artboard']==3 and counts['text']==142 and counts['bitmap']==0
    assert len({n['do_objectID'] for n in nodes})==len(nodes)
    assert all(not n['isLocked'] for n in nodes)
    assert [(b['frame']['width'],b['frame']['height']) for b in page['layers']]==[(390,756),(390,756),(1239,1152)]
    styles={s['do_objectID'] for s in document['layerTextStyles']['objects']}
    for n in nodes:
        if n['_class']=='text':
            assert n['attributedString']['string']
            assert n['sharedStyleID'] in styles
    texts=[n['attributedString']['string'] for n in nodes if n['_class']=='text']
    for content in ['乘风破浪','答题有礼','恭喜你','30','¥1.00','获奖详情','查看答案']:
        assert content in texts
    assert sum(n.get('hasClippingMask',False) for n in nodes)==4

report={
    'artboards':[{'name':b['name'],'size':[b['frame']['width'],b['frame']['height']]} for b in page['layers']],
    'nativeLayerCounts':dict(counts),'allLayersUnlocked':True,
    'fileFormatSchema':'official @sketch-hq/sketch-file-format 6.5.0: PASSED',
    'validatedSchemas':validated,'archiveIntegrity':'PASSED',
    'sharedTextStyles':len(styles),'sharedStyleReferencesChecked':True,
    'uniqueLayerIdsChecked':True,'clippingMasksChecked':4,
    'bitmapLayers':0,'wholePageScreenshotLayers':0,
    'textWidthChecks':layout,
    'previewSource':'Actual Sketch JSON layers reconstructed with Chromium; not a macOS Sketch native export.',
    'reconstructionNotes':'Video cover, avatars, live background and reward artwork are editable vector reinterpretations of the reference.',
    'macSketchOpenVerified':False,
    'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'fileSizeBytes':target.stat().st_size,
}
(HERE/'验证结果.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
