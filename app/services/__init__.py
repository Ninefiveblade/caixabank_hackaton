from flask_mail import Message

from app import mail

MESSAGE_SAVING = """
Dear {user_name},

Great news! Your savings are nearing the target amount of {alert_target_amount}.
Keep up the great work and stay consistent!

Best Regards,
The Management Team
"""

MESSAGE_BALANCE_DROP = """
Dear {user_name},

We noticed a significant balance drop in your account more than {alert_balance_drop_threshold}.
If this wasn't you, please review your recent transactions to ensure everything is correct.

Best Regards,
The Management Team
"""


def send_email(subject, recipient, body):
    msg = Message(subject, recipients=[recipient], body=body, sender="test@test.com")
    mail.send(msg)
