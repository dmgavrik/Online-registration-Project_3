const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const fs=require('fs');
const want=new Set(JSON.parse(fs.readFileSync('mga/licensees.json')).filter(r=>!r[2].includes('/B2B/')).map(r=>r[0]));
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox'], proxy:{server: process.env.HTTPS_PROXY} });
  const p = await b.newPage();
  await p.goto('https://mgalicenseeregister.mga.org.mt', { waitUntil: 'networkidle', timeout: 90000 });
  await p.getByText('View All').first().click();
  await p.waitForTimeout(8000);
  const out=[];
  for (let i=0;i<40;i++){
    const t=await p.innerText('body');
    const names=[...t.matchAll(/Company Name\n(.+?)\n/g)].map(m=>m[1].trim()).filter(n=>want.has(n));
    for (const n of names){ try{ await p.getByText(n,{exact:true}).first().click(); await p.waitForTimeout(1800);}catch(e){console.log('ERR',n)} }
    out.push(await p.innerText('body'));
    const m=t.match(/(\d+) – (\d+) of (\d+)/); console.log(m&&m[0], names.length);
    if (m && +m[2]>=+m[3]) break;
    await p.locator('button[aria-label="Next page"]').click(); await p.waitForTimeout(2500);
  }
  fs.writeFileSync('mga/details.json', JSON.stringify(out));
  await b.close();
})();
