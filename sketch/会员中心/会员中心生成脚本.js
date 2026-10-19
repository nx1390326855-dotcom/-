/* 青禾 · 微信小程序会员中心 | 375 × 812
 * Official Sketch API plugin entry: onRun(context)
 * Node CLI: node 会员中心生成脚本.js --scene-json /path/to/scene.json
 * This script creates native Text, ShapePath and Group layers, not page images.
 */
const C={bg:'#F5F7F3',white:'#FFFFFF',ink:'#25382D',muted:'#7D8B80',green:'#2B7350',deep:'#204C38',soft:'#EAF2E7',line:'#E8EDE5',light:'#C6D8C3',sand:'#DDE7D3'};
const scene={name:'会员中心',width:375,height:812,nodes:[]};
function group(name,x,y,w,h){const g={type:'group',name,x,y,w,h,children:[]};scene.nodes.push(g);return g.children}
function rect(a,name,x,y,w,h,fill,r=0,border=null){a.push({type:'rect',name,x,y,w,h,fill,r,border})}
function oval(a,name,x,y,w,h,fill,border=null){a.push({type:'oval',name,x,y,w,h,fill,border})}
function text(a,name,value,x,y,w,h,size=12,color=C.ink,bold=false,align='left'){a.push({type:'text',name,text:value,x,y,w,h,size,color,bold,align})}
function path(a,name,x,y,w,h,d,color=C.green,stroke=1.5,fill=null){const parts=d.match(/M[^M]+/g)||[d];if(parts.length>1){a.push({type:'group',name,x,y,w,h,children:parts.map((part,i)=>({type:'path',name:name+'/'+(i+1),x:0,y:0,w,h,d:part,color,stroke,fill}))})}else a.push({type:'path',name,x,y,w,h,d,color,stroke,fill})}
function icon(a,type,x,y,size=22,color=C.green){
 const g={type:'group',name:'图标/'+type,x,y,w:size,h:size,children:[]};a.push(g);const b=g.children;const k=size/24;const P=(n,d)=>path(b,n,0,0,size,size,d,color,1.45*k);const O=(n,x,y,w,h)=>oval(b,n,x*k,y*k,w*k,h*k,null,{color,width:1.45*k});
 if(type==='钱包'){P('钱包轮廓','M4 6 L18 6 C19.1 6 20 6.9 20 8 L20 18 C20 19.1 19.1 20 18 20 L5 20 C3.9 20 3 19.1 3 18 L3 5 C3 3.9 3.9 3 5 3 L17 3');P('卡包','M20 10 L14 10 C12 10 12 15 14 15 L20 15');oval(b,'扣点',14.2*k,11.7*k,1.5*k,1.5*k,color)}
 else if(type==='包裹'){P('箱体','M3 7 L12 3 L21 7 L21 18 L12 22 L3 18 Z');P('箱线','M3 7 L12 11 L21 7');P('中缝','M12 11 L12 22');P('封带','M8 5 L17 9 L17 13')}
 else if(type==='物流'){P('车厢','M2 5 L14 5 L14 17 L2 17 Z');P('车头','M14 9 L18 9 L22 13 L22 17 L14 17');O('左车轮',4,15,5,5);O('右车轮',16,15,5,5)}
 else if(type==='售后'||type==='客服'){P('耳机','M4 12 L4 10 C4 5.5 7.5 2 12 2 C16.5 2 20 5.5 20 10 L20 12');P('左耳罩','M4 10 L3 10 C1.7 10 1.7 16 3 16 L5 16 L5 10 Z');P('右耳罩','M19 10 L21 10 C22.3 10 22.3 16 21 16 L19 16 Z');P('话筒','M20 16 L20 18 C20 20 18 21 16 21 L13 21')}
 else if(type==='签到'){P('日历','M5 4 L19 4 C20.1 4 21 4.9 21 6 L21 20 L3 20 L3 6 C3 4.9 3.9 4 5 4 Z');P('日历线','M3 9 L21 9');P('装订左','M7 2 L7 6');P('装订右','M17 2 L17 6');P('对勾','M7 14 L10 17 L17 12')}
 else if(type==='社群'){O('用户一',7,3,8,8);P('用户肩部','M3 21 C3 12 19 12 19 21');P('用户二','M18 4 C23 4 23 11 18 11');P('用户二肩部','M20 14 C22.5 15 23 18 23 21')}
 else if(type==='地址'){P('定位','M19 10 C19 15 12 22 12 22 C12 22 5 15 5 10 C5 0.7 19 0.7 19 10 Z');O('定位中心',9,7,6,6)}
 else if(type==='收藏'){P('爱心','M12 21 C10 19 2 13 2 8 C2 1 10 1 12 6 C14 1 22 1 22 8 C22 13 14 19 12 21 Z')}
 else if(type==='设置'){P('设置外形','M9 3 L15 3 L16 6 L19 7 L22 10 L20 13 L20 16 L17 19 L14 19 L12 22 L9 20 L6 19 L5 16 L2 13 L3 10 L5 7 L8 6 Z');O('齿轮中心',8,8,8,8)}
 else if(type==='首页'){P('房屋','M3 11 L12 3 L21 11 L21 21 L15 21 L15 14 L9 14 L9 21 L3 21 Z')}
 else if(type==='分类'){rect(b,'左上',3*k,3*k,7*k,7*k,null,1.5*k,{color,width:1.45*k});rect(b,'右上',14*k,3*k,7*k,7*k,null,1.5*k,{color,width:1.45*k});rect(b,'左下',3*k,14*k,7*k,7*k,null,1.5*k,{color,width:1.45*k});rect(b,'右下',14*k,14*k,7*k,7*k,null,1.5*k,{color,width:1.45*k})}
 else if(type==='购物车'){P('购物车','M2 3 L5 3 L8 16 L19 16 L22 7 L6 7');O('轮一',8,19,2,2);O('轮二',18,19,2,2)}
 else if(type==='我的'){O('头像',8,3,8,8);P('肩部','M4 22 C4 11 20 11 20 22')}
 else if(type==='权益'){P('菱形','M4 8 L8 3 L16 3 L20 8 L12 20 Z');P('菱形横线','M4 8 L20 8');P('菱形刻线','M8 3 L10 8 L12 20 L14 8 L16 3')}
}
let a=group('00/背景',0,0,375,812);rect(a,'页面底色',0,0,375,812,C.bg);rect(a,'顶部纯白区域',0,0,375,160,C.white);
a=group('01/iOS状态栏',0,0,375,44);text(a,'系统时间','9:41',24,12,50,20,14,C.ink,true);for(let i=0;i<4;i++)rect(a,'信号格'+(i+1),286+i*4,22-i*2,2.6,4+i*2,C.ink,.6);path(a,'Wi-Fi',307,16,17,13,'M2 6 C7 1 17 1 22 6 M6 11 C10 8 14 8 18 11 M11 16 L13 16',C.ink,1.4);rect(a,'电池外框',332,16,23,11,null,3,{color:'#809083',width:.8});rect(a,'电池电量',334,18,18,7,C.ink,1.2);rect(a,'电池正极',356,19,1.6,5,'#809083',.6);
a=group('02/微信小程序导航栏',0,44,375,44);text(a,'页面标题','会员中心',130,11,115,24,16,C.ink,true,'center');rect(a,'微信胶囊',282,7,77,30,C.white,15,{color:C.line,width:1});rect(a,'胶囊分割',324,14,1,16,C.line);[295,301,307].forEach((x,i)=>oval(a,'更多操作点'+i,x,21,2.5,2.5,C.ink));oval(a,'关闭外圈',336,15,14,14,null,{color:C.ink,width:1.3});oval(a,'关闭圆点',341,20,4,4,C.ink);
a=group('03/用户资料',20,100,335,64);oval(a,'头像底色',0,3,54,54,C.soft);oval(a,'头像头部',20,14,15,16,'#8FAE8F');path(a,'头像肩部',10,32,36,22,'M2 22 C2 1 22 1 22 22 Z','#8FAE8F',0,'#8FAE8F');oval(a,'头像叶片底',39,40,17,17,C.white);path(a,'头像叶片',42,43,12,12,'M2 10 C1 3 6 2 10 2 C10 8 8 11 2 10 Z',C.green,1,C.green);text(a,'昵称','林间的风',70,4,204,27,19,C.ink,true);rect(a,'等级标签',70,38,108,22,C.soft,11);text(a,'会员等级','青禾会员 · Lv.3',78,40,97,18,10,C.green);icon(a,'设置',309,20,20,'#718776');
a=group('04/会员权益卡',20,176,335,110);rect(a,'自然绿卡片',0,0,335,110,C.deep,16);text(a,'会员卡标题','青禾会员',16,14,170,26,17,'#F5F8EC',true);text(a,'会员卡描述','每一份日常，都值得被认真对待',16,44,278,18,10,'#D5E3D0');icon(a,'权益',292,17,25,'#D6E6C8');rect(a,'成长进度底',16,74,220,3,'#4C7056',1.5);rect(a,'成长进度',16,74,158,3,'#CBDDB8',1.5);text(a,'成长值','成长值 720 / 1000',16,85,154,16,9,'#D5E3D0');text(a,'查看权益入口','查看权益 ›',250,85,69,16,9,'#E5EEDC',false,'right');
a=group('05/积分与优惠券',20,298,335,68);rect(a,'资产卡片',0,0,335,68,C.white,16);rect(a,'资产分隔线',167,17,1,34,C.line);text(a,'积分数值','1,250',16,7,135,29,23,C.ink,true,'center');text(a,'积分标签','积分余额',16,40,135,17,10,C.muted,false,'center');text(a,'优惠券数值','3',184,7,135,29,23,C.ink,true,'center');text(a,'优惠券标签','优惠券',184,40,135,17,10,C.muted,false,'center');
a=group('06/我的订单',20,378,335,112);rect(a,'订单卡片',0,0,335,112,C.white,16);text(a,'模块标题','我的订单',16,13,130,23,14,C.ink,true);text(a,'全部订单入口','全部订单 ›',230,17,89,17,10,C.muted,false,'right');const orderNames=['待付款','待发货','待收货','售后/退款'],orderIcons=['钱包','包裹','物流','售后'];for(let i=0;i<4;i++){const cx=44+i*82;icon(a,orderIcons[i],cx-11,49,22,C.green);text(a,'订单状态/'+orderNames[i],orderNames[i],cx-38,82,76,17,10,'#5F7264',false,'center')}oval(a,'待付款徽标',54,43,14,14,'#EEF4E9',{color:C.white,width:1.5});text(a,'待付款数量','2',54,42,14,16,8,C.green,true,'center');
a=group('07/每日签到',20,502,161,78);rect(a,'签到卡片',0,0,161,78,'#EAF2E5',16);text(a,'签到标题','每日签到',14,14,102,23,14,C.ink,true);text(a,'签到说明','连续签到，领积分',14,43,115,17,10,'#69836C');icon(a,'签到',124,25,23,C.green);
a=group('08/专属群入口',193,502,162,78);rect(a,'社群卡片',0,0,162,78,C.white,16);text(a,'社群标题','专属会员群',14,14,116,23,14,C.ink,true);text(a,'社群说明','好物福利，不错过',14,43,118,17,10,C.muted);icon(a,'社群',126,25,22,C.green);
a=group('09/常用功能',20,592,335,122);rect(a,'常用功能卡片',0,0,335,122,C.white,16);text(a,'模块标题','常用功能',16,13,180,23,14,C.ink,true);const fnNames=['收货地址','我的收藏','在线客服','设置'],fnIcons=['地址','收藏','客服','设置'];for(let i=0;i<4;i++){const cx=44+i*82;icon(a,fnIcons[i],cx-11,52,22,C.green);text(a,'功能名称/'+fnNames[i],fnNames[i],cx-38,86,76,17,10,'#65786A',false,'center')}
a=group('10/底部导航栏',0,729,375,83);rect(a,'导航栏背景',0,0,375,83,C.white);rect(a,'顶部细分割线',0,0,375,.5,C.line);const nav=['首页','分类','购物车','我的'];for(let i=0;i<4;i++){const cx=46.875+i*93.75;icon(a,nav[i],cx-11,12,22,i===3?C.green:'#8C988D');text(a,'导航名称/'+nav[i],nav[i],cx-36,40,72,17,10,i===3?C.green:'#8C988D',i===3,'center')}rect(a,'iOS Home Indicator',121,69,133,5,'#1D3024',2.5);

