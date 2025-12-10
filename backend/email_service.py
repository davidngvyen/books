import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#email setup
YOUR_EMAIL = "davidqnguyen03@gmail.com"
YOUR_PASSWORD = "ganurmzpigljuwnd"
SEND_EMAILS = True

def send_order_bill(recipient_email, order_data):
    
    if not SEND_EMAILS:
        print(f"[Email Disabled] Bill for order #{order_data['order_id']} would be sent to {recipient_email}")
        print("To enable emails: Edit email_service.py and set SEND_EMAILS = True")
        return False
    
    if YOUR_EMAIL == "your.email@gmail.com" or YOUR_PASSWORD == "your app password here":
        print("EMAIL NOT CONFIGURED! Edit email_service.py first.")
        return False
    
    try:
        subject = f"Order Confirmation - Order #{order_data['order_id']}"
        body = generate_bill_text(order_data)
        
        message = MIMEMultipart()
        message['From'] = YOUR_EMAIL
        message['To'] = recipient_email
        message['Subject'] = subject
        
        message.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(YOUR_EMAIL, YOUR_PASSWORD)
            server.send_message(message)
        
        print(f"Email sent to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        print("Make sure you're using a Gmail App Password (not regular password)")
        return False

def generate_bill_text(order_data):
    
    bill = f"""

ONLINE BOOKSTORE - ORDER RECEIPT
Order ID: #{order_data['order_id']}
Customer: {order_data['username']}
Date: {order_data.get('created_at', 'N/A')}

ORDER ITEMS:
"""
    
    for i, item in enumerate(order_data['items'], 1):
        item_type = item.get('item_type') or item.get('type', 'buy')
        item_type = item_type.upper()
        bill += f"\n{i}. {item['title']} by {item['author']}\n"
        bill += f"   Type: {item_type}\n"
        bill += f"   Price: ${item['price']:.2f}\n"
    
    bill += f"""

TOTAL AMOUNT: ${order_data['total']:.2f}
Payment Status: {order_data.get('payment_status', 'Pending')}

"""
    
    return bill
