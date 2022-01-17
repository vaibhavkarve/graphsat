#!/usr/bin/env python3.9
"""A module for mailing the results after they have been computed."""
from functools import partial
import smtplib
from email.message import EmailMessage
from typing import Any, List


def sendemail(from_addr: str,  # pylint: disable=too-many-arguments
              to_addr_list: List[str],
              cc_addr_list: List[str],
              subject: str,
              message: str,
              login: str,
              password: str,
              smtpserver: str = 'smtp.gmail.com:587') -> Any:
    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    messageb = (header + message).encode('utf-8')

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login, password)
    problems = server.sendmail(from_addr, to_addr_list, messageb)
    server.quit()
    return problems


SENDMAIL = partial(sendemail,
                   from_addr='vaibhavskarve@gmail.com',
                   to_addr_list=['vaibhavskarve@gmail.com'],
                   cc_addr_list=[],
                   subject='[mem.math] Job completed',
                   login='vaibhavskarve',
                   password='watebnbqiktonbog')
