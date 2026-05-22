import os
import shutil
import sqlite3
import json
import base64
import win32crypt
import win32file
import win32con
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_encryption_key():
    local_state_path = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Local State"
    )
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # Remove DPAPI prefix
    encrypted_key = encrypted_key[5:]
    # Decrypt key
    decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return decrypted_key

def decrypt_value(encrypted_value, key):
    try:
        # Check signature
        if encrypted_value[:3] == b'v10' or encrypted_value[:3] == b'v11':
            iv = encrypted_value[3:15]
            ciphertext = encrypted_value[15:]
            aesgcm = AESGCM(key)
            decrypted = aesgcm.decrypt(iv, ciphertext, None)
            return decrypted.decode('utf-8')
    except Exception as e:
        pass
    return ""

def copy_locked_file(src, dst):
    try:
        handle = win32file.CreateFile(
            src,
            win32file.GENERIC_READ,
            win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_DELETE,
            None,
            win32file.OPEN_EXISTING,
            win32file.FILE_ATTRIBUTE_NORMAL,
            None
        )
        
        dst_handle = win32file.CreateFile(
            dst,
            win32file.GENERIC_WRITE,
            0,
            None,
            win32file.CREATE_ALWAYS,
            win32file.FILE_ATTRIBUTE_NORMAL,
            None
        )
        
        block_size = 64 * 1024
        while True:
            err, data = win32file.ReadFile(handle, block_size)
            if not data:
                break
            win32file.WriteFile(dst_handle, data)
            
        win32file.CloseHandle(handle)
        win32file.CloseHandle(dst_handle)
        return True
    except Exception as e:
        print(f"Failed to copy locked file {src} to {dst}: {e}")
        return False

def get_cookies_for_profile(profile_path, key):
    cookie_db = os.path.join(profile_path, "Network", "Cookies")
    if not os.path.exists(cookie_db):
        return []
    
    temp_db = "temp_cookies.db"
    if not copy_locked_file(cookie_db, temp_db):
        return []
    
    cookies = []
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cookies'")
        if not cursor.fetchone():
            return []
        
        cursor.execute("""
            SELECT host_key, name, path, expires_utc, is_secure, is_httponly, encrypted_value, samesite
            FROM cookies
            WHERE host_key LIKE '%google.com' OR host_key LIKE '%youtube.com'
        """)
        
        for host_key, name, path, expires_utc, is_secure, is_httponly, encrypted_value, samesite in cursor.fetchall():
            decrypted = decrypt_value(encrypted_value, key)
            if not decrypted:
                continue
            
            expires = 0
            if expires_utc > 0:
                expires = (expires_utc / 1000000) - 11644473600
                if expires < 0:
                    expires = 0
            
            samesite_str = "Lax"
            if samesite == -1: samesite_str = "None"
            elif samesite == 0: samesite_str = "None"
            elif samesite == 1: samesite_str = "Lax"
            elif samesite == 2: samesite_str = "Strict"
            
            cookie = {
                "name": name,
                "value": decrypted,
                "domain": host_key,
                "path": path,
                "expires": expires,
                "httpOnly": bool(is_httponly),
                "secure": bool(is_secure),
                "sameSite": samesite_str
            }
            cookies.append(cookie)
            
        conn.close()
    except Exception as e:
        print(f"Error reading sqlite database: {e}")
    finally:
        if os.path.exists(temp_db):
            try:
                os.remove(temp_db)
            except:
                pass
            
    return cookies

def main():
    try:
        key = get_encryption_key()
        user_data_dir = os.path.join(
            os.environ["USERPROFILE"],
            "AppData", "Local", "Google", "Chrome", "User Data"
        )
        
        all_cookies = []
        profiles = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Profile 5"]
        
        for name in os.listdir(user_data_dir):
            if name.startswith("Profile ") and name not in profiles:
                profiles.append(name)
                
        for profile in profiles:
            profile_path = os.path.join(user_data_dir, profile)
            if os.path.exists(profile_path):
                cookies = get_cookies_for_profile(profile_path, key)
                if cookies:
                    print(f"Found {len(cookies)} cookies in profile: {profile}")
                    has_notebooklm = any("notebooklm" in c["domain"] for c in cookies)
                    if has_notebooklm:
                        print(f"Profile {profile} contains notebooklm cookies. Using it.")
                        all_cookies = cookies
                        break
                    elif not all_cookies:
                        all_cookies = cookies
        
        if not all_cookies:
            print("No google cookies found.")
            return
            
        storage_state_path = os.path.join(
            os.environ["USERPROFILE"],
            ".notebooklm", "storage_state.json"
        )
        os.makedirs(os.path.dirname(storage_state_path), exist_ok=True)
        
        state = {
            "cookies": all_cookies,
            "origins": [
                {
                    "origin": "https://notebooklm.google.com",
                    "localStorage": [
                        {
                            "name": "bcsp",
                            "value": "system"
                        }
                    ]
                }
            ]
        }
        
        with open(storage_state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            
        print(f"Successfully updated storage_state.json at {storage_state_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
