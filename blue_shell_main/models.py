from blue_shell_main import db

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    asin = db.Column(db.String(20), nullable=False)

class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True, nullable=False)
    asin = db.Column(db.String(20), unique=True, nullable=False)
    link = db.Column(db.String(255), unique=True, nullable=False)
    curr_price = db.Column(db.Float, nullable=False)
    orig_price = db.Column(db.Float, nullable=False)
    stars = db.Column(db.Float, nullable=False)
    reviews = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Float, nullable=True)
    images = db.Column(db.Text, unique=True, nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(15), unique=True, nullable=False)
    image = db.Column(db.Text, unique=True, nullable=False)
    title = db.Column(db.Text, unique=True, nullable=False)
    link = db.Column(db.Text, unique=True, nullable=False)
    camel_link = db.Column(db.Text, unique=True, nullable=False)
    current_price = db.Column(db.String(15), nullable=False)
    amazon_high = db.Column(db.String(15), nullable=True)
    amazon_high_date = db.Column(db.String(30), nullable=True)
    amazon_low = db.Column(db.String(15), nullable=True)
    amazon_low_date = db.Column(db.String(30), nullable=True)
    amazon_avg = db.Column(db.String(15), nullable=True)
    third_high = db.Column(db.String(15), nullable=True)
    third_high_date = db.Column(db.String(30), nullable=True)
    third_low = db.Column(db.String(15), nullable=True)
    third_low_date = db.Column(db.String(30), nullable=True)
    third_avg = db.Column(db.String(15), nullable=True)
    last_update = db.Column(db.String(30), nullable=True)