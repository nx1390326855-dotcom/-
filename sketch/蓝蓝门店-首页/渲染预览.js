/* Requires the environment's Playwright and system Chromium. */
const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
(async()=>{
  const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
  try {
    const page=await browser.newPage({viewport:{width:426,height:924},deviceScaleFactor:2});
    await page.setContent(fs.readFileSync(path.join(__dirname,'设计稿预览.html'),'utf8'),{waitUntil:'load'});
    await page.evaluate(()=>document.fonts.ready);
    const checks=JSON.parse(fs.readFileSync(path.join(__dirname,'文字检查数据.json'),'utf8'));
    const overflow=await page.evaluate(items=>{
      const canvas=document.createElement('canvas'), ctx=canvas.getContext('2d');
      return items.map(item=>{ctx.font=`${item.bold?700:400} ${item.size}px "Noto Sans CJK SC"`;return {...item,measured:ctx.measureText(item.text).width};}).filter(item=>item.measured>item.width+.5);
    },checks);
    const broken=await page.locator('svg image').evaluateAll(images=>images.filter(n=>!n.getAttribute('href').startsWith('data:image/png;base64,')).length);
    if(overflow.length||broken)throw new Error(JSON.stringify({overflow,broken}));
    await page.screenshot({path:path.join(__dirname,'蓝蓝门店-首页.png'),fullPage:true});
    console.log(JSON.stringify({textLayersChecked:checks.length,textWidthOverflow:overflow.length,embeddedPhotoLayers:await page.locator('svg image').count(),preview:'852 × 1848',renderer:'Chromium, reconstructed from actual Sketch layers; not native Sketch export'},null,2));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
