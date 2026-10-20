#!/usr/bin/env python3
"""Build native, editable Sketch layers. Run from any working directory.

Uses the repository's existing validated Sketch document as a format template.
All UI, video artwork, avatars and reward illustration are native editable layers.
"""
from pathlib import Path
import copy, json, zipfile, uuid

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / '会员中心/会员中心.sketch'
W, H = 390, 756
INK = '#151916'
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

board = base('artboard', '01 · 直播答题页', 0,0,W,H); board['layers'] = []
board['backgroundColor'] = color('#F5F6F6'); board['hasBackgroundColor'] = True
page = base('page','直播答题与红包奖励',0,0,0,0); page['layers'] = [board]
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

def oval(name,x,y,w,h,fill=None,stroke=None,weight=1,gradient=None):
    n=base('oval',name,x,y,w,h); n['style']=style(fill,stroke,weight,gradient); return add(n)

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

TEAL='#0BCBBE'
def grad(a,b):return ('{0, 0}','{1, 1}',[(0,a),(1,b)])
def shadow(n,blur=28,opacity='26',dx=8,dy=18):
    n['style']['shadows']=[{'_class':'shadow','isEnabled':True,'blurRadius':blur,'color':color('#7386AD'+opacity),'contextSettings':{'_class':'graphicsContextSettings','blendMode':0,'opacity':1},'offsetX':dx,'offsetY':dy,'spread':0}]
    return n
def avatar(x,y,size=30):
    oval('头像/外圈',x,y,size,size,'#F38194')
    oval('头像/底色',x+2,y+2,size-4,size-4,'#253D4A')
    oval('头像/头发',x+size*.28,y+size*.16,size*.44,size*.44,'#221E25')
    oval('头像/面部',x+size*.35,y+size*.24,size*.29,size*.35,'#DCA98B')
    path('头像/肩部',[(x+size*.18,y+size*.86),(x+size*.28,y+size*.60),(x+size*.69,y+size*.60),(x+size*.86,y+size*.86)],fill='#101E32',closed=True)
def star(x,y,s=7,c='#FFE598'):
    path('装饰星光',[(x,y-s),(x+2,y-2),(x+s,y),(x+2,y+2),(x,y+s),(x-2,y+2),(x-s,y),(x-2,y-2)],fill=c,closed=True)
def close_icon(x,y,r=14):
    oval('关闭弹窗/外圈',x-r,y-r,2*r,2*r,None,'#FFFFFF',1.8)
    path('关闭弹窗/斜线一',[(x-5,y-5),(x+5,y+5)],stroke='#FFFFFF',weight=1.8)
    path('关闭弹窗/斜线二',[(x+5,y-5),(x-5,y+5)],stroke='#FFFFFF',weight=1.8)

