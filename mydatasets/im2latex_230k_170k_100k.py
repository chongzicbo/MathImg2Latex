import os
import shutil
from typing import List


def get_data(base_dir: str):
    train_data_path = os.path.join(base_dir, "train")
    val_data_path = os.path.join(base_dir, "val")
    formula_path = os.path.join(base_dir, "math.txt")
    train_data = [
        os.path.join(train_data_path, im_name)
        for im_name in os.listdir(train_data_path)
    ]
    val_data = [
        os.path.join(val_data_path, im_name) for im_name in os.listdir(val_data_path)
    ]
    formula_texts = [line for line in open(formula_path).readlines() if line.strip()]
    data = train_data + val_data
    return (
        sorted(data, key=lambda p: int(os.path.splitext(os.path.basename(p))[0])),
        formula_texts,
    )


def output_data(output_dir: str, data: list, formulas_texts: List[str]):
    formula_set = set()
    output_train_dir = os.path.join(output_dir, "train")
    output_val_dir = os.path.join(output_dir, "val")
    os.makedirs(output_train_dir, exist_ok=True)
    os.makedirs(output_val_dir, exist_ok=True)
    output_formulas_path = os.path.join(output_dir, "math.txt")
    i = 0
    with open(output_formulas_path, mode="w") as fw:
        for im_path, formula_text in zip(data, formulas_texts):
            im_name = os.path.basename(im_path)
            new_im_name = f"{str(i).zfill(7)}{os.path.splitext(im_name.strip())[1]}"
            if i % 50 == 1:
                out_path = os.path.join(output_val_dir, new_im_name)
            else:
                out_path = os.path.join(output_train_dir, new_im_name)
            shutil.copy(im_path, out_path)
            new_formula = formula_text.strip().replace(" ", "")
            if new_formula not in formula_set:
                formula_set.add(new_formula)
                fw.write(formula_text.strip() + "\n")
                i += 1


if __name__ == "__main__":
    base_dir = "/data/bocheng/data/MathOCR/230k_10k"
    data_230k, formula_texts_230k = get_data(base_dir)

    base_dir = "/data/bocheng/data/MathOCR/im2latex_170k"
    data_170k, formula_texts_170k = get_data(base_dir)

    data = data_230k + data_170k
    formulas_texts = formula_texts_230k + formula_texts_170k
    # print(len(data), len(formulas_texts))
    output_dir = "/data/bocheng/data/MathOCR/im2latex_230k_100k_170k"
    os.makedirs(output_dir, exist_ok=True)
    output_data(output_dir, data, formulas_texts)
