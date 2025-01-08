import asyncio

import sendgrid
from fastapi import status
from sendgrid.helpers.mail import Email, Mail, To

from dripdrop.services import templates
from dripdrop.settings import ENV, settings

client = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)


async def send_mail(to_email: str, subject: str, html_content: str):
    def _send_mail():
        mail = Mail(
            from_email=Email(email="app@dripdrop.icu", name="dripdrop"),
            to_emails=To(email=to_email),
            subject=subject,
            html_content=html_content,
        )
        if settings.env != ENV.TESTING:
            response = client.send(message=mail)
            if status.HTTP_400_BAD_REQUEST <= response.status_code:
                raise Exception("Failed to send email", response.body)

    return await asyncio.to_thread(_send_mail)


async def send_verification_email(email: str, link: str):
    verify_template = templates.env.get_template("verify.jinja")
    output = await verify_template.render_async(link=link)
    await send_mail(to_email=email, subject="Verification", html_content=output)


async def send_password_reset_email(email: str, token: str):
    reset_template = templates.env.get_template("reset.jinja")
    output = await reset_template.render_async(token=token)
    await send_mail(to_email=email, subject="Reset Password", html_content=output)
