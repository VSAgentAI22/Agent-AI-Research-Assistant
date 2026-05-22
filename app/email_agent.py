import imaplib
import email
import smtplib
from email.mime.text import MIMEText

from ask_rag import ask_question

EMAIL = "vsagentai22@gmail.com"
PASSWORD ="rtwb epud ykjn grfe"

IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def read_latest_email():

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)

    mail.login(EMAIL, PASSWORD)

    mail.select("inbox")

    status, messages = mail.search(None, "UNSEEN")

    email_ids = messages[0].split()

    if not email_ids:
        print("No unread emails found.")
        mail.logout()
        return None, None

    latest_email_id = email_ids[-1]

    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

    raw_email = msg_data[0][1]

    msg = email.message_from_bytes(raw_email)

    sender = email.utils.parseaddr(msg["From"])[1]

    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    mail.logout()

    return sender, body


def send_reply(receiver_email, answer):

    msg = MIMEText(answer)

    msg["Subject"] = "AI Research Assistant Response"
    msg["From"] = EMAIL
    msg["To"] = receiver_email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

    server.starttls()

    server.login(EMAIL, PASSWORD)

    server.send_message(msg)

    server.quit()


def main():

    sender, question = read_latest_email()

    if question:

        print("Question received:")
        print(question)

        answer = ask_question(question)

        print("\nGenerated Answer:\n")
        print(answer)

        send_reply(sender, answer)

        print("\nReply email sent successfully.")


main()
