import os
import ssl
import smtplib

from utils import format_receipt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Create the welcome message
def getSalutations(user) -> str:
    message = f"""\
    Hello, {user}

    Welcome to Seneca, your new favorite ebookstore!

    We're thrilled to have you join our community of book lovers. At Seneca, we believe that reading opens up new worlds and possibilities. Our mission is to provide you with a wide range of ebooks across various genres, ensuring that you'll always find something that piques your interest.

    Here's what you can look forward to as a member of Seneca:
    - A diverse collection of ebooks, from bestsellers to hidden gems.
    - Exclusive discounts and special offers.
    - Personalized recommendations based on your reading preferences.
    - Easy and secure access to your library, anytime, anywhere.

    Happy reading!

    Best regards,
    The Seneca Team (Its just me Parth but still)
    """

    return message

def sendReceipt(receiver, items, order) -> None:
    email_sender = os.environ.get("email_sender")
    email_password = os.environ.get("email_pass")

    receipt = format_receipt(items, order.id, order.order_quantity, order.order_time, order.total_price)

    email_message = MIMEMultipart()
    email_message['From'] = email_sender
    email_message['To'] = receiver
    email_message['Subject'] = 'Purchase Receipt: Seneca'
    email_message.attach(MIMEText(receipt, 'plain'))

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(email_message)

def sendSalutation(receiver) -> None:
    email_sender = os.environ.get("email_sender")
    email_password = os.environ.get("email_pass")

    email_message = MIMEMultipart()
    email_message["From"] = email_sender
    email_message["To"] = receiver.email_id
    email_message['Subject'] = 'Welcome to Seneca!'
    email_message.attach(MIMEText(getSalutations(receiver.first_name), 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(email_message)
