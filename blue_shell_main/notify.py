import time, smtplib
from email.message import EmailMessage
from blue_shell_main import db
from blue_shell_main.models import Track, Product
from blue_shell_main.utility import *


def send_mail():
    items = Track.query.all()
    if items:
        for item in items:
            item_id = item.id
            url = short_url(item.asin)
            current_price = price_update(url)
            if current_price <= item.target_price:
                product = Product.query.filter_by(asin=item.asin).first()
                # title = (product.title).encode('ascii', 'ignore').decode('utf-8')
                img = product.image
                link = product.camel_link
                msg = EmailMessage()
                msg['Subject'] = 'Blue Shell Alert'
                msg['From'] = os.environ.get('BSA_USER')
                msg['To'] = item.email
                msg.set_content('''
                <!DOCTYPE html>
                <html>
                    <body>
                        <div style='background:linear-gradient(45deg, rgba(62, 161, 219, 1) 11.2%, rgba(93, 52, 236, 1) 100.2%); padding: 10px 20px; width: 600px'>
                            <h2 style="font-family:Arial, Helvetica, Times, sans-serif; color:#fff">Blue Shell Amazon</h2>
                        </div>
                        <div style='width: 600px; height: auto; text-align:center; margin: 20px;'>''' +
                            f"<img src={img} style='width: 400px; height: auto;'>" + 
                            f'<div style="font-size: 20px; color: #000">This item is currently ${current_price}' +
                                '''<br>''' +
                                f"<a href={link}>See this in Amazon!</a>" +
                            '''</div>
                        <small style="color: #757575; margin-top: 20px; text-align: center;">This item will be taken off from the tracker list</small>
                        </div>
                    </body>
                </html>
                ''', subtype='html')

                with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
                    connection.starttls() # Encrypt the traffic
                    connection.login(os.environ.get('BSA_USER'), os.environ.get('BSA_PW'))
                    connection.send_message(msg)

                Track.query.filter_by(id=item_id).delete()
                db.session.commit()
            
            time.sleep(5)

send_mail()