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
from config.config import logger

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
        logger.info("success load nougat model:{}".format(checkpoint_path))
    return model


def load_model(checkpoint_path) -> VisionEncoderDecoderModel:
    model = VisionEncoderDecoderModel.from_pretrained(pretrained_model_name_or_path)
    model = load_checkpoint(
        checkpoint_path,
        model,
    )
    model.to(device)
    return model


def load_tokenizer_processor():
    tokenizer = NougatTokenizerFast.from_pretrained(pretrained_model_name_or_path)
    latex_processor = NougatLaTexProcessor.from_pretrained(
        pretrained_model_name_or_path
    )
    return tokenizer, latex_processor


checkpoint_path = "/data/bocheng/data/logs/im2latex_170k/nougat-base_epoch17_step108000_lr8.861961e-07_avg_loss0.00397_token_acc0.84964_edit_dis0.02927.pth"
model = load_model(checkpoint_path)
tokenizer, latex_processor = load_tokenizer_processor()


def predict_one(
    img_path: str,
) -> str:
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
    logger.info("nougat predicted sequence:{}".format(sequence))
    return sequence


if __name__ == "__main__":
    checkpoint_path = "/data/bocheng/data/logs/im2latex_170k/nougat-base_epoch17_step108000_lr8.861961e-07_avg_loss0.00397_token_acc0.84964_edit_dis0.02927.pth"
    img_path = "/data/bocheng/data/MathOCR/test/agriculture-2549214-01.png"
    model = load_model(checkpoint_path)
    tokenizer, latex_processor = load_tokenizer_processor()
    sequence = predict_one(img_path, tokenizer, latex_processor, model)
    print(sequence)
