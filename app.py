from flask import Flask, render_template
from sql import top10_offer, concurents, concurents_today, top10_offer_today, all_offer
from matplotlib import pyplot as plt

df = concurents()
fig = plt.figure(figsize=(10, 7))
plt.pie(df['views_all'], labels=df['category'])
plt.savefig('./static/images/plot_all.png')

df = concurents_today()
fig = plt.figure(figsize=(10, 7))
plt.pie(df['views_today'], labels=df['category'])
plt.savefig('./static/images/plot_today.png')

app = Flask(__name__)
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

if __name__ == "__main__":
    app.run(debug=True)