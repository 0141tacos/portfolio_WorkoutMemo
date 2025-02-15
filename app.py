from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
import os
import calendar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workout.db'
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)

with app.app_context():
    db.drop_all()
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

class Workoutmemo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Integer, nullable=False)
    menu = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(100))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 最初の画面を出力するためのルーティング
@app.route('/', methods=['GET', 'POST'])
def workoutcalendar():
    # 現在の年と月を取得
    now = datetime.now()
    year = now.year
    month = now.month
    str_month = str(month).zfill(2)
    print(str_month)
    # カレンダーを作成
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)
    return render_template('calendar.html', year=year, month=month, str_month=str_month, month_days=month_days)

# 登録済の筋トレメニュー一覧を表示するためのルーティング
@app.route('/<string:workday>/index', methods=['GET', 'POST'])
def index(workday):
    memos = Workoutmemo.query.all()
    if len(workday) == 7:
        workday = workday[0:4] + "-" + workday[4:6] + "-0" + workday[-1] 
        return redirect(f'/{ workday }/index')
    elif len(workday) == 8:
        workday = workday[0:4] + "-" + workday[4:6] + "-" + workday[6:8] 
        return redirect(f'/{ workday }/index')
    else:
        print(workday)
        print(memos[1].date)
        return render_template('index.html', workday=workday, memos=memos)

# 実施した筋トレメニューをメモするためのルーティング
@app.route('/create', methods=['GET', 'POST'])
def  create():
    if request.method == 'POST':
        # リクエストメソッドがPOSTの時に画面に入力されていた情報を取得
        date = request.form.get('date')
        print(date)
        menu = request.form.get('menu')
        weight = request.form.get('weight')
        reps = request.form.get('reps')
        sets = request.form.get('sets')
        note = request.form.get('note')
        # DBに追加するためにDBの形式に合わせて変数を設定
        workoutmemo = Workoutmemo(date=date, menu=menu, weight=weight, reps=reps, sets=sets, note=note)
        # DBに追加、反映
        db.session.add(workoutmemo)
        db.session.commit()
        return redirect(url_for('index', workday=date))
    else:
        return render_template('create.html')