# Optional idea: limit samples per class
import os, random, shutil

base = "dataset/prepared/train"
target_count = 1000  # per class

for cls in os.listdir(base):
    cls_path = os.path.join(base, cls)
    imgs = os.listdir(cls_path)
    if len(imgs) > target_count:
        remove = random.sample(imgs, len(imgs) - target_count)
        for img in remove:
            os.remove(os.path.join(cls_path, img))
