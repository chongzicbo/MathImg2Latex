# -*- coding:utf-8 -*-
# create: @time: 10/8/23 11:47
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


def parse_option():
    parser = argparse.ArgumentParser(
        prog="nougat inference config", description="model archiver"
    )
    parser.add_argument(
        "--pretrained_model_name_or_path", default="Norm/nougat-latex-base"
    )
    # parser.add_argument(
    #     "--img_path",
    #     default="/data/bocheng/data/MathOCR/test/test01.jpg",
    #     help="path to latex image segment",
    #     # required=True,
    # )
    parser.add_argument(
        "--img_dir",
        default="/data/bocheng/data/MathOCR/test/",
        help="img dir for testing",
    )
    parser.add_argument("--device", default="cpu")
    return parser.parse_args()


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


def run_nougat_latex():
    args = parse_option()
    # device
    if args.device == "gpu":
        device = torch.device("cuda:0")
    else:
        device = torch.device("cpu")

    # init model
    model = VisionEncoderDecoderModel.from_pretrained(
        args.pretrained_model_name_or_path
    )
    model = load_model(
        "/data/bocheng/data/logs/im2latex_170k/nougat-base_epoch17_step108000_lr8.861961e-07_avg_loss0.00397_token_acc0.84964_edit_dis0.02927.pth",
        model,
    )
    model.to(device)
    # init processor
    tokenizer = NougatTokenizerFast.from_pretrained(args.pretrained_model_name_or_path)
    latex_processor = NougatLaTexProcessor.from_pretrained(
        args.pretrained_model_name_or_path
    )

    # run test
    # image = Image.open(args.img_path)
    img_dir = args.img_dir
    with open(
        "/data/bocheng/code/source_code/MathOCR/output/nougat_latex_base_test_230k_100k_170k.txt",
        mode="w",
    ) as fw:
        fw.write("\\begin{array}\n")
        if os.path.exists(img_dir):
            img_list = sorted(os.listdir(img_dir))
            for img_name in img_list:
                img_path = os.path.join(img_dir, img_name)
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
                print("\\\\" + img_name + "\\hspace{1cm}" + sequence + "\n", file=fw)
            print("\\end{array}", file=fw)


if __name__ == "__main__":
    run_nougat_latex()
