from app.database.base import Database
from app.database.models.payment_history import PaymentHistory
from app.database.models.plan import Plan
from bson import ObjectId
from typing import Dict, Any, List
from app.config import config
from app.utils.utils import capitalize_first_letter
from flask_mailman import EmailMultiAlternatives


class PaymentHistoryRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_user_id(self, user_id: str):
        """Fetch an archer rank by ID."""
        return self.db.get_one(PaymentHistory.__name__, {"user_id": ObjectId(user_id)})
    
    def create_payment_history(self, data: Dict):
        """
            Create payment history
        """
        result = self.db.insert_one(PaymentHistory.__name__, data)

        # fetch the inserted record
        return str(result.inserted_id)
    
    def all_payment_history_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """
            Get all payment history for a user
        """
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id)
                }
            },
            {
                "$lookup": {
                    "from": "Plan",
                    "localField": "plan_id",
                    "foreignField": "_id",
                    "as": "plan_details"
                }
            },
            {
                "$unwind": "$plan_details"
            },
            {
                "$project": {
                    "_id": 0,
                    "plan_name": "$plan_details.newplan",
                    "amount": {"$toInt": {"$divide": ["$amount", 100]}},
                    "payment_date": 1,
                    "status": 1
                }
            },
            {
                "$sort": {"payment_date": -1}
            }
        ]
        
        return self.db.aggregate(PaymentHistory.__name__, pipeline)
    
    def all_payment_history(self) -> List[Dict[str, Any]]:
        pipeline = [
            {
                "$lookup": {
                    "from": "Plan",
                    "localField": "plan_id",
                    "foreignField": "_id",  # The field in Plan to match against
                    "as": "plan_details"  # The resulting array containing matched Plan documents
                }
            },
            {
                "$unwind": {
                    "path": "$plan_details",  # Unwind the plan_details array
                    "preserveNullAndEmptyArrays": True  # Allow documents with no matching plan to pass through
                }
            },
            {
                "$project": {
                    "_id": 0,  # Exclude the MongoDB default _id field
                    "plan_name": {
                        "$cond": {
                            "if": {"$ne": ["$plan_id", None]},  # If plan_id is not null
                            "then": "$plan_details.newplan",  # Use newplan from the Plan model
                            "else": "$email"  # Otherwise, use the email field
                        }
                    },
                    "amount": 1,  # Include the amount field from PaymentHistory
                    "payment_date": 1,  # Include the payment_date field from PaymentHistory
                    "status": 1  # Include the status field from PaymentHistory
                }
            },
            {
                "$sort": {"payment_date": -1}  # Sort the results by payment_date in descending order
            }
        ]

        return self.db.aggregate(PaymentHistory.__name__, pipeline)
    
    def send_payment_confirmation_email(self, customer_email: str, amount: int, first_name: str):
        """
            payment confirmation email
        """
        subject = "Payment Confirmed - Zen Archery Club"
        from_email = config.MAIL_DEFAULT_SENDER
        to_email = customer_email
        cap_first_name = capitalize_first_letter("archer" if not first_name else first_name)

        # fallback
        text_content = f"""\
        Dear {cap_first_name},  
        Thank you for your payment to **Zen Archery Club**. Your transaction was successful, and we’ve received your payment of {amount}
        If you have any questions or need further assistance, feel free to reach out to us at {from_email} or call us at [phone number].  

        We appreciate your support and look forward to seeing you at the club!  

        Best regards,  
        The Zen Archery Club Team
        """

        # HTML content
        html_content = f"""\
        <!DOCTYPE html>
        <html>
        <head>
            <title>Welcome to Zen Archery</title>
        </head>
        <body
            style="
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            font-family: Arial, sans-serif;
            "
        >
            <table
            role="presentation"
            width="100%"
            cellspacing="0"
            cellpadding="0"
            border="0"
            style="background-color: #f4f4f4; padding: 20px"
            >
            <tr>
                <td align="center">
                <table
                    role="presentation"
                    width="600"
                    cellspacing="0"
                    cellpadding="0"
                    border="0"
                    style="background-color: #ffffff"
                >
                    <!-- Logo Section -->
                    <tr>
                    <td
                        align="center"
                        style="padding: 20px; background-color: #e9f4fd"
                    >
                        <img
                        src="https://res.cloudinary.com/dwsaew3cp/image/upload/v1741436688/qyf9reecykaafecpgsfy.png"
                        alt="Zen Archery Logo"
                        style="object-fit: contain"
                        width="68"
                        height="42"
                        />
                    </td>
                    </tr>

                    <!-- Greeting Section -->
                    <tr>
                    <td
                        style="
                        font-size: 14px;
                        color: #333;
                        padding: 20px 30px 0px 20px;
                        "
                    >
                        <strong>Dear {cap_first_name},</strong>
                        <p>Thank you for your payment to Zen Archery Club.</p>
                        <p>
                        Your transaction was successful, and we’ve received your
                        payment of <span style="color: #0e2b41; font-weight: 700; text-decoration: none">NGN {amount // 100}</span>.
                        </p>
                        <p>
                        We appreciate your support and look forward to seeing you at
                        the club!
                        </p>
                    </td>
                    </tr>

                    <!-- Bullet Points -->

                    <tr>
                    <td style="padding: 20px; font-size: 14px">
                        <p>Best regards,</p>
                        <p>The Zen Archery Club Team</p>
                    </td>
                    </tr>

                    <!-- First Steps -->

                    <!-- Closing Statement -->

                    <!-- Footer -->
                    <tr>
                    <td
                        align="center"
                        style="
                        padding: 30px 20px;
                        border-top: 1px solid #ddd;
                        font-size: 14px;
                        color: #777;
                        text-align: left;
                        "
                    >
                        <table
                        role="presentation"
                        width="100%"
                        cellspacing="0"
                        cellpadding="0"
                        border="0"
                        >
                        <tr>
                            <td align="left" width="50%">
                            <img
                                src="https://res.cloudinary.com/dwsaew3cp/image/upload/v1741436688/qyf9reecykaafecpgsfy.png"
                                alt="Zen Archery Logo"
                                style="object-fit: contain"
                                width="68"
                                height="42"
                            />
                            </td>
                            <td align="right" width="50%">
                            <a href="#"
                                ><img
                                src="https://res.cloudinary.com/dwsaew3cp/image/upload/v1741436559/eltgshlt6svt8cpmwejv.png"
                                alt="Social 1"
                                width="30"
                            /></a>
                            <a style="margin: 0 10px" href="#"
                                ><img
                                src="https://res.cloudinary.com/dwsaew3cp/image/upload/v1741436593/c0n1mv1lvqqbreppagww.png"
                                alt="Social 2"
                                width="30"
                            /></a>
                            <a href="#"
                                ><img
                                src="https://res.cloudinary.com/dwsaew3cp/image/upload/v1741436494/voyozqnzmieawdpkbttl.png"
                                alt="Social 3"
                                width="30"
                            /></a>
                            </td>
                        </tr>
                        <tr>
                            <td
                            colspan="2"
                            style="padding-top: 30px; font-size: 14px; color: #333"
                            >
                            If you have any questions or need assistance, our support
                            team is here to help. Contact us at
                            <a
                                href="mailto:info@zenarchery.club"
                                style="
                                color: #0e2b41;
                                font-weight: 700;
                                text-decoration: none;
                                "
                                >info@zenarchery.club</a
                            >
                            or
                            <a
                                href="tel:+2349134788226"
                                style="
                                color: #0e2b41;
                                font-weight: 700;
                                text-decoration: none;
                                "
                                >+234 913 478 8226</a
                            >.
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2" style="padding-top: 10px; font-size: 14px">
                            Click
                            <a
                                href="#"
                                style="
                                color: #0e2b41;
                                font-weight: 700;
                                text-decoration: underline;
                                "
                                >here</a
                            >
                            to unsubscribe.
                            </td>
                        </tr>
                        <tr>
                            <td
                            colspan="2"
                            style="padding-top: 10px; font-size: 14px; color: #777"
                            >
                            Copyright &copy; 2024 Zen Archery. All rights reserved.
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>
                </table>
                </td>
            </tr>
            </table>
        </body>
        </html>
        """

        # ✅ Create an email message with text content
        email_msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])

        # ✅ Attach HTML content properly
        email_msg.attach_alternative(html_content, "text/html")

        # ✅ Send the email
        email_msg.send()

