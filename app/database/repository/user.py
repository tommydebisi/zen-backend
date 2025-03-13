from app.database.base import Database
from app.database.models.user import User
from bson import ObjectId
from typing import Dict, Any
from flask_mailman import EmailMultiAlternatives
from app.utils.utils import capitalize_first_letter
from app.config import config

class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_email(self, email: str):
        """Fetch a user by email."""
        return self.db.get_one(User.__name__, {"email": email})
    
    def get_by_id(self, user_id: str):
        """Fetch a user by ID."""
        return self.db.get_one(User.__name__, {"_id": ObjectId(user_id)})

    def get_by_customer_code(self, customer_code: str):
        """Fetch a user by ID."""
        return self.db.get_one(User.__name__, {"customer_code": customer_code})

    def get_all_users(self):
        """Fetch all users."""
        return self.db.get_all(User.__name__)

    def create_user(self, data: Dict):
        """Insert a new user record."""
        result = self.db.insert_one(User.__name__, data)

        # fetch the inserted record
        return str(result.inserted_id)

    def find_and_update_user(self, query: Dict[str, Any], data: Dict):
        """Find a user by query and update the record."""
        return self.db.update_one(User.__name__, query, data)
    
    def find_and_delete_user(self, query: Dict[str, Any]):
        """Find a user by query and delete the record."""
        return self.db.delete_one(User.__name__, query)
    
    def send_welcome_email(self, user: User) -> None:
        subject = " Welcome to Zen Archery!"
        from_email = config.MAIL_DEFAULT_SENDER
        to_email = user.email

        # Plain text content (fallback)
        text_content = f"""
        Hi {capitalize_first_letter(user.firstName)},
        Welcome to Zen Archery! We're excited to have you join our community of archers.
        Check out our upcoming events and competitions at https://zenarchery.club/events.

        If you have any questions, feel free to reach out at info@zenarchery.club. We can't wait to see you on the range!
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
                    <td style="font-size: 14px; color: #333; padding: 20px">
                        <strong>Hi {user.firstName},</strong>
                        <p>
                        We’re thrilled to have you join the Zen Archery family!
                        Whether you’re a seasoned archer or just starting out, you’re
                        now part of a community that shares a passion for precision,
                        skill, and fun.
                        </p>
                        <p>Here’s what you can look forward to:</p>
                    </td>
                    </tr>

                    <!-- Bullet Points -->
                    <tr>
                    <td style="padding: 10px 20px; font-size: 14px">
                        ✅ Training Sessions – Guided practice to improve your aim<br />
                        ✅ Club Events & Competitions – Friendly matches and
                        tournaments<br />
                        ✅ Exclusive Member Perks – Discounts on gear, coaching, and
                        more<br />
                        ✅ Community & Support – Connect with fellow archers
                    </td>
                    </tr>

                    <!-- First Steps -->
                    <tr>
                    <td style="padding: 20px; font-size: 14px">
                        📍 <strong>First Steps:</strong>
                        <ul>
                        <li>
                            Check out our schedule:
                            <a href="https://zenarchery.club/events"
                            >https://zenarchery.club/events
                            </a>
                        </li>
                        <li style="margin: 5px 0">
                            Join our members' group:
                            <a href="https://zenarchery.club/ranking&records"
                            >https://zenarchery.club/ranking&records
                            </a>
                        </li>
                        <li>
                            Meet your coaches:
                            <a href="https://zenarchery.club/about"
                            >https://zenarchery.club/about
                            </a>
                        </li>
                        </ul>
                        <p>
                        We can't wait to see you on the range!
                        </p>
                    </td>
                    </tr>

                    <!-- Closing Statement -->
                    <tr>
                    <td align="left" style="padding: 20px; font-size: 14px">
                        🎯 <strong>Ready, Aim, Shoot!</strong>
                        <p>The Zen Archery Team</p>
                    </td>
                    </tr>

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

