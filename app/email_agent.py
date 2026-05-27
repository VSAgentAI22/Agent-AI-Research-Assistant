import imaplib
import email
import smtplib
import time
from email.mime.text import MIMEText
from ask_rag import ask_question

EMAIL = "vsagentai22@gmail.com"
PASSWORD = "qlxa curv qqvi qjep"

IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

CHECK_INTERVAL = 60


def read_latest_research_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, '(UNSEEN SUBJECT "Research Question")')
    email_ids = messages[0].split()

    if not email_ids:
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
    return sender, body.strip()


def send_reply(receiver_email, answer):
    email_body = f"""
Hello,

Thank you for your research question.

{answer}

Kind regards,
Agent AI Research Assistant
"""

    msg = MIMEText(email_body)
    msg["Subject"] = "AI Research Assistant Response"
    msg["From"] = EMAIL
    msg["To"] = receiver_email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()


def process_email():
    sender, question = read_latest_research_email()

    if not question:
        print("No new research question emails found.")
        return

    print("\nQuestion received:")
    print(question)

    answer = ask_question(question)

    print("\nGenerated answer:")
    print(answer)

    send_reply(sender, answer)

    print("\nReply email sent successfully.")


def main():
    print("Agent AI Email Research Assistant is running...")
    print('Only unread emails with subject "Research Question" will be processed.')
    print("Press CTRL + C to stop.\n")

    while True:
        process_email()
        time.sleep(CHECK_INTERVAL)


main()
