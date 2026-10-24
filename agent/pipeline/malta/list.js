const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const fs=require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox'], proxy:{server: process.env.HTTPS_PROXY} });
  const p = await b.newPage();
  await p.goto('https://mgalicenseeregister.mga.org.mt', { waitUntil: 'networkidle', timeout: 90000 });
  await p.getByText('View All').first().click();
  await p.waitForTimeout(8000);
  const pages=[];
  for (let i=0;i<40;i++){
    const t=await p.innerText('body'); pages.push(t);
    const m=t.match(/(\d+) – (\d+) of (\d+)/); console.log(m&&m[0]);
    if (m && +m[2]>=+m[3]) break;
    const nb=p.locator('button[aria-label="Next page"]');
    await nb.click(); await p.waitForTimeout(2500);
  }
  fs.writeFileSync('mga/pages.json', JSON.stringify(pages));
  await b.close();
})();
