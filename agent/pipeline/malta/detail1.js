const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const fs=require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox'], proxy:{server: process.env.HTTPS_PROXY} });
  const p = await b.newPage();
  p.on('response', async r => { if (/api/i.test(r.url())) console.log('API', r.status(), r.url()); });
  await p.goto('https://mgalicenseeregister.mga.org.mt', { waitUntil: 'networkidle', timeout: 90000 });
  await p.getByText('View All').first().click();
  await p.waitForTimeout(8000);
  await p.getByText('711 Malta Limited').first().click();
  await p.waitForTimeout(6000);
  console.log('URL', p.url());
  console.log((await p.innerText('body')).slice(0,3000));
  await b.close();
})();
