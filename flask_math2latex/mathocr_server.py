from flask import Flask, request, render_template
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify
from config.config import logger
from config.config import images_formulas_saved_dir, Database
from model_server.nougat_server import predict_one as nougat_predict_one
from model_server.pix2text_server import predict_one as pix2text_predict_one
from datetime import datetime

app = Flask(__name__)

db = Database()


@app.route("/save_result", methods=["POST"])
def save_result():
    data = request.get_json()
    formula = data.get("formula")
    image_path = data.get("image_path")
    create_time = datetime.now()

    # 连接数据库并执行SQL查询
    db.execute(
        "INSERT INTO math_image_foumula(formula, image_path,create_time) VALUES (%s, %s,%s)",
        (formula, image_path, create_time),
    )
    logger.info(f"image: {image_path},formula: {formula} saved to database")
    formula_saved_filename = os.path.splitext(os.path.basename(image_path))[0]
    formula_saved_path = os.path.join(
        images_formulas_saved_dir, formula_saved_filename + ".txt"
    )

    with open(formula_saved_path, "w") as fw:
        fw.write(formula)
        logger.info(f"formula had been written into {formula_saved_path}")
    return jsonify({"message": "Result saved successfully!"}), 200


def extract_mathematic_formula_pix2text(img_path):
    sequence = pix2text_predict_one(img_path)
    return sequence


def extract_mathematic_formula_nougat(img_path):
    sequence = nougat_predict_one(img_path)
    return sequence


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/save_image", methods=["POST"])
def save_image():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    # 获取目录信息，如果未提供则使用默认目录
    save_directory = request.form.get("directory")
    save_path = os.path.join(save_directory, filename)
    file.save(save_path)
    logger.info(f"file had been saved to {save_path}")
    return "Image saved", 200


@app.route("/extract", methods=["GET"])
def extract_formula():
    image_path = request.args.get("image_path")
    model = request.args.get("model")

    if model == "pix2text":
        latex_formula = extract_mathematic_formula_pix2text(image_path)
    elif model == "nougat":
        latex_formula = extract_mathematic_formula_nougat(image_path)
    else:
        return "Invalid model", 400

    return latex_formula


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=17800, debug=True)
