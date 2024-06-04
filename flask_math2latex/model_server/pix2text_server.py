from PIL import Image
from transformers import TrOCRProcessor
from optimum.onnxruntime import ORTModelForVision2Seq
import os
from config.config import logger

processor = TrOCRProcessor.from_pretrained("breezedeus/pix2text-mfr")
model = ORTModelForVision2Seq.from_pretrained(
    "breezedeus/pix2text-mfr", use_cache=False
)
logger.info("success load pix2text model!")


def predict_one(img_path: str):
    images = [Image.open(img_path).convert("RGB")]
    pixel_values = processor(images=images, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)
    logger.info(f"pix2text predicted sequence: {generated_text[0]}")
    return generated_text[0]


if __name__ == "__main__":
    img_path = "/data/bocheng/data/MathOCR/test/agriculture-2549214-01.png"
    print(predict_one(img_path=img_path))
