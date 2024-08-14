from flask import Flask, render_template, request, session
from sql import top10_offer, concurents, concurents_today, top10_offer_today, all_offer
from matplotlib import pyplot as plt
# from requests import request, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import user, password, host, db_name
import pymysql
import secrets

secret = secrets.token_urlsafe(32)


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
wurl = 'https://www.avito.ru/ufa/gotoviy_biznes'
@app.route("/")
def index():



    return render_template('base.html', name='Количество просмотров по категориям', url1='./static/images/plot_all.png',
                           url2='./static/images/plot_today.png', wurl=wurl, tables=[top10_offer().to_html(classes='data')],
                           titles=top10_offer().columns.values, tables32=[top10_offer_today().to_html(classes='data')],
                           titles32=top10_offer_today().columns.values, tables1=[concurents().to_html(classes='data')],
                           titles1=concurents().columns.values, tables2=[concurents_today().to_html(classes='data')],
                           titles2=concurents_today().columns.values)

@app.route("/table")
def table():
    return render_template('table.html', wurl=wurl, titles3=all_offer().columns.values, tables3=[all_offer().to_html(classes='data')])

@app.route("/login")
def login():
    return render_template("login.html", title="Авторизация")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            # Занесение данных в базу SQL
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
                        cursor.execute(insert_query, (request.form['name'], request.form['email'], hash))
                        connection.commit()

                        insert_query =(f"CREATE TABLE {request.form['name']}_data (url VARCHAR(100) PRIMARY KEY, category VARCHAR(32), title VARCHAR(90), description VARCHAR(2000), price INT(11), phone INT(11), views_all INT(11), views_today INT(11), publish_date DATE, status TINYINT(1));")
                        cursor.execute(insert_query)
                        connection.commit()

                finally:
                    connection.close()
            except Exception as ex:
                print(ex)
                print("Не удалось установить соединение с", db_name, 'или создать пользователя ', request.form['name'])
    return render_template("register.html", title="Регистрация")


if __name__ == "__main__":
    app.run(debug=True)