from app.database.models.contact_us import ContactUs
from flask_mailman import EmailMultiAlternatives, Mail
from app.config import config
from app.utils.utils import capitalize_first_letter


class ContactUsRepository:
    def __init__(self, mail: Mail):
        self.mail = mail

    def send_email(self, contact_message: ContactUs) -> None:
        first_name = capitalize_first_letter(contact_message.first_name)
        last_name = capitalize_first_letter(contact_message.last_name)

        subject = f"New Contact Us Message from {first_name} {last_name}"
        from_email = config.MAIL_DEFAULT_SENDER
        to_email = contact_message.email
        text_content = f"""
        New Contact Us Message
        Name: {first_name} {last_name}
        Phone Number: {contact_message.phone_number}
        Email: {contact_message.email}
        Message: {contact_message.message}
        """

        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f9f9f9;
                    padding: 20px;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #fff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #ddd;
                }}
                .header h1 {{
                    font-size: 24px;
                    color: #007BFF;
                }}
                .content {{
                    margin: 20px 0;
                }}
                .content p {{
                    margin: 10px 0;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #777;
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>Contact Us Message</h1>
                </div>
                <div class="content">
                    <p><strong>Name:</strong> {contact_message.first_name} {contact_message.last_name}</p>
                    <p><strong>Phone Number:</strong> {contact_message.phone_number}</p>
                    <p><strong>Email:</strong> {contact_message.email}</p>
                    <p><strong>Message:</strong></p>
                    <p>{contact_message.message}</p>
                </div>
                <div class="footer">
                    <p>If you have additional questions, feel free to reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # ✅ Create an email message with text content
        email_msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])

        # ✅ Attach HTML content properly
        email_msg.attach_alternative(html_content, "text/html")

        # ✅ Send the email
        email_msg.send()