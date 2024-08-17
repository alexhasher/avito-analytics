from flask import Flask, render_template, request, session, redirect, url_for
from sql import top10_offer, concurents, concurents_today, top10_offer_today, all_offer
from matplotlib import pyplot as plt
from werkzeug.security import generate_password_hash, check_password_hash
from config import user, password, host, db_name
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import pymysql
import secrets
from user_login import UserLogin
from FDataBase import FDataBase

import os
from flask_mail import Mail, Message
import jwt
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv('APP_NAME')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT  = os.getenv('MAIL_PORT')
MAIL_USERNAME  = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD  = os.getenv('MAIL_PASSWORD')
SUBJECT = os.getenv('SUBJECT')
CONFIRMATION_URI = os.getenv('CONFIRMATION_URI')



secret = secrets.token_urlsafe(32)
wurl = 'https://www.avito.ru/ufa/gotoviy_biznes'

df = concurents()
fig = plt.figure(figsize=(10, 7))
plt.pie(df['views_all'], labels=df['category'])
plt.savefig('./static/images/plot_all.png')

df = concurents_today()
fig = plt.figure(figsize=(10, 7))
plt.pie(df['views_today'], labels=df['category'])
plt.savefig('./static/images/plot_today.png')

app = Flask(__name__)
app.secret_key = secret
login_manager = LoginManager(app)


# configuration of mail
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = (APP_NAME, MAIL_USERNAME)
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

#Initialize Mail extension
mail = Mail()
mail.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    print("Загрузка данных пользователя")
    return UserLogin().fromDB(user_id)
login_manager.login_view = 'login'

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        getuser = FDataBase(host, user, password, db_name)
        user1 = getuser.getUserByEmail(email=request.form['email'])
        if user1 and check_password_hash(user1['password'], request.form['psw']):
            userlogin = UserLogin().create(user1)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            print("пользователь авторизован")
            return redirect(request.args.get("next") or url_for("profile"))
        else:
            print("Неверная пара логин/пароль", "error")
    return render_template("login.html", title="Авторизация")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    print("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return f"""<a href="{url_for('logout')}">Выйти из профиля</a>
                user info: {current_user.get_id()}"""


@app.route("/index")
@app.route("/")
def index():
    return render_template('base.html', name='Количество просмотров по категориям', url1='./static/images/plot_all.png',
                           url2='./static/images/plot_today.png', wurl=wurl, tables=[top10_offer().to_html(classes='data')],
                           titles=top10_offer().columns.values, tables32=[top10_offer_today().to_html(classes='data')],
                           titles32=top10_offer_today().columns.values, tables1=[concurents().to_html(classes='data')],
                           titles1=concurents().columns.values, tables2=[concurents_today().to_html(classes='data')],
                           titles2=concurents_today().columns.values)

@app.route("/table")
@login_required
def table():
    return render_template('table.html', wurl=wurl, titles3=all_offer().columns.values, tables3=[all_offer().to_html(classes='data')])

@app.route("/verify-email/<token>")
def verify_email(token):
    data = jwt.decode(token, secret, algorithms=["HS256"])
    try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Успешное соединение с", db_name)
        try:
            with connection.cursor() as cursor:
                insert_query = "INSERT INTO `users` (user, email, password) VALUES (%s, %s, %s);"
                cursor.execute(insert_query, (data['name'], data['email_address'], data['hash']))
                connection.commit()
                insert_query = (
                    f"CREATE TABLE {data['name']}_data (url VARCHAR(100) PRIMARY KEY, category VARCHAR(32), title VARCHAR(90), description VARCHAR(2000), price INT(11), phone INT(11), views_all INT(11), views_today INT(11), publish_date DATE, status TINYINT(1));")
                cursor.execute(insert_query)
                connection.commit()
                print("Пользователь создн")
                return redirect(url_for("profile"))

        finally:
            connection.close()
    except Exception as ex:
        print(ex)
        print("Не удалось установить соединение с", db_name, 'или создать пользователя ', data['name'])


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        getuser = FDataBase(host, user, password, db_name)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2'] and (getuser.getUserByEmail(email=request.form['email']) == False):
            token = jwt.encode(
                {
                    "email_address": request.form['email'],
                    "hash": generate_password_hash(request.form['psw']),
                    "name": request.form['name']
                }, secret, "HS256"
            )
            # print(token)
            msg = Message(
                # sender="Avito-analytics",
                subject="Завершение регистрации avito-analytics",
                html=render_template("email/verify.html", token=token, name=request.form['name']),
                recipients=[request.form['email']]
            )
            print(msg)
            mail.send(msg)
            print("Токен отправлен")
            return render_template("finish_registration.html", email=request.form['email'])
    return render_template("register.html", title="Регистрация")

if __name__ == "__main__":
    app.run(debug=True)