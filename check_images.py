from PIL import Image
import os

# 👉 Change this to your actual prepared dataset path
root_dir = r"C:\Users\Misriya A A\OneDrive\Desktop\Skinsense\dataset\prepared"

bad_images = []

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                img_path = os.path.join(root, file)
                Image.open(img_path).verify()  # check if readable
            except Exception as e:
                print(f"❌ Bad image: {img_path} ({e})")
                bad_images.append(img_path)

print(f"\n🔍 Scan complete. Found {len(bad_images)} bad images.")
