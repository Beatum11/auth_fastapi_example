from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from src.config import get_settings

settings = get_settings()

email_conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail.MAIL_USERNAME,
    MAIL_PASSWORD=settings.mail.MAIL_PASSWORD,
    MAIL_FROM=settings.mail.MAIL_FROM,
    MAIL_PORT=settings.mail.MAIL_PORT,
    MAIL_SERVER=settings.mail.MAIL_SERVER,
    #???
    MAIL_STARTTLS=settings.mail.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.mail.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

#TO-DO: change later to EmailStr
async def send_verification_email(email: str, token: str):

    verification_url = f"http://localhost:8000/api/auth/verify-email?token={token}"

    html_content = f"""
    <html>
        <body>
            <h2>Спасибо за регистрацию!</h2>
            <p>Пожалуйста, перейдите по ссылке ниже, чтобы подтвердить ваш email:</p>
            <a href="{verification_url}" target="_blank">Подтвердить email</a>
            <p>Если вы не регистрировались, просто проигнорируйте это письмо.</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject='Confirm your sign up',
        recipients=[email],
        body=html_content,
        subtype=MessageType.html
    )

    fm = FastMail(email_conf)
    await fm.send_message(message)

