import os, json, requests
from bs4 import BeautifulSoup
from datetime import datetime
from blue_shell_main import app, db
from blue_shell_main.models import Daily, Product

@app.template_global()
def short_title(title):
    for i in range(len(title)):
        if title[i] == " ":
            if len(title[:i]) > 45 and len(title[:i]) < 60:
                return title[:i]
            elif len(title[:i]) > 60:
                return f"{title[:57]}..."
    return title

@app.template_global()
def saving(curr, prev):
    if curr == prev:
        return 0

    curr = int(curr)
    return (int(((prev-curr)/prev) * 100))

@app.template_global()
def short_url(asin):
    short_url = f"https://www.amazon.com/dp/{asin}/"
    return short_url

# Inject current date in Jinja
@app.context_processor
def today_date():
    return {'today_date': datetime.now().strftime("%b %-d, %Y")}

# Inject current time in Jinja
@app.context_processor
def current_time():
    return {'current_time': datetime.now().strftime("%b %-d, %Y %I:%M %p %Z")}

# Inject timezone in Jinja
@app.context_processor
def timezone():
    return {'timezone': datetime.now().astimezone().tzinfo}

# Convert string number into floating numbers with 2 decimal places.
def dollar(numstr):
    # Get rid of $ sign
    if '$' in numstr:
        numstr = numstr[1:]

    # Get rid of any commas
    if ',' in numstr:
        numstr = numstr.replace(',', '')

    # Convert to float and round to 2 decimal
    num = round(float(numstr), 2)
    return num

def price_update(url):
    headers = {
        "Accept-Language": 'en-US,en;q=0.5',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    price_now = dollar(soup.find(name='span', class_='a-offscreen').getText()[1:])
    return price_now

def generate_graph_data(product, price_now):
    # To pick out data for bar graph
    if product.amazon_high:
        if price_now > dollar(product.amazon_avg):
            amazon_data = [dollar(product.amazon_low), dollar(product.amazon_avg), price_now, dollar(product.amazon_high)]
            amazon_dates = [product.amazon_low_date, "Average", 'Today', product.amazon_high_date]
            a_bg_color = ['#006AFF', '#006AFF', '#FF9500', '#006AFF']
        else:
            amazon_data = [dollar(product.amazon_low), price_now, dollar(product.amazon_avg), dollar(product.amazon_high)]
            amazon_dates = [product.amazon_low_date, "Today", 'Average', product.amazon_high_date]
            a_bg_color = ['#006AFF', '#FF9500', '#006AFF', '#006AFF']
    else:
        amazon_data = None
        amazon_dates = None
        a_bg_color = None

    if product.third_high:
        if price_now > dollar(product.third_avg):
            third_data = [dollar(product.third_low), dollar(product.third_avg), price_now, dollar(product.third_high)]
            third_dates = [product.third_low_date, "Average", 'Today', product.third_high_date]
            t_bg_color = ['#006AFF', '#006AFF', '#FF9500', '#006AFF']
        else:
            third_data = [dollar(product.third_low), price_now, dollar(product.third_avg), dollar(product.third_high)]
            third_dates = [product.third_low_date, "Today", 'Average', product.third_high_date]
            t_bg_color = ['#006AFF', '#FF9500', '#006AFF', '#006AFF']
    else:
        third_data = None
        third_dates = None
        t_bg_color = None

    return (amazon_data, amazon_dates, a_bg_color, third_data, third_dates, t_bg_color)

def generate_deal_tag(price_now, amazon_low, third_low):
    lowest_deal = False
    great_deal = False

    if amazon_low and third_low:
        amazon_low_price = dollar(amazon_low)
        third_low_price = dollar(third_low)
        if amazon_low_price <= third_low_price:
            if saving(amazon_low_price, price_now) <= 0:
                lowest_deal = True
            elif saving(amazon_low_price, price_now) <= 10:
                great_deal = True
        else:
            if saving(third_low_price, price_now) <= 0:
                lowest_deal = True
            elif saving(third_low_price, price_now) <= 10:
                great_deal = True
    elif amazon_low:
        amazon_low_price = dollar(amazon_low)
        if saving(amazon_low_price, price_now) <= 0:
            lowest_deal = True
        elif saving(amazon_low_price, price_now) <= 10:
            great_deal = True
    elif third_low:
        third_low_price = dollar(third_low)
        if saving(third_low_price, price_now) <= 0:
            lowest_deal = True
        elif saving(third_low_price, price_now) <= 10:
            great_deal = True

    return (lowest_deal, great_deal)

def lightning_deal_tag(url):
    headers = {
        "Accept-Language": 'en-US,en;q=0.5',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    lightning = False
    if soup.find(name='span', class_="a-size-base gb-accordion-active"):
        lightning = True

    return lightning

def update_low_high(asin, price_now):
    product = Product.query.filter_by(asin=asin).first()
    price_str = f"${price_now}"

    # Update Amazon Data
    if product.amazon_avg:
        if dollar(product.amazon_high) < price_now:
            product.amazon_high = price_str
        elif dollar(product.amazon_low) > price_now:
            product.amazon_low = price_str

    # Update Third Party Data
    if product.third_avg:
        if dollar(product.third_high) < price_now:
            product.third_high = price_str
        elif dollar(product.third_low) > price_now:
            product.third_low = price_str

    db.session.commit()
    return