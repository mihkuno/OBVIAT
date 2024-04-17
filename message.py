import smtplib

# Gmail SMTP server configuration
smtp_server   = "smtp.gmail.com"
smtp_port     = 587
smtp_username = "caindayjoeninyo@gmail.com"
smtp_password = "app password here"

# Email configuration
sender_email   = smtp_username
receiver_email = "caindayjoeninyo@gmail.com"
subject        = "Subject: Your Email Subject"
body           = "Your email content here."

# Construct email message
message = f"{subject}\n\n{body}"

# Connect to Gmail's SMTP server
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()  # Secure the connection
server.login(smtp_username, smtp_password)  # Login to your Gmail account

# Send email
server.sendmail(sender_email, receiver_email, message)

# Quit SMTP server
server.quit()

print("Email sent successfully!")
