import os

path1 = "/data/bocheng/data/MathOCR/PRINTED_TEX_230k/final_png_formulas.txt"
path2 = "/data/bocheng/data/MathOCR/nougat_latex/math.txt"
formulas1 = [f.strip() for f in open(path1).readlines() if f.strip()]
formulas2 = [f.strip() for f in open(path2).readlines() if f.strip()]
set1 = set([line.strip() for line in formulas1])
# set2 = set([line.strip() for line in fr2.readlines()])
# print(len(set1.intersection(set2)))

train_10k = "/data/bocheng/data/MathOCR/nougat_latex/train"
test_10k = "/data/bocheng/data/MathOCR/nougat_latex/test"
val_10k = "/data/bocheng/data/MathOCR/nougat_latex/val"

train_230k_dir = "/data/bocheng/data/MathOCR/PRINTED_TEX_230k/generated_png_images"
base_num = len(os.listdir(train_230k_dir))
print("base_num:", base_num)
train_10k_path = [
    os.path.join(train_10k, filename) for filename in os.listdir(train_10k)
]
test_10k_path = [os.path.join(test_10k, filename) for filename in os.listdir(test_10k)]
val_10k_path = [os.path.join(val_10k, filename) for filename in os.listdir(val_10k)]
data_path_lists = train_10k_path + test_10k_path + val_10k_path

# print(len(set(data_path_lists)))
i = 0
dic_10k = {}
for img_path in sorted(data_path_lists):
    # print(img_path)
    filename = os.path.basename(img_path)
    index = int(os.path.splitext(filename)[0])
    try:
        formula_text = formulas2[index]
        if not formula_text.strip():
            continue
        if formula_text.strip() in set1:
            # print(formula_text)
            continue
        dic_10k[img_path] = formula_text
    except IndexError:
        continue

print(len(dic_10k))
base_dir = "/data/bocheng/data/MathOCR/PRINTED_TEX_230k"
formulas_path = os.path.join(base_dir, "final_png_formulas.txt")
images_path = os.path.join(base_dir, "corresponding_png_images.txt")
fr2 = open(images_path)
images_list = fr2.readlines()
print("230k:", len(images_list))
dic_230k = {}
for i, image_name in enumerate(images_list):
    if not image_name.strip():
        continue
    # print(os.path.splitext(image_name)[1])
    image_path = os.path.join(base_dir, "generated_png_images", image_name.strip())
    formula_text = formulas1[i]
    if not formula_text.strip():
        continue
    if image_path in dic_230k:
        # print(image_path)
        # print(formula_text)
        continue
    dic_230k[image_path] = formula_text

print("after filter:", len(dic_230k))

dic_230k.update(dic_10k)
print("total data:", len(dic_230k))
import shutil

with open("/data/bocheng/data/MathOCR/230k_10k/math.txt", mode="w") as fw:
    for i, (k, v) in enumerate(dic_230k.items()):
        filename = os.path.basename(k)
        new_image_name = f"{str(i).zfill(7)}{os.path.splitext(filename.strip())[1]}"
        if i % 40 == 1:
            new_image_path = os.path.join(
                "/data/bocheng/data/MathOCR/230k_10k/val", new_image_name
            )
        else:
            new_image_path = os.path.join(
                "/data/bocheng/data/MathOCR/230k_10k/train", new_image_name
            )
        if os.path.exists(k):
            shutil.copy(k.strip(), new_image_path)
            fw.write(v + "\n")
        else:
            print(k)
            print(v)
