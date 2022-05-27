import requests, time
from blue_shell_main import db
from blue_shell_main.models import Daily

# There is time restriction on these, 7-8 AM gets the majority of the daily offers
# 10am gets the newer offers
# 4pm is the last one

# Add the daily deals to database
def call():
    db.create_all()
    url = "https://amazon-products1.p.rapidapi.com/deals"
    querystring = {"min_number":"5","country":"US","type":"LIGHTNING_DEAL","max_number":"100"}
    headers = {
        'x-rapidapi-host': "amazon-products1.p.rapidapi.com",
        'x-rapidapi-key': "add2f36842msh0b1256e730655b6p1d7d6djsn6e6596a24978"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    response.raise_for_status()

    data = response.json()

    time_now = time.time()

    if not data['error']:
        data = data['offers']

        for deal in data:
            img_str = ""
            if deal['images']:
                for img in deal['images']:
                    start = img.find('/I/')
                    end = img.find('.jpg')
                    img_code = img[start+3:end]
                    img_str += img_code + ","

            add_deal = Daily(title=deal['title'],
                                asin=deal['asin'],
                                link=deal['full_link'],
                                curr_price=deal['prices']['current_price'],
                                orig_price=deal['prices']['previous_price'],
                                stars=deal['reviews']['stars'],
                                reviews=deal['reviews']['total_reviews'],
                                images=img_str)
            db.session.add(add_deal)

        first = Daily.query.get(1)
        if first:
            first.timestamp = time_now

        db.session.commit()
    else:
        print(data)