"""
Module pour l'envoi d'emails aux utilisateurs.
Gère les emails de bienvenue, confirmation et autres notifications.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class EmailService:
    def __init__(self):
        # Configuration SMTP - vous pouvez modifier ces valeurs
        self.smtp_server = "smtp.gmail.com"  # Pour Gmail
        self.smtp_port = 587  # Port pour TLS
        
        # Variables d'environnement pour sécurité
        # Vous devez configurer ces variables d'environnement
        self.sender_email = os.getenv('SENDER_EMAIL', 'votre-email@gmail.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', 'votre-mot-de-passe-app')
        self.sender_name = "WhatToWatch - Recommandations"
        
        # Configuration de sécurité
        self.context = ssl.create_default_context()
        
    def send_welcome_email(self, user_email, user_name):
        """
        Envoie un email de bienvenue après l'inscription.
        """
        try:
            # Créer le message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Bienvenue sur WhatToWatch ! 🎬"
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = user_email
            
            # Contenu HTML de l'email
            html_content = f"""
            <html>
              <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                  <h1 style="color: #007bff; text-align: center;">
                    🎬 Bienvenue sur WhatToWatch !
                  </h1>
                  
                  <p>Bonjour <strong>{user_name}</strong>,</p>
                  
                  <p>Félicitations ! Votre compte a été créé avec succès sur WhatToWatch, 
                  votre plateforme personnalisée de recommandations de films et séries.</p>
                  
                  <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">🚀 Prochaines étapes :</h3>
                    <ul style="color: #555;">
                      <li>✅ Connectez-vous avec votre email : <strong>{user_email}</strong></li>
                      <li>🎯 Configurez vos préférences de genres</li>
                      <li>📺 Sélectionnez vos services de streaming</li>
                      <li>🎭 Obtenez des recommandations personnalisées</li>
                    </ul>
                  </div>
                  
                  <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:8080" 
                       style="background-color: #007bff; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                      🎬 Commencer à explorer
                    </a>
                  </div>
                  
                  <p style="color: #666; font-size: 14px;">
                    Cet email a été envoyé le {datetime.now().strftime("%d/%m/%Y à %H:%M")}.
                  </p>
                  
                  <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                  
                  <p style="color: #999; font-size: 12px; text-align: center;">
                    WhatToWatch - Votre assistant personnel pour découvrir films et séries<br>
                    Si vous n'avez pas créé ce compte, ignorez cet email.
                  </p>
                </div>
              </body>
            </html>
            """
            
            # Contenu texte simple (fallback)
            text_content = f"""
            Bienvenue sur WhatToWatch !
            
            Bonjour {user_name},
            
            Félicitations ! Votre compte a été créé avec succès.
            
            Prochaines étapes :
            - Connectez-vous avec votre email : {user_email}
            - Configurez vos préférences de genres
            - Sélectionnez vos services de streaming
            - Obtenez des recommandations personnalisées
            
            Visitez : http://localhost:8080
            
            WhatToWatch - Votre assistant personnel pour découvrir films et séries
            """
            
            # Attacher les contenus
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Envoyer l'email
            return self._send_email(message, user_email)
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'email de bienvenue: {str(e)}")
            return False
    
    def send_login_notification(self, user_email, user_name):
        """
        Envoie une notification de connexion (optionnel, pour sécurité).
        """
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Nouvelle connexion à votre compte WhatToWatch"
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = user_email
            
            html_content = f"""
            <html>
              <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                  <h1 style="color: #007bff;">🔐 Connexion détectée</h1>
                  
                  <p>Bonjour <strong>{user_name}</strong>,</p>
                  
                  <p>Une nouvelle connexion à votre compte WhatToWatch a été détectée :</p>
                  
                  <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>📅 Date :</strong> {datetime.now().strftime("%d/%m/%Y à %H:%M")}</p>
                    <p><strong>📧 Email :</strong> {user_email}</p>
                  </div>
                  
                  <p>Si cette connexion n'était pas de vous, veuillez changer votre mot de passe immédiatement.</p>
                  
                  <p style="color: #999; font-size: 12px;">
                    WhatToWatch - Sécurité de votre compte
                  </p>
                </div>
              </body>
            </html>
            """
            
            text_content = f"""
            Nouvelle connexion détectée
            
            Bonjour {user_name},
            
            Une nouvelle connexion à votre compte WhatToWatch a été détectée le {datetime.now().strftime("%d/%m/%Y à %H:%M")}.
            
            Si cette connexion n'était pas de vous, veuillez changer votre mot de passe immédiatement.
            
            WhatToWatch - Sécurité de votre compte
            """
            
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            return self._send_email(message, user_email)
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'email de connexion: {str(e)}")
            return False
    
    def _send_email(self, message, recipient_email):
        """
        Méthode privée pour envoyer un email.
        """
        try:
            # Vérifier la configuration
            if not self.sender_email or self.sender_email == 'votre-email@gmail.com':
                print("⚠️  Configuration email non configurée. Email non envoyé.")
                print("💡 Configurez SENDER_EMAIL et SENDER_PASSWORD dans vos variables d'environnement")
                return False
            
            # Connexion au serveur SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=self.context)
                server.login(self.sender_email, self.sender_password)
                
                # Envoyer l'email
                text = message.as_string()
                server.sendmail(self.sender_email, recipient_email, text)
                
            print(f"✅ Email envoyé avec succès à {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Erreur d'authentification SMTP. Vérifiez vos identifiants.")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Erreur SMTP: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de l'email: {str(e)}")
            return False
    
    def test_email_configuration(self):
        """
        Teste la configuration email.
        """
        print("🧪 Test de la configuration email...")
        print(f"📧 Serveur SMTP: {self.smtp_server}:{self.smtp_port}")
        print(f"📧 Email expéditeur: {self.sender_email}")
        
        if self.sender_email == 'votre-email@gmail.com':
            print("❌ Configuration email non configurée")
            print("💡 Instructions de configuration:")
            print("   1. Créez un mot de passe d'application Gmail")
            print("   2. Définissez les variables d'environnement:")
            print("      - SENDER_EMAIL=votre-email@gmail.com")
            print("      - SENDER_PASSWORD=votre-mot-de-passe-app")
            return False
        else:
            print("✅ Configuration email détectée")
            return True

# Instance globale du service email
email_service = EmailService()