# Screen 1: video, quiz tabs, scrolling question list, fixed bottom action.
left=board
group('01 · 直播视频与播放控制')
rect('视频画布',0,0,390,218,gradient=grad('#093E40','#122D31'))
path('主视觉/橘红色块',[(0,69),(101,0),(209,0),(57,139)],fill='#D33515',closed=True)
path('主视觉/金色块',[(191,0),(285,0),(390,142),(284,215),(169,90)],fill='#EDA11E',closed=True)
path('主视觉/青绿色块',[(0,107),(110,218),(0,218)],fill='#18C0A5',closed=True)
path('主视觉/海绿色块',[(319,0),(390,0),(390,119)],fill='#24B897',closed=True)
path('主视觉/深蓝主牌',[(78,62),(257,0),(315,150),(149,218)],fill='#112944',stroke='#DBB875',weight=2,closed=True)
oval('主视觉/光斑',192,20,110,110,'#FFFFFF10')
path('主视觉/蓝色飘带',[(10,168,10,168,73,109),(146,165,89,110,189,204),(220,150,191,186,220,150)],stroke='#14C7D2AA',weight=9)
text('主视觉标题/投影','乘风破浪',71,66,260,69,52,'#7C8A91',True)
text('主视觉标题','乘风破浪',68,62,260,69,52,'#FFFDFC',True)
text('主视觉副标题','2 0 2 0  ·  毕 业 季',113,130,215,16,8,'#D5F4F8',True,2)
for x in [193,237,281]:oval('视频顶部操作底',x-10,15,20,20,'#15263255')
path('视频顶部/首页',[(184,24),(193,17),(201,24),(201,33),(184,33),(184,24)],stroke='#FFFFFF',weight=1.6)
oval('视频顶部/小程序',229,16,17,17,None,'#FFFFFF',1.5)
text('视频顶部/小程序标记','♪',232,16,13,17,13,'#FFFFFF')
path('视频顶部/刷新',[(288,25,288,25,288,12),(274,20,282,11,270,17),(274,31,269,27,274,31)],stroke='#FFFFFF',weight=1.5)
rect('在线人数底',312,12,65,25,'#0D232855',13)
text('在线人数','♧ 1432',320,15,54,18,11,'#FFFFFF')
rect('视频底部渐变',0,162,390,56,gradient=('{0, 0}','{0, 1}',[(0,'#001E3000'),(1,'#06191EDD')]))
rect('播放进度底',13,170,364,2,'#FFFFFF88',1);rect('播放进度',13,170,37,2,'#37C7DF',1)
oval('播放进度拖点',46,166,9,9,'#3CCBDD','#FFFFFF',1.6)
for x in [18,26]:rect('暂停按钮',x,190,3,13,'#FFFFFF',.5)
text('播放时间','04:23/56:48',43,187,135,19,12,'#FFFFFF')
path('播放列表/上',[(233,190),(247,190)],stroke='#FFFFFF',weight=2)
path('播放列表/中',[(233,197),(243,197)],stroke='#FFFFFF',weight=2)
path('播放列表/下',[(233,204),(247,204)],stroke='#FFFFFF',weight=2)
rect('倍速边框',269,186,31,20,None,4,'#FFFFFF',1)
text('倍速文字','倍速',270,186,29,20,10,'#FFFFFF',align=2)
rect('弹幕边框',316,187,20,18,None,4,'#FFFFFF',1)
text('弹幕文字','弹',317,187,18,18,11,'#FFFFFF',align=2)
for x,y,dx,dy in [(357,188,7,7),(375,188,-7,7),(357,204,7,-7),(375,204,-7,-7)]:
    path('全屏/四角',[(x,y+dy),(x,y),(x+dx,y)],stroke='#FFFFFF',weight=1.5)
group('02 · 直播内容标签栏')
rect('标签栏底',0,218,390,47,'#FFFFFF')
for label,x in [('互动',25),('直播介绍',114),('答题有礼',219)]:
    text('标签/'+label,label,x,229,92,26,14,'#158DCF' if label=='答题有礼' else '#202E31',True,2)
rect('选中标签下划线',257,262,17,3,'#159EE1',1)
rect('关注按钮',318,218,72,47,'#119DE3')
text('关注按钮文字','+ 关注',326,229,60,25,14,'#FFFFFF',True,2)
group('03 · 问题列表/可滚动区域')
mask=rect('列表视口蒙版',0,265,390,411,'#FFFFFF');mask['hasClippingMask']=True
rect('答题区薄荷渐变',0,265,390,491,gradient=grad('#B4F5F4','#D6F1FC'))
for i,(tag,top) in enumerate([('[单选题]',278),('[多选题]',596)]):
    rect('题目卡片/'+str(i+1),12,top,366,306,'#F6FFFFE8',18)
    text('题型标签/'+str(i+1),tag,29,top+14,60,21,13,TEAL,True)
    text('题目第一行/'+str(i+1),'下列选项中，含钙量最高且最易被',90,top+14,274,21,13,'#17292F',True)
    text('题目第二行/'+str(i+1),'人体吸收的食物是哪一种？',29,top+35,334,21,13,'#17292F',True)
    for j,option in enumerate(['A.   新鲜的鸡蛋','B.   牧场的牛奶','C.   酸酸的橘子','D.   烤焦的面包']):
        y=top+78+j*54
        rect('选项底/'+str(i)+'/'+str(j),28,y,334,46,'#FFFFFFD9',5)
        text('选项/'+str(i)+'/'+str(j),option,43,y+10,304,27,14,'#233439')
