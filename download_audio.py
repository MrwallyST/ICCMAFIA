import json
import requests
import os

# Load cookies from notebooklm-mcp-cli profile
cookie_path = r'C:\Users\cesar\.notebooklm-mcp-cli\profiles\default\cookies.json'
with open(cookie_path, 'r') as f:
    raw_cookies = json.load(f)

# Build a requests session with all cookies
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Referer': 'https://notebooklm.google.com/',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
})

for c in raw_cookies:
    domain = c.get('domain', '').lstrip('.')
    session.cookies.set(c['name'], c['value'], domain=domain, path=c.get('path', '/'))

# Print key cookies found
key_names = ['SID', 'SSID', 'APISID', 'SAPISID', '__Secure-1PSID', '__Secure-3PSID', 'HSID', '__Secure-1PSIDTS']
for c in raw_cookies:
    if c['name'] in key_names:
        print(f"Cookie {c['name']}: {c['value'][:25]}... (domain: {c['domain']})")

# The audio URL from the fresh studio status
audio_url = "https://lh3.googleusercontent.com/notebooklm/AKXwDQEAx0HcbiMOLaDp9JL92axtjRPQPSwqULkAKFGx81XCZ1lDHz8c5VEd0NKEOY-NFr0p21aHRhUBihwxEabwVmd5JTloJv2G3wX4YKdceiEOKtRsX5xBRKVD4czAhE8e6q4TojXWVUKVHK23vH5IlD8du_8YZW4=m140-dv"

print(f"\nDownloading from: {audio_url[:80]}...")
r = session.get(audio_url, stream=True, timeout=120)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type', 'unknown')}")
print(f"Content-Length: {r.headers.get('Content-Length', 'unknown')}")

out_path = r"C:\Users\cesar\Documents\New folder\TradesBySci\studios\day-11\day11_en.mp3"
content_type = r.headers.get('Content-Type', '')

if r.status_code == 200 and 'html' not in content_type:
    with open(out_path, 'wb') as f:
        total = 0
        for chunk in r.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                total += len(chunk)
    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"SUCCESS: Downloaded {size_mb:.2f} MB to {out_path}")
else:
    print("FAILED - Got HTML/error response")
    print("First 500 chars of response:", r.text[:500])
