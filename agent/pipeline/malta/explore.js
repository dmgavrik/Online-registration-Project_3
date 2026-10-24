const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const fs=require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox'], proxy:{server: process.env.HTTPS_PROXY} });
  const p = await b.newPage();
  await p.goto('https://mgalicenseeregister.mga.org.mt', { waitUntil: 'networkidle', timeout: 90000 });
  fs.writeFileSync('mga/home.txt', await p.innerText('body'));
  await p.getByText('View All').first().click();
  await p.waitForTimeout(10000);
  fs.writeFileSync('mga/all.txt', await p.innerText('body'));
  fs.writeFileSync('mga/all.html', await p.content());
  await b.close();
})();
