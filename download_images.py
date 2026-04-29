import os
import urllib.request
from duckduckgo_search import DDGS
import time

garments = [
    "Skirt", "Shorts", "Scarf", "Bath Towel", "Pillow Cover",
    "Trackpants", "Undergarment", "Socks", "Hand Towel", "Cap",
    "Hoodie", "Cardigan", "Shawl", "Gloves", "Table Cloth",
    "Nightgown", "Pajamas", "Uniform", "Apron", "Vest"
]

dest_dir = r"C:\laundry-system\frontend\static\garments"
os.makedirs(dest_dir, exist_ok=True)

with DDGS() as ddgs:
    for g in garments:
        filename = f"garment_{g.lower().replace(' ', '')}.png"
        filepath = os.path.join(dest_dir, filename)
        
        print(f"Searching for {g}...")
        try:
            results = list(ddgs.images(
                keywords=f"{g} product photography plain background",
                region="wt-wt",
                safesearch="on",
                max_results=5,
            ))
            
            success = False
            for res in results:
                try:
                    url = res.get("image")
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response, open(filepath, 'wb') as out_file:
                        data = response.read()
                        out_file.write(data)
                    print(f"Saved {filename}")
                    success = True
                    break
                except Exception as e:
                    print(f"  Failed URL {url}: {e}")
                    
            if not success:
                print(f"Could not download any image for {g}")
                
        except Exception as e:
            print(f"Error for {g}: {e}")
            
        time.sleep(1)
