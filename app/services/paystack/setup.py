from app.config import config
from paystackapi.paystack import Paystack

paystack = Paystack(secret_key=config.PAYSTACK_SECRET_KEY)