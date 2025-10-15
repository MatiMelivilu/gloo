import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailSender:
    def __init__(self, user="309b56001@smtp-brevo.com", password="wsv60X8LqO4czYt2", server="smtp-relay.brevo.com", port=587):
        """
        Inicializa el cliente SMTP.
        """
        self.user = user
        self.password = password
        self.server = server
        self.port = port

    def enviar_resumen_venta(self, destinatario, monto_tarjeta, monto_efectivo, fichas, promociones):
        """
        Envia un correo con el resumen de venta.
        """
        asunto = f"Resumen de venta - {datetime.now():%d/%m/%Y %H:%M}"

        # Cuerpo HTML del mensaje
        cuerpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Resumen de venta</h2>
            <p><strong>Monto pagado con tarjeta:</strong> ${monto_tarjeta}</p>
            <p><strong>Monto pagado en efectivo:</strong> ${monto_efectivo}</p>
            <p><strong>Cantidad de fichas compradas sin promociones:</strong> {fichas}</p>
            <p><strong>Cantidad de promociones compradas:</strong> {promociones}</p>
        </body>
        </html>
        """

        # Crear el mensaje
        mensaje = MIMEMultipart()
        mensaje["From"] = self.user
        mensaje["To"] = destinatario if isinstance(destinatario, str) else ", ".join(destinatario)
        mensaje["Subject"] = asunto
        mensaje.attach(MIMEText(cuerpo, "html"))

        # Envio
        try:
            with smtplib.SMTP(self.server, self.port) as smtp:
                smtp.starttls()  # Inicia conexion segura
                smtp.login(self.user, self.password)
                smtp.send_message(mensaje)
                print("? Correo enviado correctamente a:", destinatario)
        except Exception as e:
            print("? Error al enviar correo:", e)
