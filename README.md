# MathImg2Latex

Translate the image of a mathematical formula into LaTeX code.

The code in this repository comes from [nougat-latex-ocr](https://github.com/NormXU/nougat-latex-ocr), and I just used more open-source data for training based on it.

## Data

img2latex-230K: https://zenodo.org/records/7738969

im2latex-100K: https://zenodo.org/records/56198#.V2px0jXT6eA

[im2latex170k (kaggle.com)](https://www.kaggle.com/datasets/rvente/im2latex170k)

There are over 540,000 filtered image-equation pair.



## Evaluation

1/50, that is, more than 10,000 data were used as the validation set, and the evaluation results are as follows:

| model              | token_acc ↑  | normed edit distance |
| ------------------ | ------------ | -------------------- |
| pix2tex            | 0.5346       | 0.10312              |
| pix2tex*           | 0.60         | 0.10                 |
| nougat-latex-based | **0.623850** | **0.06180**          |
| MathImg2Latex      | 0.7131       | 0.3948               |

## Uses

### fine-tune on your customized dataset

1. Prepare your dataset in [this](https://drive.google.com/drive/folders/13CA4vAmOmD_I_dSbvLp-Lf0s6KiaNfuO) format
2. Change `config/base.yaml`
3. Run the training script

```
python tools/train_experiment.py --config_file config/base.yaml --phase 'train'
```

## 

## Predict

Please refer to examples/predict.py and examples/run_latex_ocr.py.



Thanks to [NormXU/nougat-latex-ocr: Codebase for fine-tuning / evaluating nougat-based image2latex generation models (github.com)](https://github.com/NormXU/nougat-latex-ocr)

## Model
https://huggingface.co/chongzicbo/MathImg2Latex


