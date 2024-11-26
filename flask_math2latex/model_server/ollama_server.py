from PIL import Image
from transformers import TrOCRProcessor
from optimum.onnxruntime import ORTModelForVision2Seq
from flask import Flask, request, jsonify
import os
from config.config import logger

app = Flask(__name__)

# Load the model and processor
processor = TrOCRProcessor.from_pretrained("breezedeus/pix2text-mfr")
model = ORTModelForVision2Seq.from_pretrained(
    "breezedeus/pix2text-mfr", use_cache=False
)
logger.info("Successfully loaded pix2text model!")


def predict_one(img_path: str):
    images = [Image.open(img_path).convert("RGB")]
    pixel_values = processor(images=images, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)
    logger.info(f"pix2text predicted sequence: {generated_text[0]}")
    return generated_text[0]


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files["image"]
    image_path = "temp_image.png"
    image.save(image_path)

    try:
        result = predict_one(image_path)
        os.remove(image_path)
        return jsonify({"result": result})
    except Exception as e:
        os.remove(image_path)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
