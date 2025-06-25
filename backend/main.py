"""
Fichier principal pour exécuter le système de recommandation de films et séries.
Inclut une fonctionnalité pour arrêter le programme avec la touche Echap.
"""

import keyboard
import threading
import sys
import time
from src.user_interface import main
from src.recommendation_engine import check_api_key

def check_exit_key():
    """
    Fonction qui vérifie en continu si la touche Echap a été pressée.
    Si c'est le cas, elle arrête le programme.
    """
    print("\nAppuyez sur la touche 'Echap' à tout moment pour quitter le programme.")
    
    while True:
        try:
            if keyboard.is_pressed('esc'):
                print("\n\nArrêt du programme à la demande de l'utilisateur. Au revoir!")
                sys.exit(0)
            time.sleep(0.1)  # Pause pour éviter d'utiliser trop de CPU
        except Exception:
            # Ignorer les erreurs potentielles
            pass

if __name__ == "__main__":
    # Lancer la vérification de la touche d'arrêt dans un thread séparé
    exit_thread = threading.Thread(target=check_exit_key, daemon=True)
    exit_thread.start()
      # Exécuter le programme principal
    try:
        # La clé API est maintenant gérée par l'administrateur
        main()
    except KeyboardInterrupt:
        print("\n\nProgramme arrêté par l'utilisateur. Au revoir!")
    except Exception as e:
        print(f"\n\nUne erreur est survenue: {e}")
    finally:
        # Assurer que le programme se termine proprement
        sys.exit(0)
