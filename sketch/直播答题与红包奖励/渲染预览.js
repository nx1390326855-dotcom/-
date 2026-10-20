const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
(async()=>{
  const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
  const reports=[];
  try {
    const artboards=JSON.parse(fs.readFileSync(path.join(__dirname,'文字检查数据.json'),'utf8'));
    for(const [name,artboard] of Object.entries(artboards)) {
      const page=await browser.newPage({viewport:{width:artboard.width,height:artboard.height},deviceScaleFactor:name==='双手机展示'?1:2});
      await page.setContent(fs.readFileSync(path.join(__dirname,name+'.html'),'utf8'),{waitUntil:'load'});
      await page.evaluate(()=>document.fonts.ready);
      const overflow=await page.evaluate(items=>{
        const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');
        return items.map(item=>{ctx.font=`${item.bold?700:400} ${item.size}px "Noto Sans CJK SC"`;return {...item,measured:ctx.measureText(item.text).width};}).filter(item=>item.measured>item.width+.5);
      },artboard.texts);
      if(overflow.length)throw new Error(JSON.stringify({name,overflow}));
      await page.screenshot({path:path.join(__dirname,name+'.png'),fullPage:true});
      reports.push({name,textLayersChecked:artboard.texts.length,textWidthOverflow:0});
      await page.close();
    }
  } finally {await browser.close();}
  fs.writeFileSync(path.join(__dirname,'排版检查结果.json'),JSON.stringify(reports,null,2)+'\n');
  console.log(JSON.stringify(reports,null,2));
})().catch(error=>{console.error(error);process.exit(1)});
