from flask import Flask, request, render_template, send_from_directory, url_for
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# 配置MySQL数据库连接
app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "123456"
app.config["MYSQL_DB"] = "test"
app.config["MYSQL_CHARSET"]="utf8mb4"

mysql = MySQL(app)


@app.route("/save_result", methods=["POST"])
def save_result():
    data = request.get_json()
    print(data)
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

    return jsonify({"message": "Result saved successfully!"}), 200


# 假设的模拟方法，你需要替换为实际的模型调用方法
def extract_mathematic_formula_pix2text(img_path):
    # 这里应该是调用模型的代码，返回LaTeX公式
    return "LaTeX formula from pix2text"


def extract_mathematic_formula_nougat(img_path):
    # 这里应该是调用模型的代码，返回LaTeX公式
    return "LaTeX formula from nougat"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/save_image", methods=["POST"])
def save_image():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    save_path = os.path.join("/data/bocheng/data/test/images", filename)
    file.save(save_path)

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
