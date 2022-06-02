import os, psycopg2
import urllib.parse as urlparse
from datetime import datetime
from flask import redirect, render_template, flash, url_for, request
from blue_shell_main import app, db, ENV
from blue_shell_main.forms import UrlForm, AlertForm
from blue_shell_main.models import Track, Daily, Product
from blue_shell_main.tracker import *
from blue_shell_main.utility import *
from blue_shell_main.daily_deals import *

DAY_TO_SEC = 60 * 60 * 24

@app.route('/', methods=["GET", "POST"])
@app.route('/home', methods=["GET", "POST"])
def home():
    form = UrlForm()
    if request.method == 'POST':
        url = form.url.data
        if form.validate_on_submit():
            start = form.url.data.find('/dp/')
            end = form.url.data.find('/', start+4)
            asin = form.url.data[start+4:end]
            return redirect(url_for('product', asin=asin, url=url, price=0))
        elif url == "":
            return redirect(url_for('search', keyword=""))
        else:
            if "https://www.amazon.com/" in url:
                keyword = url[24:50]
            elif "https://smile.amazon.com/" in url:
                keyword = url[31: 67]
            else:
                keyword = url[:26]
            return redirect(url_for('search', keyword=keyword))

    return render_template('home.html', form=form)

@app.route('/about')
def about():
    form = UrlForm()
    return render_template('about.html', title='About', form=form)

@app.route('/daily', methods=['GET', 'POST'])
def daily():
    if Daily.query.all():
        timestamp = Daily.query.get(1).timestamp
        day_after_time = datetime.fromtimestamp(timestamp + DAY_TO_SEC)
        current_datetime = datetime.now()
        start_time = datetime(current_datetime.year, current_datetime.month, current_datetime.day, hour=14) # 14 utc
        end_time = datetime(current_datetime.year, current_datetime.month, current_datetime.day, hour=23) # 23 utc

        if (current_datetime > start_time and current_datetime < end_time) and current_datetime > day_after_time:
            # Delete the current Daily items
            if ENV == 'dev':
                db.session.query(Daily).delete()
                db.session.commit()
            else:
                url = urlparse.urlparse(os.environ['DATABASE_URL_FIXED'])
                dbname = url.path[1:]
                user = url.username
                pw = url.password
                host = url.hostname
                port = url.port

                conn = psycopg2.connect(
                    dbname=dbname,
                    user=user,
                    password=pw,
                    host=host,
                    port=port
                )
                cur = conn.cursor()
                cur.execute('''
                TRUNCATE ONLY daily
                RESTART IDENTITY;
                ''') # DELETE FROM table_name
                conn.commit()
                cur.close()
                conn.close()
            call()
    else:
        call()

    form = UrlForm()

    # This is to paginate the items
    page = request.args.get('page', 1, type=int)
    daily_deals = Daily.query.paginate(page=page, per_page=12)

    return render_template('daily.html', title="Daily Deals", sql_deal=daily_deals, form=form)

@app.route('/product/<string:asin>', methods=['GET', 'POST'])
def product(asin, url="", price="0"):
    alert_form = AlertForm()
    form = UrlForm()

    url = request.args['url']
    lightning = lightning_deal_tag(url)

    if alert_form.validate_on_submit():
        item = Track(email=alert_form.email.data, target_price=float(alert_form.price.data), asin=asin)
        db.session.add(item)
        db.session.commit()
        flash('Tracking Activated', 'success')
        return redirect(url_for('product', asin=asin, url=url, price='0'))

    if bool(Product.query.filter_by(asin=asin).first()):
        product = Product.query.filter_by(asin=asin).first()
        price_now = price_update(product.link)
    else:
        product = fetch_product(url)
        if request.args['price'] != '0':
            price_now = dollar(request.args['price'])
        else:
            price_now = dollar(product.current_price)

    # Compare price_now to lowest price for deal signs
    lowest_deal, great_deal = generate_deal_tag(price_now, product.amazon_low, product.third_low)

    amazon_data, amazon_dates, a_bg_color, third_data, third_dates, t_bg_color = generate_graph_data(product, price_now)

    update_low_high(asin, price_now)

    return render_template('product.html', title='Product', asin=asin, product=product, alert_form=alert_form, form=form, price_now=price_now, amazon_data=amazon_data, amazon_dates=amazon_dates, third_data=third_data, third_dates=third_dates, a_bg_color=a_bg_color, t_bg_color=t_bg_color, is_lightning=lightning, is_great=great_deal, is_lowest=lowest_deal)
    
@app.route('/product/update/<string:asin>', methods=['GET', 'POST'])
def update_product(asin, url=""):
    alert_form = AlertForm()
    form = UrlForm()

    url = request.args['url']

    lightning = lightning_deal_tag(url)

    product = Product.query.filter_by(asin=asin).first()
    product.last_update = 'Just now'

    price_now = price_update(product.link)

    lowest_deal, great_deal = generate_deal_tag(price_now, product.amazon_low, product.third_low)

    amazon_data, amazon_dates, a_bg_color, third_data, third_dates, t_bg_color = generate_graph_data(product, price_now)

    update_low_high(asin, price_now)

    return render_template('product.html', title='Product', asin=asin, product=product, alert_form=alert_form, form=form, price_now=price_now, amazon_data=amazon_data, amazon_dates=amazon_dates, third_data=third_data, third_dates=third_dates, a_bg_color=a_bg_color, t_bg_color=t_bg_color, is_lightning=lightning, is_great=great_deal, is_lowest=lowest_deal)

@app.route('/search/', methods=['GET', 'POST'])
def search():
    form = UrlForm()
    keyword = request.args['keyword']

    url = "https://amazon-products1.p.rapidapi.com/search"

    querystring = {"country":"US", "query":keyword, "page":"1"}

    headers = {
        "X-RapidAPI-Host": "amazon-products1.p.rapidapi.com",
        "X-RapidAPI-Key": os.environ.get("AMAZON_PRODUCT_KEY")
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    data = response.json()
    search_items = data['results']

    """ For Testing Purposes """
    # site_root = os.path.realpath(os.path.dirname(__file__))
    # json_url = os.path.join(site_root, 'static', 'product.json')
    # with open(json_url, 'r') as f:
    #     data = json.load(f)

    # search_items = data['results']

    return render_template('search.html', title="search", form=form, keyword=keyword, data=search_items)

""" Error Pages """

@app.errorhandler(404)
def error_404(error):
    form = UrlForm()
    return render_template('404.html', form=form, title='404'), 404

@app.errorhandler(405)
def error_405(error):
    form = UrlForm()
    return render_template('405.html', form=form, title='405'), 405

@app.errorhandler(500)
def error_500(error):
    form = UrlForm()
    return render_template('500.html', form=form, title='500'), 500