function onRun(context){
 const sketch=require('sketch');const dom=require('sketch/dom');const fm=NSFileManager.defaultManager();const fs={existsSync:p=>Boolean(fm.fileExistsAtPath(p)),mkdirSync:p=>{const ok=fm.createDirectoryAtPath_withIntermediateDirectories_attributes_error(p,true,null,null);if(!ok)throw new Error('无法创建目录：'+p)},copyFileSync:(a,b)=>{const ok=fm.copyItemAtPath_toPath_error(a,b,null);if(!ok)throw new Error('无法复制文件：'+b)},writeFileSync:(p,s)=>{const ok=NSString.stringWithString(String(s)).writeToFile_atomically_encoding_error(p,true,NSUTF8StringEncoding,null);if(!ok)throw new Error('无法写入文件：'+p)}};const {Document,Artboard,Group,ShapePath,Text,SharedStyle}=dom;
 const desktop=String(NSHomeDirectory())+'/Desktop/Sketch设计稿';if(!fs.existsSync(desktop))fs.mkdirSync(desktop);
 const output=desktop+'/会员中心.sketch';if(fs.existsSync(output)){const stamp=Date.now();fs.copyFileSync(output,desktop+'/会员中心.备份-'+stamp+'.sketch')}
 const document=new Document();document.selectedPage.name='01 · 会员中心';const board=new Artboard({parent:document.selectedPage,name:'会员中心',frame:{x:0,y:0,width:375,height:812},background:{enabled:true,color:C.bg,includedInExport:true}});
 const sharedText={},sharedLayer={};const created=[];
 function build(n,parent){let layer;const frame={x:n.x,y:n.y,width:n.w,height:n.h};
  if(n.type==='group'){layer=new Group({parent,name:n.name,frame});n.children.forEach(c=>build(c,layer));return layer}
  if(n.type==='text'){layer=new Text({parent,name:n.name,text:n.text,fixedWidth:true,frame,style:{fontFamily:'Source Han Sans CN',fontSize:n.size,fontWeight:n.bold?9:5,textColor:n.color,alignment:n.align,verticalAlignment:'top',lineHeight:n.h}});const key=[n.size,n.bold,n.color,n.align,n.h].join('/');if(!sharedText[key])sharedText[key]=SharedStyle.fromStyle({name:'文字/'+n.size+'/'+(n.bold?'Bold':'Regular')+'/'+n.color+'/'+n.align+'/'+n.h,style:layer.style,document});layer.sharedStyle=sharedText[key]}
  else{
   if(n.type==='path'){
    // ShapePath.fromSVGPath returns an individual native Bezier layer, never a page image.
    layer=ShapePath.fromSVGPath(n.d);const actual=layer.frame;layer.frame={x:n.x+actual.x*n.w/24,y:n.y+actual.y*n.h/24,width:Math.max(actual.width*n.w/24,.01),height:Math.max(actual.height*n.h/24,.01)};layer.parent=parent;layer.name=n.name;
   }else{layer=new ShapePath({parent,name:n.name,shapeType:n.type==='oval'?ShapePath.ShapeType.Oval:ShapePath.ShapeType.Rectangle,frame});if(n.r)layer.points.forEach(p=>{p.cornerRadius=n.r})}
   layer.style={fills:n.fill?[n.fill]:[],borders:n.type==='path'&&n.stroke>0?[{color:n.color,thickness:n.stroke,position:'Center'}]:n.border?[{color:n.border.color,thickness:n.border.width,position:'Inside'}]:[],borderOptions:{lineEnd:'Round',lineJoin:'Round'}};
   const key=JSON.stringify([n.fill,n.color,n.stroke,n.border]);if(!sharedLayer[key])sharedLayer[key]=SharedStyle.fromStyle({name:'图形/'+(n.fill||n.color||n.border?.color||'空'),style:layer.style,document});layer.sharedStyle=sharedLayer[key]
  }created.push(layer);return layer;
 }
 try{scene.nodes.forEach(n=>build(n,board));const violations=[];created.forEach(l=>{if(l.type==='Text'){const f=l.fragments||[];if(f.length>1||f.some(r=>r.rect&&(r.rect.width>l.frame.width+.5||r.rect.height>l.frame.height+.5)))violations.push(l.name)}});if(violations.length)throw new Error('文字溢出检查失败：'+violations.join('、'));
 document.save(output,{saveMode:'SaveAs'},function(error){if(error){fs.writeFileSync(desktop+'/生成失败.txt',String(error));sketch.UI.message('保存失败：'+error);return}
 try{const previewDir=desktop+'/.native-export-'+Date.now();fs.mkdirSync(previewDir);sketch.export(board,{formats:'png',scales:'3',output:previewDir,overwriting:true});const items=fm.contentsOfDirectoryAtPath_error(previewDir,null);let nativePng=null;for(let i=0;i<items.count();i++){const name=String(items.objectAtIndex(i));if(/\.png$/i.test(name))nativePng=previewDir+'/'+name}if(!nativePng)throw new Error('Sketch 没有导出 PNG');const previewPath=desktop+'/会员中心.png';if(fs.existsSync(previewPath)){const ok=fm.moveItemAtPath_toPath_error(previewPath,desktop+'/会员中心.预览备份-'+Date.now()+'.png',null);if(!ok)throw new Error('无法备份已有 PNG')}fs.copyFileSync(nativePng,previewPath);const json=sketch.export(board,{formats:'json',output:false});fs.writeFileSync(desktop+'/原生图层验证.json',JSON.stringify(json,null,2));const info={saved:output,preview:desktop+'/会员中心.png',width:375,height:812,editableTextLayers:created.filter(l=>l.type==='Text').length,nativeNonGroupLayers:created.length,generatedBy:'Sketch official JavaScript API',sketchVersion:sketch.version.sketch,checkedAt:new Date().toISOString(),note:'可编辑原生 Text / ShapePath / Group 图层；PNG 由本机 Sketch 导出。'};fs.writeFileSync(desktop+'/本机验证结果.json',JSON.stringify(info,null,2));sketch.UI.message('已保存至桌面 / Sketch设计稿 / 会员中心.sketch')}catch(e){fs.writeFileSync(desktop+'/导出失败.txt',String(e));sketch.UI.message('文件已保存，预览导出失败：'+e)}})
 }catch(e){fs.writeFileSync(desktop+'/生成失败.txt',String(e.stack||e));throw e}
}
if(typeof module!=='undefined')module.exports={onRun,scene};
if(typeof process!=='undefined'&&process.versions&&process.versions.node&&require.main===module){const fs=require('fs');const i=process.argv.indexOf('--scene-json');if(i>=0){fs.writeFileSync(process.argv[i+1],JSON.stringify(scene,null,2));console.log('Scene exported: '+process.argv[i+1])}else console.log('在 Sketch 插件中调用 onRun，或使用 --scene-json 输出原生设计节点。')}
