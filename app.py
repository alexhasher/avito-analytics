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

import time
from parser import pages_list_parse, next_page, page_parse

load_dotenv()

APP_NAME = os.getenv('APP_NAME')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT  = os.getenv('MAIL_PORT')
MAIL_USERNAME  = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD  = os.getenv('MAIL_PASSWORD')
SUBJECT = os.getenv('SUBJECT')
CONFIRMATION_URI = os.getenv('CONFIRMATION_URI')

secret = secrets.token_urlsafe(32)




app = Flask(__name__)
app.secret_key = secret
login_manager = LoginManager(app)





app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = (APP_NAME, MAIL_USERNAME)
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail()
mail.init_app(app)


menu = ["index", "profile", "analytics", "table", "login", "logout", "register"]



@login_manager.user_loader
def load_user(user_id):
    print("Загрузка данных пользователя")
    return UserLogin().fromDB(user_id)



login_manager.login_view = 'login'

# wurl = current_user.get_url()

#'https://www.avito.ru/ufa/gotoviy_biznes'

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
    return render_template("login.html", title="Авторизация", menu=menu)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    print("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", user=current_user, menu=menu)


@app.route("/")
def index():
    return render_template('index.html', user=current_user, menu=menu)


@app.route("/analytics")
@login_required
def analytics():
    dbase_name = current_user.get_name() + '_data'
    df = concurents(dbase_name)
    fig = plt.figure(figsize=(10, 7))
    plt.pie(df['views_all'], labels=df['category'])
    plt.savefig('./static/images/plot_all.png')

    df = concurents_today(dbase_name)
    fig = plt.figure(figsize=(10, 7))
    plt.pie(df['views_today'], labels=df['category'])
    plt.savefig('./static/images/plot_today.png')

    return render_template('analytics.html', name='Количество просмотров по категориям',
                           url1='./static/images/plot_all.png',
                           url2='./static/images/plot_today.png',
                           wurl=current_user.get_url(),

                           table1=concurents(dbase_name).to_html(classes='table',
                                                      border=0,
                                                      index=False,
                                                      na_rep='-',
                                                      justify='left',
                                                      columns=(concurents(dbase_name).columns[0],
                                                               concurents(dbase_name).columns[1],
                                                               concurents(dbase_name).columns[2],),),
                           table2=concurents_today(dbase_name).to_html(classes='table',
                                                       border=0,
                                                       index=False,
                                                       na_rep='-',
                                                       justify='left',
                                                       columns=(concurents_today(dbase_name).columns[0],
                                                                concurents_today(dbase_name).columns[1],
                                                                concurents_today(dbase_name).columns[2],),),
                           table3=top10_offer(dbase_name).to_html(classes='table',
                                                             border=0,
                                                             index=False,
                                                             na_rep='-',
                                                             justify='left',
                                                             columns=(top10_offer(dbase_name).columns[0],
                                                                      top10_offer(dbase_name).columns[1],
                                                                      top10_offer(dbase_name).columns[2],
                                                                      top10_offer(dbase_name).columns[4],
                                                                      top10_offer(dbase_name).columns[6],
                                                                      top10_offer(dbase_name).columns[7],
                                                                      top10_offer(dbase_name).columns[8],),),
                           table4=top10_offer_today(dbase_name).to_html(classes='table',
                                                        border=0,
                                                        index=False,
                                                        na_rep='-',
                                                        justify='left',
                                                        columns=(top10_offer_today(dbase_name).columns[0],
                                                                 top10_offer_today(dbase_name).columns[1],
                                                                 top10_offer_today(dbase_name).columns[2],
                                                                 top10_offer_today(dbase_name).columns[4],
                                                                 top10_offer_today(dbase_name).columns[6],
                                                                 top10_offer_today(dbase_name).columns[7],
                                                                 top10_offer_today(dbase_name).columns[8],),),
                           user=current_user, menu=menu)

@app.route("/table")
@login_required
def table():
    dbase_name = current_user.get_name() + '_data'
    return render_template('table.html', wurl=current_user.get_url(),
                           table=all_offer(dbase_name).to_html(classes='table',
                                                       border=0,
                                                       index=False,
                                                       na_rep='-',
                                                       justify='left',),
                           user=current_user, menu=menu)

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

@app.route("/research", methods=["POST"])
def research():

    dbase_name = current_user.get_name() + '_data'
    link_url = current_user.get_url()
    urls_list = []

    if request.method == "POST":
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
                    insert_query = "UPDATE `users` SET link_url = %s WHERE id = %s ;"
                    cursor.execute(insert_query, (request.form['research'], current_user.get_id()))
                    connection.commit()

                    pages_list_parse(link_url, urls_list)
                    u = link_url
                    while next_page(u):
                        time.sleep(60)
                        u = next_page(u)
                        print(u)
                        time.sleep(60)
                        pages_list_parse(u, urls_list)
                        time.sleep(60)

                        print(len(urls_list))

                        for u in urls_list:
                            time.sleep(60)
                            page_parse(u, dbase_name)

                    return redirect(url_for("profile"))

            finally:
                connection.close()
        except Exception as ex:
            print(ex)
            print("Не удалось установить соединение с", db_name)

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
            return render_template("finish_registration.html", email=request.form['email'], user=current_user)
    return render_template("register.html", title="Регистрация", user=current_user, menu=menu)

if __name__ == "__main__":
    app.run(debug=True)