import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel
from transformers.models.nougat import NougatTokenizerFast
from nougat_latex.util import process_raw_latex_code
from nougat_latex import NougatLaTexProcessor
from loguru import logger

# 设置环境变量
os.environ["XDG_CACHE_HOME"] = "/data/bocheng/.cache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/data/bocheng/.cache/huggingface/hub/"

# 预训练模型名称或路径
pretrained_model_name_or_path = "Norm/nougat-latex-base"
device = "cpu"


def load_checkpoint(checkpoint_path, model, strict=True, **kwargs):
    if os.path.exists(checkpoint_path) and os.path.isfile(checkpoint_path):
        state_dict = torch.load(checkpoint_path, map_location=torch.device("cpu"))
        if "model_state_dict" in state_dict:
            model_state_dict = state_dict["model_state_dict"]
        else:
            model_state_dict = state_dict
        model.load_state_dict(model_state_dict, strict=strict)
        logger.info(f"Success load Nougat model: {checkpoint_path}")
    return model


def load_model(checkpoint_path) -> VisionEncoderDecoderModel:
    model = VisionEncoderDecoderModel.from_pretrained(pretrained_model_name_or_path)
    model = load_checkpoint(checkpoint_path, model)
    model.to(device)
    return model


def load_tokenizer_processor():
    tokenizer = NougatTokenizerFast.from_pretrained(pretrained_model_name_or_path)
    latex_processor = NougatLaTexProcessor.from_pretrained(
        pretrained_model_name_or_path
    )
    return tokenizer, latex_processor


# 检查点路径
checkpoint_path = "/data/bocheng/pretrained_model/mathocr/nougat-base_epoch17_step108000_lr8.861961e-07_avg_loss0.00397_token_acc0.84964_edit_dis0.02927.pth"
model = load_model(checkpoint_path)
model.eval()
tokenizer, latex_processor = load_tokenizer_processor()

# 创建一个 dummy input
img_path = "/data/bocheng/data/MathOCR/nougat_latex/test/0000051.png"
# print(predict_one_onnx(img_path=img_path))
image = Image.open(img_path)
if not image.mode == "RGB":
    image = image.convert("RGB")
dummy_input = latex_processor(
    image, return_tensors="pt"
).pixel_values  # 假设输入图像大小为 224x560
print("dummy_input shape:", dummy_input.shape)
task_prompt = tokenizer.bos_token
decoder_input_ids = tokenizer(
    task_prompt, add_special_tokens=False, return_tensors="pt"
).input_ids
print(decoder_input_ids.shape)

import openvino as ov

inputs = {
    "pixel_values": dummy_input,
    "decoder_input_ids": decoder_input_ids,
}
# ov_model = ov.convert_model(model, example_input=(dummy_input, decoder_input_ids))
# torch.jit.trace(model, (dummy_input, decoder_input_ids))
torch.jit.script(model)