rect('滚动条轨道',384,278,3,354,'#B0E1E6',2)
rect('滚动条当前段',384,413,3,96,'#63B5BB',2)
group('04 · 固定底部答题入口')
rect('底部渐变底',0,674,390,82,gradient=('{0, 0}','{0, 1}',[(0,'#D8FCF400'),(.27,'#E1FBF8F5'),(1,'#DAF9F4')]))
rect('活动说明/后页',38,697,21,19,'#79E4D7',2)
rect('活动说明/前页',34,701,20,18,'#29CEB9',2)
for y in [706,711]:rect('活动说明/文档横线',39,y,8,1.5,'#FFFFFF',.5)
text('活动说明文字','活动说明',17,725,64,19,11,'#5A8386',align=2)
rect('观看时长条件按钮',88,689,277,52,gradient=grad('#08C9D0','#02D8A2'),r=27)
text('观看时长条件文字','观看时长需达到1时60分可答题',102,702,250,25,13,'#FFFFFF',True,2)

# Screen 2: live broadcast behind a darkened reward modal.
board=base('artboard','02 · 红包奖励弹窗',470,0,W,H);board['layers']=[]
board['backgroundColor']=color('#FFFFFF');board['hasBackgroundColor']=True
board['includeBackgroundColorInExport']=True
right=board;page['layers'].append(board)
group('01 · 直播间背景与主播信息')
rect('直播间视频底',0,0,390,671,gradient=('{0, 0}','{0.7, 1}',[(0,'#7F969E'),(.5,'#637C7E'),(1,'#6C4231')]))
oval('视频/人物柔光',116,146,210,295,'#C4B5A23F')
oval('视频/人物发型',162,200,85,100,'#3B393B55')
oval('视频/人物面部',173,221,65,90,'#CCA58B55')
path('视频/人物上身',[(90,564),(118,379),(291,379),(325,608)],fill='#90745C77',closed=True)
avatar(12,13,38)
rect('主播信息胶囊',48,18,157,29,'#3D4D5155',15)
text('主播名称','治伯直播间…',55,23,111,19,12,'#FFFFFF')
rect('主播关注按钮',149,23,44,19,'#ED3F56',10)
text('主播关注文字','+ 关注',150,23,42,19,9,'#FFFFFF',align=2)
for x in [219,233,247]:avatar(x,22,23)
text('直播间观看数','14万 ›',277,23,63,20,12,'#FFFFFF')
path('直播间刷新图标',[(369,30,369,30,369,16),(355,25,364,17,353,22),(356,38,352,33,356,38)],stroke='#FFFFFF',weight=2)
rect('分享榜标签',13,65,76,26,'#F94642',13)
text('分享榜文字','🏆 分享榜',17,68,68,19,11,'#FFFFFF',True,2)
rect('热度提示条',95,65,282,26,'#4C636C99',13)
text('热度提示文字','🔥 心动多一点  参与答题赢大奖…',103,68,267,19,11,'#FFFFFF')
for i,(label,c) in enumerate([('红包','#EB4452'),('答题','#1AD1B6'),('福袋','#42B4E4'),('宝箱','#538ADC'),('签到','#E9AF35'),('任务','#EB8753')]):
    y=111+i*65
    rect('直播侧栏/'+label,337,y,37,34,c,8)
    path('直播侧栏/礼盒/'+label,[(345,y+9),(367,y+9),(367,y+26),(345,y+26)],fill='#FFE193',closed=True)
    rect('直播侧栏/礼带/'+label,354,y+8,4,19,'#FFB448',1)
    rect('直播侧栏/标签底/'+label,337,y+32,37,16,'#ED4F7F',5)
    text('直播侧栏/标签/'+label,label,338,y+31,35,18,9,'#FFFFFF',True,2)
for i in range(10):
    y=235+i*41
    avatar(15,y,28)
    rect('聊天气泡/'+str(i),44,y+3,166 if i%2 else 204,23,'#47555266',12)
    text('聊天用户名/'+str(i),['吕晓晴','云霞青','小贝'][i%3],46,y+5,46,19,10,'#3CDED4',True)
    text('聊天内容/'+str(i),['分享了直播间','参与了投票','欢迎来到直播间'][i%3],94,y+5,141,19,10,'#FFFFFF')
