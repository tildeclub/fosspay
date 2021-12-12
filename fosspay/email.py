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

def send_thank_you(user, amount, monthly):
    if _cfg("smtp-host") == "":
        return
    smtp = smtplib.SMTP_SSL(_cfg("smtp-host"), _cfgi("smtp-port"))
    smtp.ehlo()
    smtp.login(_cfg("smtp-user"), _cfg("smtp-password"))
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
    smtp.sendmail(_cfg("smtp-from"), [ user.email ], message.as_string())
    smtp.quit()

def send_password_reset(user):
    if _cfg("smtp-host") == "":
        return
    smtp = smtplib.SMTP_SSL(_cfg("smtp-host"), _cfgi("smtp-port"))
    smtp.ehlo()
    smtp.login(_cfg("smtp-user"), _cfg("smtp-password"))
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
    smtp.sendmail(_cfg("smtp-from"), [ user.email ], message.as_string())
    smtp.quit()

def send_declined(user, amount):
    if _cfg("smtp-host") == "":
        return
    smtp = smtplib.SMTP_SSL(_cfg("smtp-host"), _cfgi("smtp-port"))
    smtp.ehlo()
    smtp.login(_cfg("smtp-user"), _cfg("smtp-password"))
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
    smtp.sendmail(_cfg("smtp-from"), [ user.email ], message.as_string())
    smtp.quit()

def send_new_donation(user, donation):
    if _cfg("smtp-host") == "":
        return
    smtp = smtplib.SMTP_SSL(_cfg("smtp-host"), _cfgi("smtp-port"))
    smtp.ehlo()
    smtp.login(_cfg("smtp-user"), _cfg("smtp-password"))
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
    smtp.sendmail(_cfg("smtp-from"), [ _cfg('your-email') ], message.as_string())
    smtp.quit()

def send_cancellation_notice(user, donation):
    if _cfg("smtp-host") == "":
        return
    smtp = smtplib.SMTP_SSL(_cfg("smtp-host"), _cfgi("smtp-port"))
    smtp.ehlo()
    smtp.login(_cfg("smtp-user"), _cfg("smtp-password"))
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
    smtp.sendmail(_cfg("smtp-from"), [ _cfg('your-email') ], message.as_string())
    smtp.quit()
