#!/usr/bin/env python3
"""Build native, editable Sketch layers. Run from any working directory.

Uses the repository's existing validated Sketch document as a format template.
Product photos are separate replaceable bitmap layers; no page screenshot layers.
"""
from pathlib import Path
import copy, json, zipfile, uuid, hashlib, html, re

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / '会员中心/会员中心.sketch'
W, H = 426, 924
GREEN, INK = '#00B95B', '#151916'
uid = lambda: str(uuid.uuid4()).upper()
clone = copy.deepcopy
with zipfile.ZipFile(TEMPLATE) as z:
    document = json.loads(z.read('document.json'))
    meta = json.loads(z.read('meta.json'))
    page = json.loads(z.read(next(n for n in z.namelist() if n.startswith('pages/') and n.endswith('.json'))))

def walk(n):
    yield n
    for c in n.get('layers', []): yield from walk(c)

templates = {}
for layer in walk(page): templates.setdefault(layer['_class'], clone(layer))
base_style = clone(templates['rectangle']['style'])
base_style['fills'] = []
base_style['borders'] = []
fill_template = clone(templates['rectangle']['style']['fills'][0])
border_template = clone(templates['shapePath']['style']['borders'][0])
image_data = {}
styles = {'text': {}, 'shape': {}}

def color(value):
    value = value.lstrip('#')
    return {'_class':'color','red':int(value[:2],16)/255,'green':int(value[2:4],16)/255,'blue':int(value[4:6],16)/255,'alpha':int(value[6:8],16)/255 if len(value)==8 else 1}

def style(fill=None, stroke=None, weight=1, gradient=None):
    s = clone(base_style); s['do_objectID'] = uid()
    if fill or gradient:
        f = clone(fill_template); f['color'] = color(fill or '#FFFFFF')
        if gradient:
            f['fillType'] = 1
            f['gradient']['from'], f['gradient']['to'] = gradient[0], gradient[1]
            f['gradient']['stops'] = [{'_class':'gradientStop','position':pos,'color':color(c)} for pos,c in gradient[2]]
        s['fills'] = [f]
    if stroke:
        b = clone(border_template); b['color'] = color(stroke); b['thickness'] = weight
        s['borders'] = [b]
    return s

def base(kind, name, x, y, w, h):
    n = clone(templates[kind]); n['do_objectID'] = uid(); n['name'] = name
    n['frame'] = {'_class':'rect','x':x,'y':y,'width':w,'height':h,'constrainProportions':False}
    n['isLocked'] = False; n['hasClippingMask'] = False; n['shouldBreakMaskChain'] = False
    n.pop('sharedStyleID',None)
    n['style'] = style()
    return n

board = base('artboard', '蓝蓝门店 · 首页', 0,0,W,H); board['layers'] = []
board['backgroundColor'] = color('#F5F6F6'); board['hasBackgroundColor'] = True
page = base('page','01 · 蓝蓝门店首页',0,0,0,0); page['layers'] = [board]
board['includeBackgroundColorInExport'] = True
board['exportOptions']['exportFormats'] = [{'_class':'exportFormat','absoluteSize':0,'fileFormat':'png','name':'@2x','namingScheme':0,'scale':2,'visibleScaleType':0}]
current = board

def group(name,x=0,y=0,w=W,h=H):
    global current
    n = base('group',name,x,y,w,h); n['layers'] = []; board['layers'].append(n); current = n
    return n

def add(n): current['layers'].append(n); return n

def rect(name,x,y,w,h,fill=None,r=0,stroke=None,weight=1,gradient=None):
    n=base('rectangle',name,x,y,w,h); n['style']=style(fill,stroke,weight,gradient)
    for p in n['points']: p['cornerRadius']=r
    n['fixedRadius']=r; return add(n)

def oval(name,x,y,w,h,fill=None,stroke=None,weight=1):
    n=base('oval',name,x,y,w,h); n['style']=style(fill,stroke,weight); return add(n)

