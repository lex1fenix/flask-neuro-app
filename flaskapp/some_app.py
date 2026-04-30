print("Starting Flask app...")

from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import base64
from io import BytesIO
from PIL import Image
import json
import net as neuronet

app = Flask(__name__)

# Секретный ключ (можно свой)
SECRET_KEY = 'my_super_secret_key_123'
app.config['SECRET_KEY'] = SECRET_KEY

# 🔐 КЛЮЧИ КАПЧИ (получите на https://www.google.com/recaptcha)
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = 'ВАШ_SITE_KEY'
app.config['RECAPTCHA_PRIVATE_KEY'] = 'ВАШ_SECRET_KEY'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

Bootstrap(app)

# ------------------ ФОРМА ------------------
class NetForm(FlaskForm):
    openid = StringField('Ваш ID', validators=[DataRequired()])
    upload = FileField('Загрузите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только картинки!')
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Распознать')

# ------------------ ГЛАВНАЯ СТРАНИЦА ------------------
@app.route("/")
def hello():
    return "<html><body><h1>Нейросетевой классификатор</h1><a href='/net'>Перейти к загрузке</a></body></html>"

# ------------------ СТРАНИЦА С ФОРМОЙ ------------------
@app.route("/net", methods=['GET', 'POST'])
def net():
    form = NetForm()
    filename = None
    neurodic = {}

    if form.validate_on_submit():
        # сохраняем файл
        f = form.upload.data
        filename_secure = secure_filename(f.filename)
        filename = os.path.join('static', filename_secure)
        f.save(filename)

        # классифицируем
        _, images = neuronet.read_image_files(1, 'static', filename_secure)
        decode = neuronet.getresult(images)
        for elem in decode:
            neurodic[elem[0][1]] = float(elem[0][2])

        return render_template('net.html', form=form, image_name=filename, neurodic=neurodic)

    return render_template('net.html', form=form, image_name=None, neurodic={})

# ------------------ JSON API ДЛЯ КЛАССИФИКАЦИИ ------------------
@app.route("/apinet", methods=["POST"])
def apinet():
    if request.mimetype == 'application/json':
        data = request.get_json()
        filebytes = data['imagebin'].encode('utf-8')
        img_data = base64.b64decode(filebytes)
        img = Image.open(BytesIO(img_data))
        decode = neuronet.getresult([img])
        result = {}
        for elem in decode:
            result[elem[0][1]] = float(elem[0][2])
        return jsonify(result)
    return jsonify({"error": "need JSON"}), 400

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
