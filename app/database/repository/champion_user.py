from app.database.base import Database
from app.database.models.champion_user import ChampionUser
from bson import ObjectId
from typing import Dict, Any
from flask_mailman import EmailMultiAlternatives
from app.config import config
from app.utils.utils import capitalize_first_letter


class ChampionUserRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, champion_user_id: str):
        """Fetch a user by ID."""
        return self.db.get_one(ChampionUser.__name__, {"_id": ObjectId(champion_user_id)})
    
    def create_champion_user(self, data: Dict):
        """Insert a new user record."""
        result = self.db.insert_one(ChampionUser.__name__, data)

        # fetch the inserted record
        return str(result.inserted_id)
    
    def find_and_update_champion_user(self, query: Dict[str, Any], data: Dict):
        """Find a champion user by query and update the record."""
        return self.db.update_one(ChampionUser.__name__, query, data)
    
    def find_and_delete_champion_user(self, query: Dict[str, Any]):
        """Find a champoion user by query and delete the record."""
        return self.db.delete_one(ChampionUser.__name__, query)
    def send_welcome_email(self, champion_user: ChampionUser) -> None:
        subject = "Thank You for Registering - Zen Archery Open Competition 2025"
        from_email = config.MAIL_DEFAULT_SENDER
        to_email = champion_user.email

        # Plain text content (fallback)
        text_content = f"""
        Hi {champion_user.firstName},
        Thank you for registering for the Zen Archery Open Competition 2025! We’re excited to have you join us for this incredible event.
        Your Unique ID: {champion_user.unique_id}
        Please keep this ID handy, as you may be asked to provide it during the event.

        We’re looking forward to an amazing competition and can’t wait to see you showcase your skills. If you have any questions, feel free to reach out.

        For International Athletes:
        If you are an international athlete, please click the link below to fill out the visa form:
        https://forms.gle/oPpq9KCd7NArgYJ76

        See you soon! 🎯 

        The Zen Archery Team
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
                        <strong>Hi {capitalize_first_letter(champion_user.firstName)},</strong>
                        <p>
                        Thank you for registering for the Zen Archery Open Competition 2025!
                        We’re excited to have you join us for this incredible event
                        </p>
                        <p>Your Unique ID: <span style="font-weight: 700">{champion_user.unique_id}</span></p>
                    </td>
                    </tr>

                    <!-- Bullet Points -->
                    <tr>
                    <td style="padding: 10px 20px; font-size: 14px">
                        Please keep this ID handy, as you may be asked to provide it
                        during the event.
                        <br />
                        We’re looking forward to an amazing competition and can’t wait
                        to see you showcase your skills. If you have any questions, feel
                        free to reach out<br />
                    </td>
                    </tr>
                    <tr>
                    <td style="padding: 20px; font-size: 14px">
                        For International Athletes: <br />
                        If you are an international athlete, please click the link below
                        to fill out the visa form:
                        <br />
                        <a href="https://forms.gle/oPpq9KCd7NArgYJ76" target="_blank" style="color: #0e2b41; font-weight: 700; text-decoration: none" >
                        Visa Form Link
                        </a>
                    </td>
                    </tr>

                    <!-- First Steps -->

                    <!-- Closing Statement -->
                    <tr>
                    <td align="left" style="padding: 20px; font-size: 14px">
                        <strong>See you soon! </strong>
                        🎯
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
