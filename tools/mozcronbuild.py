#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import os

from tools import moz_l10n_builder


MOZDIR = os.path.join( os.path.expanduser('~'), 'mozbuild' )
# E-mail details
FROM_ADDRESS = 'mozl10n@translate.org.za'
SMTP_SERVER = 'localhost'
SMTP_USER = ''
SMTP_PASS = ''


def build_langs(checkout=False):
    olddir = os.getcwd()
    os.chdir(MOZDIR)

    moz_l10n_builder.main(
        langs='ALL',
        mozcheckout=checkout,
        recover=True,
        potpack=True,
        popack=True
        update_trans=True,
    )

    os.chdir(olddir)

def check_potpacks():
    """Copy new and check available POT-packs."""
    pass

def send_mail(subject, text, addresses):
    import email.Message
    import smtplib

    smtp = smtplib.SMTP(SMTP_SERVER)
    smtp.login(SMTP_USER, SMTP_PASS)

    for address in addresses:
        message = email.Message.Message()
        message['To'] = address
        message['From'] = FROM_ADDRESS
        message['Subject'] = subject
        message.set_payload(text)

        smtp.sendmail(FROM_ADDRESS, address, message.as_string())

    smtp.quit()

def update_rss():
    """Update the RSS feed with the available POT-packs."""
    pass

USAGE='%prog [<options>]'
def create_option_parser():
    """Creates and returns cmd-line option parser."""

    from optparse import OptionParser

    parser = OptionParser(usage=USAGE)

    parser.add_option(
        '-m', '--mailto',
        dest='mailto',
        action='append',
        help='Add the given e-mail address to the people that should receive the output via e-mail'
    )

    return parser

def main(mailto=[]):
    checkout = False

    if not os.path.isdir(MOZDIR):
        os.makedirs(MOZDIR)
        checkout = True

    import StringIO
    import sys
    output = StringIO.StringIO()
    streambackups = (sys.stdout, sys.stderr)
    sys.stdout = output
    sys.stderr = output

    build_langs(checkout=checkout)
    check_potpacks()
    update_rss()

    if mailto:
        send_mail('mozcronbuild.py output', output.getvalue(), mailto)

    sys.stdout, sys.stderr = streambackups

def main_cmd_line():
    options, args = create_option_parser().parse_args()

    main(mailto=options.mailto)

if __name__ == '__main__':
    main_cmd_line()
