import os, sys

sys.path.append(os.path.dirname(".."))
os.environ["XDG_CACHE_HOME"] = "/data/bocheng/.cache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/data/bocheng/.cache/huggingface/hub/"
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel
from transformers.models.nougat import NougatTokenizerFast
from nougat_latex.util import process_raw_latex_code
from nougat_latex import NougatLaTexProcessor
from loguru import logger

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


checkpoint_path = "/data/bocheng/pretrained_model/mathocr/nougat-base_epoch17_step108000_lr8.861961e-07_avg_loss0.00397_token_acc0.84964_edit_dis0.02927.pth"
model = load_model(checkpoint_path)
tokenizer, latex_processor = load_tokenizer_processor()

if __name__ == "__main__":
    # model.save_pretrained("./mymodel", safe_serialization=True)
    tokenizer.save_pretrained("./mymodel")
    latex_processor.save_pretrained("./mymodel")
