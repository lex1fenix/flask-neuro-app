print("Starting Flask app...")

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import net as neuronet

app = Flask(__name__)

# Секретный ключ (нужен для форм, можно любой)
SECRET_KEY = 'my_super_secret_key_123'
app.config['SECRET_KEY'] = SECRET_KEY

Bootstrap(app)

# ------------------ ФОРМА (без капчи) ------------------
class NetForm(FlaskForm):
    openid = StringField('Ваш ID', validators=[DataRequired()])
    upload = FileField('Загрузите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только картинки!')
    ])
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

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
