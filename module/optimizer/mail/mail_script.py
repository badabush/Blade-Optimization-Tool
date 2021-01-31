import smtplib, ssl

import configparser
import json
import os
import re

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mimetypes import guess_type
from pathlib import Path


def deapMail(configfile, attachments, custom_message = ""):
    """
    Function for mailing the Log and Plots to assigned recipients.Called in module/optimizer/genetic_algorithm/deaptools
    after creating log folder and plotting has finished.

    :param configfile: full path from cwd to config file
    :type configfile: Path
    :param attachments: list of attachments; has to start with log file
    :type attachments: list

    :return:
    """

    config = configparser.ConfigParser()
    config.read(configfile)

    subject = "New Log"

    sender_email = config['login']['user']
    password = config['login']['password']
    receiver_email = json.loads(config.get('recipient', 'list'))

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email[0]
    message["Subject"] = subject
    if len(receiver_email) > 1:
        message["Bcc"] = ", ".join(receiver_email[1:])  # Recommended for mass emails

    # get parameters from log and put into body
    fp = open(attachments[0], 'rb')
    lines = fp.readlines()
    Date = 0
    POP_SIZE = 0
    CXPB = 0
    MUTPB = 0
    try:
        for line in lines:
            if "POP_SIZE" in line.__str__():
                substr = line.__str__().split("---")
                ssubstr = substr[1].split(", ")
                POP_SIZE = ssubstr[0].split(": ")[1]
                CXPB = ssubstr[1].split(": ")[1]
                MUTPB = ssubstr[2].split(": ")[1]
                rematch = re.search(r"\[([0-9]{2}-[A-Z][a-z]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2})", substr[0])
                Date = rematch.group(1)
    except IndexError as e:
        print(e)

    body = custom_message + """
        This is a generated E-Mail by the DeapBot. A new run has finished successfully.
        
        Date: {0}
        Population size: {1}
        CXPB: {2}
        MUTPB: {3}
        """.format(Date, POP_SIZE, CXPB, MUTPB)

    # add body to email
    message.attach(MIMEText(body, "plain"))

    # add attachments
    if attachments is not None:
        for filename in attachments:
            if os.path.basename(filename)[-3:] == "log":
                attachment = MIMEBase("application", "octet-stream")
                fp = open(filename, 'rb')
                attachment.set_payload(fp.read())
            else:
                mimetype, encoding = guess_type(os.path.basename(filename))
                mimetype = mimetype.split('/', 1)
                fp = open(filename, 'rb')
                attachment = MIMEBase(mimetype[0], mimetype[1])
                attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
            message.attach(attachment)

    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


if __name__ == "__main__":
    configfile = Path.cwd() / "config/mailinglist.ini"
    dir = "log/30-11-2020_12.22.45/"
    attachments = [Path.cwd() / dir / "debug.log",
                   Path.cwd() / dir / "gene_output_density.png",
                   Path.cwd() / dir / "pp_ao_omega_contour.png",
                   Path.cwd() / dir / "pp_ao_time.png"]

    deapMail(configfile, attachments)
