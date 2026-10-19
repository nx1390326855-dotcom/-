#!/usr/bin/env python3
"""Re-read actual Sketch layers and export an SVG/HTML inspection preview.

This is not Sketch's native macOS renderer.
"""
from pathlib import Path
import json, zipfile, base64, html, re

HERE=Path(__file__).resolve().parent
FILE=HERE/'蓝蓝门店-首页.sketch'
escape=lambda s:html.escape(str(s),quote=True)
defs=[]
checks=[]

def col(c):
    return 'rgba('+','.join(str(round(c[k]*255)) for k in ['red','green','blue'])+','+str(c.get('alpha',1))+')'

def pair(s):return [float(v) for v in s.strip('{}').split(',')]

def paint(layer):
    s=layer['style']; result=[]
    f=next((f for f in s.get('fills',[]) if f.get('isEnabled')),None)
    if f and f['fillType']==1:
        g=f['gradient']; start=pair(g['from']); end=pair(g['to']); ident='gradient'+str(len(defs))
        stops=''.join('<stop offset="'+str(p['position']*100)+'%" stop-color="'+col(p['color'])+'"/>' for p in g['stops'])
        defs.append(f'<linearGradient id="{ident}" x1="{start[0]*100}%" y1="{start[1]*100}%" x2="{end[0]*100}%" y2="{end[1]*100}%">{stops}</linearGradient>')
        result.append('fill="url(#'+ident+')"')
    else:result.append('fill="'+(col(f['color']) if f else 'none')+'"')
    b=next((b for b in s.get('borders',[]) if b.get('isEnabled')),None)
    if b:result.append('stroke="'+col(b['color'])+'" stroke-width="'+str(b['thickness'])+'" stroke-linecap="round" stroke-linejoin="round"')
    return ' '.join(result)

with zipfile.ZipFile(FILE) as z:
    assert z.testzip() is None
    page=json.loads(z.read(next(n for n in z.namelist() if n.startswith('pages/'))))
    board=page['layers'][0];W=board['frame']['width'];H=board['frame']['height']
    def node(n,svg_text=False):
        f=n['frame'];x,y,w,h=(f[k] for k in ['x','y','width','height']);kind=n['_class'];p=paint(n)
        title='<title>'+escape(n['name'])+'</title>'
        if kind in ['group','artboard','page']:
            pieces=[];active=False
            for child in n['layers']:
                if child.get('shouldBreakMaskChain') and active:pieces.append('</g>');active=False
                if child.get('hasClippingMask'):
                    if active:pieces.append('</g>')
                    ident='mask'+str(len(defs));defs.append(f'<clipPath id="{ident}">{node(child,svg_text)}</clipPath>')
                    pieces.append(f'<g clip-path="url(#{ident})">');active=True
                else:pieces.append(node(child,svg_text))
            if active:pieces.append('</g>')
            return f'<g transform="translate({x} {y})">{title}'+''.join(pieces)+'</g>'
        if kind=='rectangle':
            r=n.get('fixedRadius',n['points'][0].get('cornerRadius',0))
            return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {p}>{title}</rect>'
        if kind=='oval':return f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" {p}>{title}</ellipse>'
        if kind=='bitmap':
            ref=n['image']['_ref'];assert ref in z.namelist()
            encoded=base64.b64encode(z.read(ref)).decode()
            return f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{encoded}">{title}</image>'
        if kind=='text':
            a=n['attributedString']['attributes'][0]['attributes'];font=a['MSAttributedStringFontAttribute']['attributes'];size=font['size'];bold='Bold' in font['name'];align={0:'left',1:'right',2:'center'}[a['paragraphStyle']['alignment']]
            content=n['attributedString']['string']
            assert content
            if svg_text:
                # Noto Sans CJK SC: hhea ascent=1160, descent=-288, UPM=1000.
                # Match the CSS line box while retaining native, editable SVG text.
                anchor={'left':'start','right':'end','center':'middle'}[align]
                tx=x+({'left':0,'right':w,'center':w/2}[align])
                baseline=y+h/2+size*(1.160-.288)/2
                return f'<text x="{tx}" y="{baseline}" font-family="Noto Sans CJK SC,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{col(a["MSAttributedStringColorAttribute"])}" text-anchor="{anchor}" xml:space="preserve">{title}{escape(content)}</text>'
            checks.append({'name':n['name'],'text':content,'width':w,'height':h,'size':size,'bold':bold})
            css=f'font-family:"Noto Sans CJK SC",sans-serif;font-size:{size}px;font-weight:{700 if bold else 400};line-height:{h}px;color:{col(a["MSAttributedStringColorAttribute"])};white-space:nowrap;text-align:{align};margin:0'
            return f'<foreignObject x="{x}" y="{y}" width="{w}" height="{h}"><div xmlns="http://www.w3.org/1999/xhtml" style="{escape(css)}">{escape(content)}</div></foreignObject>'
        if kind=='shapePath':
            pts=n['points'];data=''
            def absolute(s):
                a,b=pair(s);return f'{x+a*w},{y+b*h}'
            for i,point in enumerate(pts):
                target=absolute(point['point'])
                if i==0:data='M'+target
                else:
                    prev=pts[i-1]
                    if prev.get('hasCurveFrom') or point.get('hasCurveTo'):
                        data+=' C'+absolute(prev['curveFrom'] if prev.get('hasCurveFrom') else prev['point'])+' '+absolute(point['curveTo'] if point.get('hasCurveTo') else point['point'])+' '+target
                    else:data+=' L'+target
            if n['isClosed']:data+=' Z'
            return f'<path d="{data}" {p}>{title}</path>'
        raise ValueError(kind)
    body=node(board)
    html_defs=''.join(defs)
    defs.clear()
    native_body=node(board,True)
    native_svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="svg-title svg-desc"><title id="svg-title">蓝蓝门店 · 生鲜商城首页</title><desc id="svg-desc">独立 SVG；文字、形状、图标可编辑，商品摄影以 PNG 内嵌。</desc><defs>'+''.join(defs)+'</defs>'+native_body+'</svg>'
    (HERE/'蓝蓝门店-首页.svg').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'+native_svg,encoding='utf-8')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>'+html_defs+'</defs>'+body+'</svg>'
# HTML wrapper supports XHTML text inside foreignObject consistently in Chromium.
(HERE/'设计稿预览.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>蓝蓝门店 · 原生图层检查预览</title><style>html,body{margin:0;width:426px;background:#f5f6f6}svg{display:block}</style>'+svg,encoding='utf-8')
(HERE/'文字检查数据.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print('Read-back preview generated from actual .sketch layers:',len(checks),'text layers')
