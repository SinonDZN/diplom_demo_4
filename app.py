from flask import Flask, render_template, url_for, request, redirect
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#from flask_admin import Admin, BaseView, AdminIndexView, expose
#from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Goods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.Text)
    name = db.Column(db.String(20), nullable=False)
    info = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.Text, nullable=False)
    shortname = db.Column(db.Text)
    color = db.Column(db.Text)

    def __repr__(self):
        return [self.name, self.id, self.kind, self.info, self.price, self.date, self.image, self.shortname, self.color]

"""
1. on create page make что бы можно было добавлять сколько угодно файлов и это записывалось в бд списком
2. fix text area in index.html if image with bad size
3. bootstrap on /goods/good_type/iphone - 404 not found
"GET /assets/dist/css/bootstrap.min.css HTTP/1.1" 404
"""

@app.route('/')
@app.route('/main')
def index():
    goods = Goods().query.order_by(Goods.price).all()
    return render_template("index.html", data=goods)


@app.route('/katalog')
def katalog():
    return render_template("katalog.html")


@app.route('/info')
def info():
    return render_template("info.html")


@app.route('/cart')
def cart():
    return 'Корзина'


@app.route('/goods/<good_type>/')
def good_similar_type(good_type):
    good = Goods().query.filter_by(kind=good_type).all()
    # other_goods = Goods().query.filter(Goods.shortname.startswith(good.shortname.split('_')[0])).all()  # other colors
    return render_template("good_type.html", data=good)


@app.route('/goods/<good_type>/<shortname>/')
def post(good_type, shortname):
    """
    1. make new cards under main good with same good_type
    """
    good = Goods().query.filter_by(shortname=shortname).first()
    other_goods = Goods().query.filter(Goods.shortname.startswith(good.shortname.split('_')[0])).all() # other colors
    if '[' in good.image:
        img = eval(good.image)
    else:
        img = [good.image]
    return render_template("index_goods.html", dats=good, dats_image=img, other_goods=other_goods)


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        kind = request.form['kind']
        color = request.form['color']
        shortname = request.form['shortname']
        info = request.form['info']
        image = request.files['file']
        image.save(os.path.join('static\\img\\goods', image.filename))

        goods = Goods(name=name, color=color, shortname=shortname, kind=kind, price=price, info=info, image="img/goods/"+str(image.filename))

        try:
            db.session.add(goods)
            db.session.commit()
            return redirect('/')
        except Exception as err:
            print(f"db.create error: {err}")
            return "Ошибка"
    else:
        return render_template("create.html")


# @app.get('/')
# def index():
#     return render_template(index.html)


if __name__ == '__main__':
    app.run(debug=True)
