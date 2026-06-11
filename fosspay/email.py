# fosspay/email.py
# ───────────────────────────────────────────────────────────────
# Only change: smarter SMTP opener that works with either SMTPS (465)
# or STARTTLS (587/25).  All calling functions now use it.
# ───────────────────────────────────────────────────────────────
import smtplib
import os
import html.parser
from email.mime.text import MIMEText
from email.utils import localtime, format_datetime
from werkzeug.utils import secure_filename
from flask import url_for
from string import Template

from fosspay.database import db
from fosspay.objects import User, DonationType
from fosspay.config import _cfg, _cfgi
from fosspay.currency import currency


# helper: open & log in using the right TLS mode
def _open_smtp():
    if _cfg("smtp-host") == "":
        return None
    host = _cfg("smtp-host")
    port = _cfgi("smtp-port")
    if port == 465:                                 # implicit TLS
        smtp = smtplib.SMTP_SSL(host, port)
    else:                                           # STARTTLS pathway
        smtp = smtplib.SMTP(host, port)
        smtp.ehlo()
        smtp.starttls()
    smtp.ehlo()
    smtp.login(_cfg("smtp-user"), _cfg("smtp-password"))
    return smtp


def send_thank_you(user, amount, monthly):
    smtp = _open_smtp()
    if smtp is None:
        return
    with open("emails/thank-you") as f:
        tmpl = Template(f.read())
        message = MIMEText(tmpl.substitute(**{
            "root": _cfg("protocol") + "://" + _cfg("domain"),
            "your_name": _cfg("your-name"),
            "summary": ("Monthly donation" if monthly else "One-time donation"),
            "amount": currency.amount("{:.2f}".format(amount / 100)),
            "your_email": _cfg("your-email")
        }))
    message['Subject'] = "Thank you for your donation!"
    message['From'] = _cfg("smtp-from")
    message['To'] = user.email
    message['Date'] = format_datetime(localtime())
    smtp.sendmail(_cfg("smtp-from"), [user.email], message.as_string())
    smtp.quit()


def send_password_reset(user):
    smtp = _open_smtp()
    if smtp is None:
        return
    with open("emails/reset-password") as f:
        tmpl = Template(f.read())
        message = MIMEText(tmpl.substitute(**{
            "password_reset": user.password_reset,
            "root": _cfg("protocol") + "://" + _cfg("domain"),
            "your_name": _cfg("your-name"),
            "your_email": _cfg("your-email")
        }))
    message['Subject'] = "Reset your donor password"
    message['From'] = _cfg("smtp-from")
    message['To'] = user.email
    message['Date'] = format_datetime(localtime())
    smtp.sendmail(_cfg("smtp-from"), [user.email], message.as_string())
    smtp.quit()


def send_declined(user, amount):
    smtp = _open_smtp()
    if smtp is None:
        return
    with open("emails/declined") as f:
        tmpl = Template(f.read())
        message = MIMEText(tmpl.substitute(**{
            "root": _cfg("protocol") + "://" + _cfg("domain"),
            "your_name": _cfg("your-name"),
            "amount": currency.amount("{:.2f}".format(amount / 100))
        }))
    message['Subject'] = "Your monthly donation was declined."
    message['From'] = _cfg("smtp-from")
    message['To'] = user.email
    message['Date'] = format_datetime(localtime())
    smtp.sendmail(_cfg("smtp-from"), [user.email], message.as_string())
    smtp.quit()


def send_new_donation(user, donation):
    smtp = _open_smtp()
    if smtp is None:
        return
    with open("emails/new_donation") as f:
        tmpl = Template(f.read())
        message = MIMEText(tmpl.substitute(**{
            "email": user.email,
            "your_name": _cfg("your-name"),
            "amount": currency.amount("{:.2f}".format(
                donation.amount / 100)),
            "frequency": (" per month"
                if donation.type == DonationType.monthly else ""),
            "comment": donation.comment or "",
        }))
    message['Subject'] = "New donation on fosspay!"
    message['From'] = _cfg("smtp-from")
    message['To'] = f"{_cfg('your-name')} <{_cfg('your-email')}>"
    message['Date'] = format_datetime(localtime())
    smtp.sendmail(_cfg("smtp-from"), [_cfg('your-email')], message.as_string())
    smtp.quit()


def send_cancellation_notice(user, donation):
    smtp = _open_smtp()
    if smtp is None:
        return
    with open("emails/cancelled") as f:
        tmpl = Template(f.read())
        message = MIMEText(tmpl.substitute(**{
            "email": user.email,
            "root": _cfg("protocol") + "://" + _cfg("domain"),
            "your_name": _cfg("your-name"),
            "amount": currency.amount("{:.2f}".format(
                donation.amount / 100)),
        }))
    message['Subject'] = "A monthly donation on fosspay has been cancelled"
    message['From'] = _cfg("smtp-from")
    message['To'] = f"{_cfg('your-name')} <{_cfg('your-email')}>"
    message['Date'] = format_datetime(localtime())
    smtp.sendmail(_cfg("smtp-from"), [_cfg('your-email')], message.as_string())
    smtp.quit()
