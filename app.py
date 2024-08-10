from flask import Flask, render_template
from sql import top10_offer, concurents
from matplotlib import pyplot as plt

df = concurents()
fig = plt.figure(figsize=(10, 7))
plt.pie(df['views_all'], labels=df['category'])
plt.savefig('./static/images/plot.png')

app = Flask(__name__)
wurl = 'https://www.avito.ru/ufa/gotoviy_biznes'
@app.route("/")
def index():



    return render_template('base.html', name='Количество просмотров по категориям', url='./static/images/plot.png',
                           wurl=wurl, tables=[top10_offer().to_html(classes='data')],
                           titles=top10_offer().columns.values, tables1=[concurents().to_html(classes='data')],
                           titles1=concurents().columns.values)


if __name__ == "__main__":
    app.run(debug=True)

# from flask import Flask, request, render_template, session, redirect
# import numpy as np
# import pandas as pd
# app = Flask(__name__)
# df = pd.DataFrame({'A': [0, 1, 2, 3, 4],
#                    'B': [5, 6, 7, 8, 9],
#                    'C': ['a', 'b', 'c--', 'd', 'e']})
# @app.route('/', methods=("POST", "GET"))
# def html_table():
#     return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
# if __name__ == '__main__':
#     app.run(host='0.0.0.0')







# from matplotlib import pyplot as plt
#
# cars = ['AUDI', 'BMW', 'FORD',
#         'TESLA', 'JAGUAR', 'MERCEDES']
# data = [23, 17, 35, 29, 12, 41]
# fig = plt.figure(figsize=(10, 7))
# plt.pie(data, labels=cars)
# plt.savefig('./static/images/plot.png')

