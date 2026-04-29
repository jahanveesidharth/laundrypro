import os, shutil, glob

src_dir = r"C:\Users\lappify\.gemini\antigravity\brain\6eef0708-128a-4f57-8e55-f21dadecf097"
dest_dir = r"C:\laundry-system\frontend\static\garments"
os.makedirs(dest_dir, exist_ok=True)

for file in glob.glob(os.path.join(src_dir, "garment_*.png")):
    filename = os.path.basename(file)
    # filename is like garment_shirt_1777468948967.png
    parts = filename.split('_')
    if len(parts) >= 3:
        clean_name = f"garment_{parts[1]}.png"
        shutil.copy(file, os.path.join(dest_dir, clean_name))
        print(f"Copied {filename} -> {clean_name}")