def text(name,value,x,y,w,h,size=12,fill=INK,bold=False,align=0):
    n=base('text',name,x,y,w,h)
    attrs=clone(templates['text']['attributedString']['attributes'][0]['attributes'])
    attrs['MSAttributedStringFontAttribute']['attributes']={'name':'NotoSansCJKsc-Bold' if bold else 'NotoSansCJKsc-Regular','size':size}
    attrs['MSAttributedStringColorAttribute']=color(fill)
    attrs['paragraphStyle'].update(alignment=align,minimumLineHeight=h,maximumLineHeight=h)
    n['attributedString']={'_class':'attributedString','string':value,'attributes':[{'_class':'stringAttribute','location':0,'length':len(value.encode('utf-16-le'))//2,'attributes':clone(attrs)}]}
    n['style']['textStyle']={'_class':'textStyle','encodedAttributes':attrs,'verticalAlignment':0}
    n['glyphBounds']='{{0, 0}, {'+str(w)+', '+str(h)+'}}'
    key=(size,fill,bold,align,h)
    if key not in styles['text']:
        styles['text'][key]={'_class':'sharedStyle','do_objectID':uid(),'name':f'文字/{size}/{"粗体" if bold else "常规"}/{fill}','value':clone(n['style'])}
    n['sharedStyleID']=styles['text'][key]['do_objectID']
    return add(n)

def path(name, pts, fill=None, stroke=None, weight=1, closed=False):
    # Each point is absolute x,y or (x,y, incoming_x,incoming_y,outgoing_x,outgoing_y).
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    x,y=min(xs),min(ys); w,h=max(max(xs)-x,.01),max(max(ys)-y,.01)
    n=base('shapePath',name,x,y,w,h); n['style']=style(fill,stroke,weight); n['isClosed']=closed
    def norm(a,b): return '{'+str((a-x)/w)+', '+str((b-y)/h)+'}'
    n['points']=[]
    for p in pts:
        point=norm(*p[:2]); q={'_class':'curvePoint','cornerRadius':0,'cornerStyle':0,'curveMode':1,'point':point,'curveFrom':point,'curveTo':point,'hasCurveFrom':False,'hasCurveTo':False}
        if len(p)==6:
            q.update(curveMode=4,curveTo=norm(p[2],p[3]),curveFrom=norm(p[4],p[5]),hasCurveTo=True,hasCurveFrom=True)
        n['points'].append(q)
    return add(n)

def image(name,asset,x,y,w,h,r=0):
    global current
    data=(HERE/'素材'/asset).read_bytes(); digest=hashlib.sha256(data).hexdigest(); ref='images/'+digest+'.png'; image_data[ref]=data
    # Separate masking group means replacing a photo cannot affect adjacent layers.
    parent=current; n=base('group',name,x,y,w,h); n['layers']=[]; parent['layers'].append(n); current=n
    mask=rect('圆角蒙版',0,0,w,h,'#FFFFFF',r); mask['hasClippingMask']=True
    # Bitmap frame follows its source aspect ratio; clip centrally to the target.
    from PIL import Image
    with Image.open(HERE/'素材'/asset) as im: iw,ih=im.size
    scale=max(w/iw,h/ih); bw,bh=iw*scale,ih*scale
    b=base('rectangle','可替换摄影素材',(w-bw)/2,(h-bh)/2,bw,bh)
    for key in ['points','fixedRadius','edited','isClosed','pointRadiusBehaviour','rectangleCornerRadii','needsConvertionToNewRoundCorners','hasConvertedToNewRoundCorners']:
        b.pop(key,None)
    b['_class']='bitmap'; b.update(clippingMask='{{0, 0}, {1, 1}}',fillReplacesImage=False,intendedDPI=72,image={'_class':'MSJSONFileReference','_ref_class':'MSImageData','_ref':ref})
    add(b); current=parent

def plus(x,y,r=9):
    oval('加购按钮',x-r,y-r,2*r,2*r,GREEN)
    path('加号/横',[(x-4,y),(x+4,y)],stroke='#FFFFFF',weight=1.4)
    path('加号/竖',[(x,y-4),(x,y+4)],stroke='#FFFFFF',weight=1.4)

def chevron(x,y,c='#666666',s=3): path('向右箭头',[(x-s,y-s),(x,y),(x-s,y+s)],stroke=c,weight=1.2)

def cart(x,y,s=1,c='#FFFFFF'):
    def p(points): return [(x+a*s,y+b*s) for a,b in points]
    path('购物车/车框',p([(0,0),(4,0),(7,15),(20,15),(24,4),(5,4)]),stroke=c,weight=1.5*s)
    path('购物车/篮底',p([(7,15),(7,18),(20,18)]),stroke=c,weight=1.4*s)
    oval('购物车/轮一',x+7*s,y+20*s,3*s,3*s,c); oval('购物车/轮二',x+18*s,y+20*s,3*s,3*s,c)

group('00 · 背景')
rect('页面底色',0,0,W,H,'#F5F6F6')
rect('顶部鲜绿渐变',0,0,W,170,gradient=('{0, 0}','{1, 0.8}',[(0,'#08C76B'),(.55,'#30C975'),(1,'#BAECA1')]))
oval('顶部柔光',235,-90,300,260,'#FFFFFF15')
oval('背景弧线',-110,95,640,112,'#43CE7E22')
group('01 · 系统状态栏与门店')
text('系统时间','14:40',32,8,70,22,15,'#FFFFFF',True)
for i in range(4):rect('蜂窝信号/'+str(i),314+i*6,20-i*3,4,6+i*3,'#FFFFFF',1.5)
for k in [0,1]:
    path('Wi-Fi/弧'+str(k),[(346+k*3,16+k*4,346+k*3,16+k*4,351,10+k*5),(362-k*3,16+k*4,357,10+k*5,362-k*3,16+k*4)],stroke='#FFFFFF',weight=2.3)
oval('Wi-Fi/点',352.5,22,3,3,'#FFFFFF')
rect('电池',373,11.5,25,14,'#00C435',4); rect('电池正极',398,16,2,5,'#FFFFFF88',1)
text('电池电量','81ϟ',376,10.5,24,16,12,'#FFFFFF',True)
text('门店名称','蓝蓝门店',15,38,190,27,21,'#FFFFFF',True)
text('门店标语','新鲜好物 送到家',16,64,200,18,12,'#FFFFFF')
rect('微信胶囊',323,43,94,33,'#FFFFFFCC',17)
rect('胶囊分割线',370,49,0.5,20,'#D7E9D7')
for i,r in [(0,2),(1,3.2),(2,2)]:oval('更多圆点/'+str(i),338+i*7-r,59-r,2*r,2*r,'#060C06')
oval('关闭/外圈',386,51,16,16,None,'#071107',2.2);oval('关闭/中心',391,56,6,6,'#071107')
group('02 · 搜索框')
rect('搜索白底',10,86,406,39,'#FFFFFF',20)
oval('搜索图标/镜头',23,98,14,14,None,'#8D918D',1.4); path('搜索图标/手柄',[(35,110),(39,114)],stroke='#8D918D',weight=1.4)
text('搜索提示','搜索你想要的生鲜好物',46,95,286,23,14,'#929592')
rect('搜索按钮',352,89.5,61,32,GREEN,16)
text('搜索按钮文字','搜索',364,94,43,23,15,'#FFFFFF',True)
group('03 · 主视觉轮播')
image('主视觉/生鲜篮','01-生鲜篮.png',12,135,403,148,13)
rect('标题衬底渐变',12,135,247,148,r=13,gradient=('{0, 0.5}','{1, 0.5}',[(0,'#DFFFF2F5'),(.65,'#EDFFF2D9'),(1,'#FFFFFF00')]))
text('主视觉标题一','新鲜食材',37,154,230,37,29,'#138B22',True)
text('主视觉标题二','从田间到餐桌',37,188,270,38,28,'#092E15',True)
path('橙色促销底',[(38,232),(186,224),(189,244),(35,254)],fill='#FF821E',closed=True)
text('主视觉促销文案','当季鲜蔬 · 新鲜直达',49,229,190,24,13,'#FFFFFF',True)
rect('轮播指示器底',182,268,62,14,'#FFFFFFDD',7)
rect('当前页',187,271.5,11,7,GREEN,4)
for x in [204,217,230]:oval('未选中页',x,271.5,7,7,'#B5B7B4')
group('04 · 十大商品分类')
rect('分类面板',10,292,406,184,'#FFFFFF',13)
labels=['新鲜蔬菜','新鲜水果','肉禽蛋品','海鲜水产','乳品烘焙','粮油调味','休闲零食','酒水饮料','速食冻品','日用百货']
assets=['02-蔬菜.png','03-水果.png','04-肉类.png','05-海鲜.png','06-乳品.png','07-粮油.png','08-零食.png','09-饮料.png','10-速食.png','11-日用.png']
for i,(label,asset) in enumerate(zip(labels,assets)):
    x=19+(i%5)*80; y=300+(i//5)*87
    image('分类/'+label,asset,x,y,70,55,13)
    text('分类名称/'+label,label,x-5,y+61,80,22,12,align=2)
group('05 · 促销活动双卡')
rect('限时抢购/底色',13,485,197,59,'#FFE5D3',12)
image('限时抢购/番茄','12-番茄.png',121,485,89,59,12)
text('限时抢购/标题','限时抢购',26,494,130,25,17,'#F91E0B',True)
for i,t in enumerate(['08','20','36']):
    x=27+i*25
    rect('倒计时/数字底',x,521,15,14,'#FF3522',3);text('倒计时/'+t,t,x,520,15,15,10,'#FFFFFF',align=2)
    if i<2:text('倒计时/分隔符',' : ',x+14,520,11,15,10,'#FA3625')
oval('抢购箭头底',100,520,15,15,'#FF3522'); chevron(109,527,'#FFFFFF')
rect('新鲜到家/底色',217,485,198,59,'#DEF6DD',12)
text('新鲜到家/标题','新鲜到家',230,494,130,25,17,'#008D30',True)
text('配送承诺','最快30分钟送达',230,520,140,19,11,'#00A13E',True)
oval('配送箭头底',311,520,15,15,'#00B550');chevron(320,527,'#FFFFFF')
# Native vector courier and scooter, kept editable as individual shapes.
oval('电动车/后轮',339,530,13,13,'#243D32');oval('电动车/前轮',379,530,13,13,'#243D32')
oval('电动车/后轮毂',342,533,7,7,'#9CAEA1');oval('电动车/前轮毂',382,533,7,7,'#9CAEA1')
path('电动车/车身',[(342,530),(350,514),(362,514),(370,530),(380,530),(379,519),(384,511)],fill='#00A452',stroke='#087C41',weight=2,closed=True)
path('电动车/前挡',[(377,508),(384,508),(384,530),(373,531)],fill='#13BE6D',closed=True)
rect('外卖保温箱',366,505,16,14,'#F3C43B',2);rect('保温箱标记',371,508,8,2,'#31A761',.5)
oval('骑手/头',356,494,9,11,'#EDC198');rect('骑手/帽',352,491,14,5,'#00A657',2)
path('骑手/身体',[(356,505),(364,504),(367,517),(355,520),(350,514)],fill='#00A65C',closed=True)
path('骑手/腿',[(359,517),(367,520),(363,530),(357,530)],stroke='#233A30',weight=5)
path('骑手/手臂',[(356,506),(349,513),(341,511)],stroke='#0E7F4A',weight=4)
oval('骑手/手',339,509,4,4,'#EDC198')
for x,y in [(334,525),(401,516),(398,534)]:path('配送装饰叶',[(x,y),(x+7,y-5),(x+10,y-7),(x+8,y+1)],fill='#8DD442',closed=True)
group('06 · 当季推荐商品')
rect('栏目绿标',12,560,3,15,GREEN,2);rect('栏目下划线',21,572,71,4,'#6FD79B',2)
text('栏目标题','当季推荐',22,552,160,28,18,'#0A100D',True)
text('查看更多','更多',382,562,28,15,11,'#666666');chevron(412,570)
products=[('山东水蜜桃','果肉饱满 清甜多汁','12.8','13-桃子.png'),('小番茄','新鲜直采 酸甜可口','9.9','12-番茄.png'),('云南蓝莓','颗颗饱满 产地直发','19.8','14-蓝莓.png'),('有机生菜','脆嫩爽口 新鲜采摘','5.9','02-蔬菜.png')]
for i,(name,desc,price,asset) in enumerate(products):
    x=13+i*103
    rect('商品卡/'+name,x,587,96,137,'#FFFFFF',9)
    image('商品主图/'+name,asset,x,587,96,71,9)
    text('商品名/'+name,name,x+7,661,88,18,11)
    text('商品描述/'+name,desc,x+7,680,88,15,9,'#828682')
    text('货币符号/'+name,'¥',x+8,702,10,15,10,'#FF2B0C')
    text('价格/'+name,price,x+17,697,63,23,16,'#FF2B0C',True)
    plus(x+81,707,9.5)
group('07 · 热销商品与筛选')
rect('栏目绿标',12,746,3,15,GREEN,2);rect('栏目下划线',21,757,69,4,'#6FD79B',2)
text('栏目标题','热销商品',22,738,130,27,18,'#0A100D',True)
for i,label in enumerate(['全部','蔬菜','水果','肉禽','海鲜']):
    x=117+i*49
    rect('筛选/'+label,x,744,43,20,GREEN if i==0 else '#EBEDEC',11)
    text('筛选文字/'+label,label,x,743,43,22,11,'#FFFFFF' if i==0 else '#353B37',i==0,2)
text('查看更多','更多',382,748,28,16,11,'#666666');chevron(412,756)
for i,asset in enumerate(['12-番茄.png','04-肉类.png','15-玉米.png','16-三文鱼.png']):
    x=13+i*103
    rect('热销卡白边',x,774,97,93,'#FFFFFF',9)
    image('热销商品/'+asset,asset,x+3,777,91,84,7)
    if i<2:
        rect('商品角标',x+3,777,34,19,'#FF6519' if i==0 else '#FF371B',6)
        text('商品角标文字','热销' if i==0 else '推荐',x+5,777,30,19,11,'#FFFFFF',True,2)
    oval('热销加购底',x+66,831,24,24,GREEN,'#FFFFFF',1.5);cart(x+71,837,.64)
group('08 · 底部导航')
rect('底部导航白底',0,859,W,65,'#FFFFFF')
items=[('首页',38),('分类',128),('直播间',213),('购物车',298),('我的',387)]
for label,x in items:
    c=GREEN if label=='首页' else '#333733'; y=868
    if label=='首页':
        path('首页/房屋',[(x-11,y+7),(x,y),(x+12,y+7),(x+12,y+21),(x-11,y+21)],fill=c,closed=True)
        rect('首页/门',x-2.5,y+12,5,9,'#FFFFFF',2)
    elif label=='分类':
        for dx,dy in [(0,0),(12,0),(0,12),(12,12)]:rect('分类/四宫格',x-10+dx,y+1+dy,8,9,None,4,c,1.4)
    elif label=='直播间':
        oval('直播/外圈',x-11,y,22,22,None,c,1.4)
        path('直播/播放',[(x-3,y+6),(x+6,y+11),(x-3,y+17)],fill=c,closed=True)
    elif label=='购物车':
        cart(x-11,y+1,.9,c)
        oval('购物车/数量徽标',x+7,y-4,15,15,'#FF4C31','#FFFFFF',1)
        text('购物车/数量','3',x+7,y-5,15,17,10,'#FFFFFF',align=2)
    else:
        oval('我的/外圈',x-11,y,22,22,None,c,1.4);oval('我的/头像',x-4,y+4,8,8,None,c,1.2)
        path('我的/肩部',[(x-8,y+20,x-8,y+20,x-7,y+10),(x+8,y+20,x+7,y+10,x+8,y+20)],stroke=c,weight=1.2)
    text('导航/'+label,label,x-34,892,68,20,11,'#008E31' if label=='首页' else INK,label=='首页',2)

document['do_objectID']=uid();document['currentPageIndex']=0
document['pages']=[{'_class':'MSJSONFileReference','_ref_class':'MSImmutablePage','_ref':'pages/'+page['do_objectID']}]
document['layerTextStyles']['objects']=list(styles['text'].values())
document['layerStyles']['objects']=[]
document['sharedSwatches']['objects']=[]
document['fontReferences']=[]
document['assets']['colors']=[];document['assets']['colorAssets']=[]
document['assets']['images']=[]
meta['pagesAndArtboards']={page['do_objectID']:{'name':page['name'],'artboards':{board['do_objectID']:{'name':board['name']}}}}
output=HERE/'蓝蓝门店-首页.sketch'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in [('document.json',document),('meta.json',meta),('user.json',{'document':{'pageListHeight':100,'pageListCollapsed':0}}),('pages/'+page['do_objectID']+'.json',page)]:
        z.writestr(name,json.dumps(data,ensure_ascii=False,separators=(',',':')))
    for name,data in image_data.items():z.writestr(name,data)
print(output)
print('Native layer counts:',{k:sum(n['_class']==k for n in walk(page)) for k in ['artboard','group','text','rectangle','oval','shapePath','bitmap']})
