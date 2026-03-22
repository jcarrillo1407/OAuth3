from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_mfa_email(user, code):
    subject = "Tu código de verificación"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@oauth3.local")
    to = [user.email]

    try:
        html_content = render_to_string("emails/mfa_code.html", {
            "user": user,
            "code": code,
        })
    except Exception:
        html_content = f"""
        <html>
            <body>
                <h2>Verificación de acceso</h2>
                <p>Hola {user.nombres},</p>
                <p>Tu código es: <strong>{code}</strong></p>
                <p>Expira en 5 minutos.</p>
            </body>
        </html>
        """

    text_content = f"Hola {user.nombres}, tu código de verificación es: {code}"

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()