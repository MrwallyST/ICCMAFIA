import puppeteer from 'puppeteer-core';
import fs from 'fs';

(async () => {
  console.log('Launching Chrome with your profile...');
  try {
    const browser = await puppeteer.launch({
      executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      userDataDir: 'C:\\Users\\cesar\\AppData\\Local\\Google\\Chrome\\User Data',
      headless: "new"
    });
    
    const page = await browser.newPage();
    console.log('Navigating to NotebookLM...');
    await page.goto('https://notebooklm.google.com/', { waitUntil: 'networkidle2' });
    
    const cookies = await page.cookies();
    let cookieObj = {};
    for (let c of cookies) {
      cookieObj[c.name] = c.value;
    }
    
    const html = await page.content();
    let csrf = '';
    const match = html.match(/\["SNlM0e","([^"]+)"/);
    if (match) {
      csrf = match[1];
      console.log('Found CSRF token!');
    } else {
      console.log('Warning: Could not find CSRF token. Are you logged in?');
    }
    
    const authData = {
      cookies: cookieObj,
      csrf_token: csrf,
      session_id: '',
      extracted_at: Date.now() / 1000
    };
    
    fs.writeFileSync('C:\\Users\\cesar\\.notebooklm-mcp\\auth.json', JSON.stringify(authData, null, 2));
    console.log('Successfully updated NotebookLM auth.json with real Chrome profile data!');
    
    await browser.close();
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
})();
