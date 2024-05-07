import argparse
import os, sys

sys.path.append(os.path.dirname("."))
os.environ["XDG_CACHE_HOME"] = "/data/bocheng/data/.cache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/data/bocheng/data/.cache/huggingface/hub/"
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel
from transformers.models.nougat import NougatTokenizerFast
from nougat_latex.util import process_raw_latex_code
from nougat_latex import NougatLaTexProcessor

os.environ["RUN_ON_GPU_IDs"] = "1"


def load_model(checkpoint_path, model, strict=True, **kwargs):
    if os.path.exists(checkpoint_path) and os.path.isfile(checkpoint_path):
        state_dict = torch.load(checkpoint_path, map_location=torch.device("cpu"))
        if "model_state_dict" in state_dict:
            model_state_dict = state_dict["model_state_dict"]
        else:
            model_state_dict = state_dict
        model.load_state_dict(model_state_dict, strict=strict)
        print("success load model:{}".format(checkpoint_path))
    return model


device = torch.device("cpu")
model_path = "Norm/nougat-latex-base"
# model_path = "facebook/nougat-base"
tokenizer = NougatTokenizerFast.from_pretrained(model_path)
latex_processor = NougatLaTexProcessor.from_pretrained(model_path)
model = VisionEncoderDecoderModel.from_pretrained(model_path)
model = load_model(
    "/data/bocheng/data/logs/nougat_latex/nougat-base_epoch18_step214000_lr1.833212e-07_avg_loss0.00551_token_acc0.71300_edit_dis0.03889.pth",
    model,
)
model.to(device)
img_path = "/data/bocheng/code/source_code/MathOCR/nougat-latex-ocr/examples/test_data/test86_screenshot_bigger.jpg"
image = Image.open(img_path)
if not image.mode == "RGB":
    image = image.convert("RGB")

pixel_values = latex_processor(image, return_tensors="pt").pixel_values
task_prompt = tokenizer.bos_token
decoder_input_ids = tokenizer(
    task_prompt, add_special_tokens=False, return_tensors="pt"
).input_ids
with torch.no_grad():
    outputs = model.generate(
        pixel_values.to(device),
        decoder_input_ids=decoder_input_ids.to(device),
        max_length=model.decoder.config.max_length,
        early_stopping=True,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        use_cache=True,
        num_beams=1,
        bad_words_ids=[[tokenizer.unk_token_id]],
        return_dict_in_generate=True,
    )
sequence = tokenizer.batch_decode(outputs.sequences)[0]
sequence = (
    sequence.replace(tokenizer.eos_token, "")
    .replace(tokenizer.pad_token, "")
    .replace(tokenizer.bos_token, "")
)
sequence = process_raw_latex_code(sequence)
print(sequence)
