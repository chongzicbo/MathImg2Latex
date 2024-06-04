from flask import Flask, request, render_template, send_from_directory, url_for
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL
from config.config import logger
from config.config import MysqlConfig
from model_server.nougat_server import predict_one as nougat_predict_one
from model_server.pix2text_server import predict_one as pix2text_predict_one

app = Flask(__name__)

# 配置MySQL数据库连接
app.config.from_object(MysqlConfig)
mysql = MySQL(app)


@app.route("/save_result", methods=["POST"])
def save_result():
    data = request.get_json()
    formula = data.get("formula")
    image_path = data.get("image_path")

    # 连接数据库并执行SQL查询
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO math_image_foumula(formula, image_path) VALUES (%s, %s)",
        (formula, image_path),
    )
    mysql.connection.commit()
    cur.close()
    logger.info(f"image: {image_path},formula: {formula} saved to database")
    return jsonify({"message": "Result saved successfully!"}), 200


# 假设的模拟方法，你需要替换为实际的模型调用方法
def extract_mathematic_formula_pix2text(img_path):
    # 这里应该是调用模型的代码，返回LaTeX公式
    sequence = pix2text_predict_one(img_path)
    return sequence


def extract_mathematic_formula_nougat(img_path):
    # 这里应该是调用模型的代码，返回LaTeX公式
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
    app.run(host="0.0.0.0", port=8504, debug=True)
