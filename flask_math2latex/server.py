import os, sys

sys.path.append("..")
print(sys.path)
os.environ["XDG_CACHE_HOME"] = "/data/bocheng/data/.cache"
os.environ["HUGGINGFACE_HUB_CACHE"] = "/data/bocheng/data/.cache/huggingface/hub/"
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel
from transformers.models.nougat import NougatTokenizerFast
from nougat_latex.util import process_raw_latex_code
from nougat_latex import NougatLaTexProcessor
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import random

app = Flask(__name__)
access_token = "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"

device = torch.device("cpu")
model_path = "chongzicbo/MathImg2Latex"
# model_path = "facebook/nougat-base"
tokenizer = NougatTokenizerFast.from_pretrained(model_path, token=access_token)
latex_processor = NougatLaTexProcessor.from_pretrained(model_path, token=access_token)
model = VisionEncoderDecoderModel.from_pretrained(model_path, token=access_token)
# model = load_model(
#     "/data/bocheng/data/logs/nougat_latex/nougat-base_epoch18_step214000_lr1.833212e-07_avg_loss0.00551_token_acc0.71300_edit_dis0.03889.pth",
#     model,
# )
model.to(device)
# img_path = "/data/bocheng/code/source_code/MathOCR/MathImg2Latex/examples/test_data/test86_screenshot_bigger.jpg"


# 假设 image2latex 函数定义如下
def image2latex(image_path):
    # 用你的模型处理图片并返回latex代码
    # 这里只是一个占位符
    image = Image.open(image_path)
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
    return sequence


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def handle_upload():
    if "image" in request.files:
        image = request.files["image"]
        filename = secure_filename(image.filename)
        filename = "".join(random.sample("zyxwvutsrqponmlkjihgfedcba", 10)) + filename
        image_path = os.path.join("/data/bocheng/data/test/images", filename)
        image.save(image_path)

        # 调用 image2latex 函数处理图片
        latex_code = image2latex(image_path)

        # 向前端返回图片 URL（假设已经设置了 static 文件夹) 和 latex 代码
        return jsonify(
            {
                "message": "Image uploaded and processed successfully!",
                "image_url": "/images/" + filename,
                "latex_code": latex_code,
            }
        )
    return jsonify({"error": "No Image Provided!"}), 400


@app.route("/images/<filename>")
def uploaded_file(filename):
    return send_from_directory("/data/bocheng/data/test/images", filename)


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8502, debug=True)