group('02 · 直播间底部工具栏')
rect('聊天输入栏',58,619,116,34,'#383A3EAA',18)
text('聊天输入提示','说点什么…',69,625,100,23,12,'#C7CFCE')
rect('购物袋',17,620,32,34,'#EA3062',4);text('购物袋数量','100',18,630,30,21,12,'#FFFFFF',align=2)
for x in [197,204,211]:oval('更多操作点',x,636,4,4,'#FFFFFF')
path('礼物图标/外形',[(246,629),(257,624),(267,629),(267,644),(257,649),(246,644)],fill='#F0AC54',closed=True)
path('分享箭头',[(296,632),(307,624),(307,630),(318,638),(306,647),(307,640),(293,647)],fill='#FFFFFF',closed=True)
text('点赞数量','1306',341,643,36,18,10,'#FFFFFF',align=2)
group('03 · 奖励弹窗遮罩')
rect('全屏半透明遮罩',0,0,390,671,'#10252A99')
group('04 · 奖励插画/原生可编辑矢量')
oval('插画/轨道光环',96,95,201,71,None,'#C7FFFC',7)
oval('插画/轨道内环',111,102,170,57,None,'#FFFFFF99',2)
path('插画/左薄荷叶',[(110,150),(77,141),(64,123),(98,131)],fill='#11C9B9',closed=True)
path('插画/右薄荷叶',[(272,148),(309,126),(322,143),(290,155)],fill='#0BCBBE',closed=True)
rect('插画/手机外壳',153,77,61,87,'#53DDD6',9,stroke='#B0FFF4',weight=3)
rect('插画/手机屏幕',160,89,47,65,'#EEFFFB',5)
rect('插画/手机听筒',174,81,17,3,'#29ADA6',2)
oval('插画/手机校验圆',171,107,30,30,'#20CBBB')
path('插画/手机勾号',[(179,121),(184,126),(194,115)],stroke='#FFFFFF',weight=4)
path('插画/黄色奖励券',[(205,130),(237,101),(252,114),(223,147)],fill='#FFE597',stroke='#FFF6CE',weight=2,closed=True)
for x,y,s in [(90,120,6),(242,96,4),(143,87,4),(309,141,5)]:star(x,y,s)
oval('插画/上方光点',201,71,4,4,'#FFF7C9')
group('05 · 奖励弹窗卡片')
shadow(rect('奖励卡片',40,144,312,385,gradient=grad('#E5FFFB','#FFFFFF'),r=18),24,'35',0,8)
path('恭喜你/标题飘带',[(102,137),(289,137),(281,164),(270,174),(121,174),(110,166)],fill=TEAL,closed=True)
text('恭喜你/标题','恭喜你',133,140,125,30,21,'#FFFFFF',True,2)
text('答题结果/答对','答对',138,204,51,30,22,'#15BDB5',True)
text('答题结果/数量','30',189,198,44,39,31,'#15BDB5',True)
text('答题结果/单位','题',233,205,27,28,21,'#15BDB5',True)
text('红包金额前缀','获得红包',122,251,75,24,16,'#303C40')
text('红包金额','¥1.00',197,251,56,24,17,'#252C2F',True)
text('红包金额单位','元',256,251,28,24,16,'#303C40')
group('06 · 红包奖品/原生可编辑矢量')
oval('红包/外层柔光',126,293,138,138,'#FFF2BD66')
oval('红包/内层柔光',131,298,128,128,'#FFE49AAA')
oval('红包/金币底',137,303,116,116,gradient=grad('#FFEFB7','#FFC96C'))
for x,y,s in [(139,328,4),(248,366,5),(154,397,3)]:star(x,y,s,'#FFF7DB')
shadow(rect('红包/主体',151,319,90,101,gradient=grad('#FFB05C','#F0442E'),r=8,stroke='#F5C877',weight=3),10,'15',1,4)
path('红包/封口翻盖',[(153,322),(238,322),(238,350),(195,364),(153,350)],fill='#FF8650',stroke='#FFDE91',weight=2,closed=True)
path('红包/封口金线',[(153,350),(195,364),(238,350)],stroke='#FFE7A5',weight=2.5)
oval('红包/封口金扣',186,355,19,19,'#FFE399',stroke='#FFF4CB',weight=2)
group('07 · 奖励弹窗操作区')
rect('获奖详情按钮',92,408,208,52,gradient=grad('#0CCBD0','#01D7A7'),r=27)
text('获奖详情按钮文字','获奖详情',124,420,144,27,16,'#FFFFFF',True,2)
text('查看答案链接','查看答案',145,478,100,25,15,'#19B6B1',True,2)
close_icon(196,558,15)
group('08 · 底部浏览器导航')
rect('浏览器导航底',0,671,390,85,'#F9FEFF')
for x,reverse in [(137,False),(253,True)]:
    pts=[(x+6,691),(x,697),(x+6,703)] if not reverse else [(x-6,691),(x,697),(x-6,703)]
    path('浏览器/后退' if not reverse else '浏览器/前进',pts,stroke='#303D42',weight=2.4)
    path('浏览器/箭杆',[(x-2,697),(x+11,697)] if not reverse else [(x-11,697),(x+2,697)],stroke='#303D42',weight=2.4)
