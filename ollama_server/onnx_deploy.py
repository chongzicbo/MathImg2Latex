import os
import sys

sys.path.append(os.path.dirname(".."))
import onnxruntime as ort
import numpy as np
from PIL import Image
from nougat_latex.util import process_raw_latex_code
from nougat_latex import NougatLaTexProcessor
from transformers.models.nougat import NougatTokenizerFast
from loguru import logger

# 设置环境变量
sys.path.append(os.path.dirname(".."))
os.environ["XDG_CACHE_HOME"] = "/data/bocheng/.cache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/data/bocheng/.cache/huggingface/hub/"


# 加载 ONNX 模型
onnx_path = "/data/bocheng/dev/mywork/MathImg2Latex/mymodel/mathocr_new.onnx"
ort_session = ort.InferenceSession(onnx_path)


# 加载分词器和处理器
def load_tokenizer_processor():
    tokenizer = NougatTokenizerFast.from_pretrained("Norm/nougat-latex-base")
    latex_processor = NougatLaTexProcessor.from_pretrained("Norm/nougat-latex-base")
    return tokenizer, latex_processor


# 加载分词器和处理器
tokenizer, latex_processor = load_tokenizer_processor()


# 使用 ONNX 模型进行预测
def predict_one_onnx(img_path: str) -> str:
    image = Image.open(img_path)
    if not image.mode == "RGB":
        image = image.convert("RGB")
    pixel_values = latex_processor(image, return_tensors="np").pixel_values
    task_prompt = tokenizer.bos_token
    print(pixel_values.shape)
    decoder_input_ids = tokenizer(
        task_prompt, add_special_tokens=False, return_tensors="np"
    ).input_ids
    # 初始化生成的 token IDs
    generated_ids = []

    # 循环生成 token，直到遇到 eos_token
    while True:
        # 运行 ONNX 模型
        inputs = {
            "input": pixel_values,
            "decoder_input_ids": decoder_input_ids,
        }
        outputs = ort_session.run(None, inputs)

        # 处理输出
        output = outputs[0]  # 假设第一个输出是生成的 token IDs
        output = output[:, -1, :]
        # output = np.squeeze(output, axis=1)  # 去除多余的维度
        next_token_id = np.argmax(output, axis=-1)  # 获取概率最高的 token

        # 将生成的 token 添加到 generated_ids
        generated_ids.append(next_token_id)

        # 更新 decoder_input_ids
        decoder_input_ids = np.concatenate(
            [decoder_input_ids, next_token_id[:, None]], axis=-1
        )

        # 检查是否遇到 eos_token
        if (
            next_token_id == tokenizer.eos_token_id
            or next_token_id == tokenizer.pad_token_id
            or len(generated_ids) == 100
        ):
            break

    # 将生成的 token IDs 解码为文本
    generated_ids = np.array(generated_ids).T
    generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    sequence = generated_text[0]
    sequence = (
        sequence.replace(tokenizer.eos_token, "")
        .replace(tokenizer.pad_token, "")
        .replace(tokenizer.bos_token, "")
    )
    sequence = process_raw_latex_code(sequence)
    logger.info("nougat predicted sequence:{}".format(sequence))
    return sequence


# 测试预测
img_path = "/data/bocheng/data/MathOCR/nougat_latex/test/0000051.png"
print(predict_one_onnx(img_path=img_path))
