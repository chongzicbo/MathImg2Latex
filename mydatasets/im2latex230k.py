import os
import shutil
import imagesize
import cv2
from PIL import Image
from tqdm import tqdm

base_dir = "/data/bocheng/data/MathOCR/PRINTED_TEX_230k"
formulas_path = os.path.join(base_dir, "final_png_formulas.txt")
images_path = os.path.join(base_dir, "corresponding_png_images.txt")

# fr1 = open(formulas_path)
# formulas_list = fr1.readlines()
# print(formulas_list[0:2])
# print(len(formulas_list))
fr2 = open(images_path)
images_list = fr2.readlines()
# print(images_list[:2])
# print(len(images_list))
train_image_dir = os.path.join(base_dir, "train_images")
val_image_dir = os.path.join(base_dir, "val_images")
os.makedirs(train_image_dir, exist_ok=True)
os.makedirs(val_image_dir, exist_ok=True)
for i, image_name in tqdm(enumerate(images_list)):
    if not image_name.strip():
        continue
    # print(os.path.splitext(image_name)[1])
    image_path = os.path.join(base_dir, "generated_png_images", image_name.strip())
    new_image_name = f"{str(i).zfill(7)}{os.path.splitext(image_name.strip())[1]}"

    # width, height = imagesize.get(image_path)
    # new_width = width
    # new_height = height
    # if width < 32:
    #     new_width = 32
    # elif width > 1024:
    #     new_width = 1024
    # if height < 32:
    #     new_height = 32
    # elif height > 512:
    #     new_height = 512
    # if width < 32 or width > 1024 or height < 32 or height > 512:
    #     im = Image.open(image_path)
    #     im = im.resize(size=(new_width, new_height))
    #     im.save(os.path.join(new_image_dir, new_image_name))
    # else:
    if i % 20 == 0:
        shutil.copy(
            image_path,
            os.path.join(val_image_dir, new_image_name),
        )
    else:
        shutil.copy(
            image_path,
            os.path.join(train_image_dir, new_image_name),
        )