rect('系统Home指示条',126,738,139,6,'#151D20',3)

# Presentation artboard: independent native copies, clipped to phone screens.
board=base('artboard','03 · 双手机展示排版',0,870,1239,1152);board['layers']=[]
board['backgroundColor']=color('#EDF3FF');board['hasBackgroundColor']=True
board['includeBackgroundColorInExport']=True
presentation=board;page['layers'].append(board)
group('01 · 展示画布',w=1239,h=1152)
rect('浅蓝展示背景',0,0,1239,1152,gradient=grad('#EAF2FF','#F1F5FF'))
def independent_copy(n):
    n=clone(n)
    def reid(v):
        if isinstance(v,dict):
            if 'do_objectID' in v:v['do_objectID']=uid()
            for value in v.values():reid(value)
        elif isinstance(v,list):
            for value in v:reid(value)
    reid(n);return n
for label,src,x,y in [('直播答题',left,174,77),('红包奖励',right,667,300)]:
    group('手机外壳/'+label,w=1239,h=1152)
    shadow(rect('手机/外层圆角机身',x-19,y-19,428,794,'#F7FBFF',58,stroke='#FFFFFF',weight=1.5),42,'30',11,19)
    rect('手机/内层描边',x-7,y-7,404,770,'#EFF8FF',47,stroke='#FFFFFF',weight=2)
    screen=base('group','屏幕内容/'+label,x,y,390,756);screen['layers']=[];board['layers'].append(screen)
    current=screen
    clip=rect('屏幕圆角蒙版',0,0,390,756,'#FFFFFF',40);clip['hasClippingMask']=True
    screen['layers'].extend(independent_copy(n) for n in src['layers'])

document['do_objectID']=uid();document['currentPageIndex']=0
document['pages']=[{'_class':'MSJSONFileReference','_ref_class':'MSImmutablePage','_ref':'pages/'+page['do_objectID']}]
document['layerTextStyles']['objects']=list(styles['text'].values())
document['layerStyles']['objects']=[];document['sharedSwatches']['objects']=[]
document['fontReferences']=[];document['assets']['colors']=[];document['assets']['colorAssets']=[];document['assets']['images']=[]
meta['pagesAndArtboards']={page['do_objectID']:{'name':page['name'],'artboards':{b['do_objectID']:{'name':b['name']} for b in page['layers']}}}
output=HERE/'直播答题与红包奖励.sketch'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in [('document.json',document),('meta.json',meta),('user.json',{'document':{'pageListHeight':100,'pageListCollapsed':0}}),('pages/'+page['do_objectID']+'.json',page)]:
        z.writestr(name,json.dumps(data,ensure_ascii=False,separators=(',',':')))
print(output)
print('Native layers:',{k:sum(n['_class']==k for n in walk(page)) for k in ['artboard','group','text','rectangle','oval','shapePath','bitmap']})
