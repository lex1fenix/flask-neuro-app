from flask import Flask, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, SubmitField, StringField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

Bootstrap(app)

# ------------------ ФОРМА ------------------
class ImageForm(FlaskForm):
    image = FileField('Загрузите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')
    ])
    cross_type = SelectField('Тип креста', choices=[
        ('vertical', 'Вертикальный'),
        ('horizontal', 'Горизонтальный')
    ])
    cross_color = StringField('Цвет креста (RGB)', default='255,0,0',
                              validators=[DataRequired()])
    submit = SubmitField('Нарисовать крест')

# ------------------ ФУНКЦИЯ ДЛЯ ГИСТОГРАММЫ ------------------
def get_histogram_image(image_path):
    img = Image.open(image_path).convert('RGB')
    colors = ['red', 'green', 'blue']
    plt.figure(figsize=(6, 4))
    for i, color in enumerate(colors):
        hist = img.histogram()[i*256:(i+1)*256]
        plt.plot(hist, color=color, label=color.capitalize())
    plt.legend()
    plt.title('Гистограмма цветов')
    plt.xlabel('Интенсивность')
    plt.ylabel('Количество пикселей')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return plot_url

# ------------------ ГЛАВНАЯ СТРАНИЦА ------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ImageForm()
    original_hist = None
    processed_hist = None
    processed_image_url = None
    
    if form.validate_on_submit():
        # сохраняем загруженный файл
        f = form.image.data
        filename = secure_filename(f.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], 'original_' + filename)
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_' + filename)
        f.save(original_path)
        
        # получаем параметры
        cross_type = form.cross_type.data
        color_str = form.cross_color.data
        try:
            r, g, b = map(int, color_str.split(','))
            cross_color = (r, g, b)
        except:
            cross_color = (255, 0, 0)
        
        # рисуем крест
        img = Image.open(original_path).convert('RGB')
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        if cross_type == 'vertical':
            draw.line([(width//2, 0), (width//2, height)], fill=cross_color, width=5)
        else:
            draw.line([(0, height//2), (width, height//2)], fill=cross_color, width=5)
        
        img.save(processed_path)
        
        # гистограммы
        original_hist = get_histogram_image(original_path)
        processed_hist = get_histogram_image(processed_path)
        processed_image_url = url_for('static', filename=f'uploads/processed_{filename}')
        
        return render_template('index.html', form=form,
                               original_hist=original_hist,
                               processed_hist=processed_hist,
                               processed_image=processed_image_url)
    
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
