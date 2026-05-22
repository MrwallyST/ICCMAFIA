import json

def find_lockups(data):
    lockups = []
    
    def recurse(node):
        if isinstance(node, dict):
            if "lockupViewModel" in node:
                lockups.append(node["lockupViewModel"])
            for k, v in node.items():
                recurse(v)
        elif isinstance(node, list):
            for item in node:
                recurse(item)
                
    recurse(data)
    return lockups

def main():
    try:
        with open('yt_channel.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        lockups = find_lockups(data)
        print(f"Total lockupViewModels found: {len(lockups)}")
        
        for idx, lockup in enumerate(lockups[:20], 1):
            # Let's inspect the keys and find videoId and title
            print(f"\nLockup {idx}:")
            print(f"  Keys: {list(lockup.keys())}")
            
            # Look for videoId inside overlays or commands
            # We saw: lockupViewModel -> contentImage -> thumbnailViewModel -> overlays -> ... -> addToPlaylistCommand -> videoId
            # Or lockupViewModel -> onTap -> innertubeCommand -> watchEndpoint -> videoId
            # Let's write a helper to extract videoId recursively from this lockup
            vids = []
            def find_vid(n):
                if isinstance(n, dict):
                    if "videoId" in n:
                        vids.append(n["videoId"])
                    for k, v in n.items():
                        find_vid(v)
                elif isinstance(n, list):
                    for item in n:
                        find_vid(item)
            find_vid(lockup)
            vid = list(dict.fromkeys(vids))[0] if vids else "unknown"
            
            # Let's extract title
            # Look for title in metadata
            title = "unknown"
            if "metadata" in lockup:
                m = lockup["metadata"]
                if isinstance(m, dict) and "lockupMetadataViewModel" in m:
                    lm = m["lockupMetadataViewModel"]
                    if "title" in lm:
                        t = lm["title"]
                        if isinstance(t, dict) and "content" in t:
                            title = t["content"]
                            
            print(f"  Video ID: {vid}")
            print(f"  Title: {title}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
