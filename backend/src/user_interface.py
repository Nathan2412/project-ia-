"""
Interface utilisateur pour le système de recommandation.
Ce fichier contient l'interface en ligne de commande pour interagir avec le système de recommandation.
"""

import sys
import os

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommendation_engine import (
    get_recommendations, create_user_profile, update_user_history,
    get_online_genres, configure_api_key
)
# Importer la nouvelle base de données utilisateurs
from data.user_database import load_users, save_users, add_user, update_user
from data.movies_series_database import STREAMING_SERVICES

# Charger les utilisateurs depuis la base de données au démarrage
users = load_users()

def display_welcome():
    """Affiche un message de bienvenue."""
    print("\n" + "=" * 60)
    print("  SYSTÈME DE RECOMMANDATION DE FILMS ET SÉRIES")
    print("=" * 60)
    print("Ce système vous aide à trouver des films et séries adaptés à vos goûts.")


def display_main_menu():
    """Affiche le menu principal."""
    print("\nMENU PRINCIPAL:")
    print("1. Se connecter avec un profil existant")
    print("2. Créer un nouveau profil")
    # Cette option n'est plus nécessaire avec la gestion centralisée de l'API
    # print("3. Configurer la clé API TMDb")
    print("3. Quitter")
    print("0. Quitter immédiatement")
    return input("\nVotre choix (0-3): ")

def display_user_menu(user):
    """Affiche le menu utilisateur."""
    print(f"\nBienvenue, {user['name']}!")
    print("\nMENU UTILISATEUR:")
    print("1. Rechercher des films recommandés")
    print("2. Rechercher des séries recommandées")
    print("3. Rechercher des films et séries recommandés")
    print("4. Rechercher par service de streaming")
    print("5. Mettre à jour mes préférences")
    print("6. Voir mon profil")
    # Cette option n'est plus nécessaire avec la gestion centralisée de l'API
    # print("7. Configurer la clé API TMDb")
    print("7. Retour au menu principal")
    print("0. Quitter immédiatement")
    return input("\nVotre choix (0-7): ")

def select_user():
    """Permet à l'utilisateur de sélectionner un profil existant."""
    if not users:
        print("\nAucun profil utilisateur disponible.")
        return None
    
    print("\nPROFILS DISPONIBLES:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['name']}")
    
    try:
        choice = int(input("\nSélectionnez un profil (numéro): "))
        if 1 <= choice <= len(users):
            return users[choice - 1]
        else:
            print("Choix invalide.")
            return None
    except ValueError:
        print("Veuillez entrer un nombre valide.")
        return None

def create_new_profile():
    """Crée un nouveau profil utilisateur."""
    print("\nCRÉATION D'UN NOUVEAU PROFIL")
    name = input("Nom: ")
    
    # Récupération des genres depuis TMDb
    print("\nRécupération des genres depuis TMDb...")
    try:
        genres = get_online_genres()
    except Exception as e:
        print(f"Erreur lors de la récupération des genres en ligne: {e}")
        print("Utilisant des genres par défaut.")
        genres = ["Action", "Aventure", "Animation", "Comédie", "Crime", "Documentaire", "Drame", "Famille", "Fantaisie", 
                 "Histoire", "Horreur", "Musique", "Mystère", "Romance", "Science-Fiction", "Téléfilm", "Thriller", "Guerre", "Western"]
    
    # Sélection des genres préférés
    print("\nGenres disponibles:")
    for i, genre in enumerate(genres, 1):
        print(f"{i}. {genre}")
    
    genres_likes_input = input("\nEntrez les numéros des genres que vous aimez (séparés par des espaces): ")
    genres_likes = [genres[int(i) - 1] for i in genres_likes_input.split() if i.isdigit() and 1 <= int(i) <= len(genres)]
    
    genres_dislikes_input = input("Entrez les numéros des genres que vous n'aimez pas (séparés par des espaces): ")
    genres_dislikes = [genres[int(i) - 1] for i in genres_dislikes_input.split() if i.isdigit() and 1 <= int(i) <= len(genres)]
    
    # Mots clés d'intérêt
    keywords = input("\nEntrez quelques mots-clés d'intérêt (séparés par des virgules): ")
    keywords_likes = [k.strip() for k in keywords.split(",") if k.strip()]
    
    # Note minimale
    rating_min = 0
    while rating_min < 1 or rating_min > 10:
        try:
            rating_min = float(input("\nNote minimale pour les recommandations (1-10): "))
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    # Réalisateurs/créateurs préférés
    directors = input("\nEntrez les noms des réalisateurs/créateurs que vous appréciez (séparés par des virgules): ")
    directors_likes = [d.strip() for d in directors.split(",") if d.strip()]
    
    # Services de streaming
    from data.movies_series_database import STREAMING_SERVICES
    
    print("\nServices de streaming disponibles:")
    for i, service in enumerate(STREAMING_SERVICES, 1):
        print(f"{i}. {service.capitalize()}")
    
    print("\nAuxquels de ces services êtes-vous abonné(e)?")
    streaming_input = input("Entrez les numéros des services (séparés par des espaces): ")
    streaming_services = [STREAMING_SERVICES[int(i) - 1] for i in streaming_input.split() 
                         if i.isdigit() and 1 <= int(i) <= len(STREAMING_SERVICES)]
      # Création du profil
    new_user = create_user_profile(
        name=name,
        genres_likes=genres_likes,
        genres_dislikes=genres_dislikes,
        directors_likes=directors_likes,
        keywords_likes=keywords_likes,
        mood_preferences=[],  # Les ambiances ne sont pas utilisées en mode en ligne
        rating_min=rating_min,
        streaming_services=streaming_services
    )
    
    # Ajouter l'utilisateur à la base de données persistante
    updated_user = add_user(new_user)
    
    print(f"\nProfil '{name}' créé avec succès et sauvegardé dans la base de données!")
    return updated_user

def display_recommendations(recommendations, user=None):
    """Affiche les recommandations à l'utilisateur."""
    if not recommendations:
        print("\nDésolé, aucune recommandation n'a été trouvée pour vos préférences.")
        return
    
    print("\nVOICI VOS RECOMMANDATIONS:")
    print("-" * 60)
    
    for i, rec in enumerate(recommendations, 1):
        item = rec['item']
        item_type = "Film" if rec['type'] == 'movie' else "Série"
        year = item.get('year', '')
        director = item.get('director', item.get('creator', 'N/A'))
        genres = ", ".join(item.get('genre', []))
        streaming = ", ".join(rec.get('streaming_services', []))
        
        print(f"{i}. {item['title']} ({year}) - {item_type}")
        print(f"   Genre: {genres}")
        print(f"   Réalisateur/Créateur: {director}")
        print(f"   Note: {item.get('rating', 'N/A')}/10")
        print(f"   Synopsis: {item.get('plot', 'N/A')}")
        print(f"   Score de compatibilité: {rec['score']:.2f}")
        print(f"   Disponible sur: {streaming if streaming else 'Aucune information'}")
        
        # Afficher l'URL de l'image si disponible
        if 'poster_path' in item and item['poster_path']:
            print(f"   Affiche: https://image.tmdb.org/t/p/w500{item['poster_path']}")
            
        print("-" * 60)
    
    # Permettre à l'utilisateur de sélectionner un film/série pour l'ajouter à son historique
    if user and recommendations:
        print("\nVoulez-vous marquer un des titres comme vu? Cela l'ajoutera à votre historique.")
        print("Entrez le numéro du titre ou 0 pour ne rien sélectionner.")
        
        try:
            selection = int(input("Votre choix: "))
            if 1 <= selection <= len(recommendations):
                selected_item = recommendations[selection-1]
                item_id = selected_item['item']['id']
                
                if update_user_history(user['id'], item_id):
                    print(f"\n✅ '{selected_item['item']['title']}' a été ajouté à votre historique.")
                    print("Ce titre n'apparaîtra plus dans vos recommandations futures.")
                else:
                    print("\n❌ Erreur lors de la mise à jour de l'historique.")
        except ValueError:
            pass  # Ignore les entrées non numériques

def update_preferences(user):
    """Permet à l'utilisateur de mettre à jour ses préférences."""
    print("\nMISE À JOUR DES PRÉFÉRENCES")
    print("1. Ajouter/Modifier les genres aimés")
    print("2. Ajouter/Modifier les genres non aimés")
    print("3. Ajouter/Modifier les mots-clés d'intérêt")
    print("4. Modifier la note minimale")
    print("5. Ajouter/Modifier les réalisateurs/créateurs préférés")
    print("6. Mettre à jour mes abonnements streaming")
    print("7. Retour")
    print("0. Quitter immédiatement")
    
    choice = input("\nVotre choix (0-7): ")
    
    if choice == "0":
        # Quitter immédiatement
        print("\nAu revoir!")
        import sys
        sys.exit(0)
    
    if choice == "1":
        # Genres aimés
        print("\nRécupération des genres depuis TMDb...")
        try:
            genres = get_online_genres()
        except Exception as e:
            print(f"Erreur lors de la récupération des genres en ligne: {e}")
            print("Utilisant des genres par défaut.")
            genres = ["Action", "Aventure", "Animation", "Comédie", "Crime", "Documentaire", "Drame", "Famille", "Fantaisie", 
                     "Histoire", "Horreur", "Musique", "Mystère", "Romance", "Science-Fiction", "Téléfilm", "Thriller", "Guerre", "Western"]
        
        print("\nGenres disponibles:")
        for i, genre in enumerate(genres, 1):
            print(f"{i}. {genre}")
        
        genres_input = input("\nEntrez les numéros des genres que vous aimez (séparés par des espaces): ")
        user['preferences']['genres_likes'] = [genres[int(i) - 1] for i in genres_input.split() if i.isdigit() and 1 <= int(i) <= len(genres)]
        print("Genres aimés mis à jour!")
    
    elif choice == "2":
        # Genres non aimés
        print("\nRécupération des genres depuis TMDb...")
        try:
            genres = get_online_genres()
        except Exception as e:
            print(f"Erreur lors de la récupération des genres en ligne: {e}")
            print("Utilisant des genres par défaut.")
            genres = ["Action", "Aventure", "Animation", "Comédie", "Crime", "Documentaire", "Drame", "Famille", "Fantaisie", 
                     "Histoire", "Horreur", "Musique", "Mystère", "Romance", "Science-Fiction", "Téléfilm", "Thriller", "Guerre", "Western"]
        
        print("\nGenres disponibles:")
        for i, genre in enumerate(genres, 1):
            print(f"{i}. {genre}")
        
        genres_input = input("\nEntrez les numéros des genres que vous n'aimez pas (séparés par des espaces): ")
        user['preferences']['genres_dislikes'] = [genres[int(i) - 1] for i in genres_input.split() if i.isdigit() and 1 <= int(i) <= len(genres)]
        print("Genres non aimés mis à jour!")
    
    elif choice == "3":
        # Mots-clés
        keywords = input("\nEntrez quelques mots-clés d'intérêt (séparés par des virgules): ")
        user['preferences']['keywords_likes'] = [k.strip() for k in keywords.split(",") if k.strip()]
        print("Mots-clés mis à jour!")
    
    elif choice == "4":
        # Note minimale
        try:
            rating_min = float(input("\nNote minimale pour les recommandations (1-10): "))
            if 1 <= rating_min <= 10:
                user['preferences']['rating_min'] = rating_min
                print("Note minimale mise à jour!")
            else:
                print("La note doit être entre 1 et 10.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    elif choice == "5":
        # Réalisateurs/créateurs
        directors = input("\nEntrez les noms des réalisateurs/créateurs que vous appréciez (séparés par des virgules): ")
        user['preferences']['directors_likes'] = [d.strip() for d in directors.split(",") if d.strip()]
        print("Réalisateurs/créateurs préférés mis à jour!")
    
    elif choice == "6":
        # Abonnements streaming
        from data.movies_series_database import STREAMING_SERVICES
        
        print("\nServices de streaming disponibles:")
        for i, service in enumerate(STREAMING_SERVICES, 1):
            print(f"{i}. {service.capitalize()}")
        
        print("\nAuxquels de ces services êtes-vous abonné(e)?")
        streaming_input = input("Entrez les numéros des services (séparés par des espaces): ")
        user['preferences']['streaming_services'] = [STREAMING_SERVICES[int(i) - 1] for i in streaming_input.split() 
                         if i.isdigit() and 1 <= int(i) <= len(STREAMING_SERVICES)]
        print("Abonnements streaming mis à jour!")
    
    # Sauvegarder les changements dans la base de données
    if choice in ["1", "2", "3", "4", "5", "6"]:
        if update_user(user):
            print("Profil sauvegardé dans la base de données!")
        else:
            print("Erreur lors de la sauvegarde du profil.")

def display_profile(user):
    """Affiche le profil complet de l'utilisateur."""
    print("\nVOTRE PROFIL:")
    print(f"Nom: {user['name']}")
    
    preferences = user['preferences']
    print("\nPréférences:")
    print(f"Genres aimés: {', '.join(preferences.get('genres_likes', ['Aucun']))}")
    print(f"Genres non aimés: {', '.join(preferences.get('genres_dislikes', ['Aucun']))}")
    print(f"Réalisateurs/Créateurs favoris: {', '.join(preferences.get('directors_likes', ['Aucun']))}")
    print(f"Mots-clés d'intérêt: {', '.join(preferences.get('keywords_likes', ['Aucun']))}")
    print(f"Note minimale: {preferences.get('rating_min', 'Non définie')}")
    
    # Afficher les services de streaming
    streaming_services = preferences.get('streaming_services', [])
    if streaming_services:
        print(f"Abonnements streaming: {', '.join(s.capitalize() for s in streaming_services)}")
    else:
        print("Abonnements streaming: Aucun")

def select_streaming_service(user=None):
    """
    Permet à l'utilisateur de sélectionner un service de streaming.
    
    Args:
        user: Profil utilisateur (optionnel)
    
    Returns:
        Le service de streaming sélectionné ou None pour tous les services
    """
    from data.movies_series_database import STREAMING_SERVICES
    
    print("\nSERVICES DE STREAMING DISPONIBLES:")
    
    # Mettre en évidence les services auxquels l'utilisateur est abonné
    user_services = []
    if user and 'preferences' in user:
        user_services = user['preferences'].get('streaming_services', [])
        if user_services:
            print("(✓ = vos abonnements)")
    
    for i, service in enumerate(STREAMING_SERVICES, 1):
        indicator = "✓ " if service in user_services else "  "
        print(f"{i}. {indicator}{service.capitalize()}")
    
    print(f"{len(STREAMING_SERVICES) + 1}. Tous les services")
    print("0. Quitter immédiatement")
    
    choice = input(f"\nChoisissez un service (0-{len(STREAMING_SERVICES) + 1}): ")
    
    if choice == "0":
        # Quitter immédiatement
        print("\nAu revoir!")
        import sys
        sys.exit(0)
    elif choice.isdigit() and 1 <= int(choice) <= len(STREAMING_SERVICES):
        selected_service = STREAMING_SERVICES[int(choice) - 1]
        return selected_service
    else:
        return None  # Tous les services

def main():
    """Fonction principale du programme."""
    display_welcome()
    
    while True:
        choice = display_main_menu()
        
        if choice == "0":
            # Quitter immédiatement
            print("\nAu revoir!")
            import sys
            sys.exit(0)
        
        elif choice == "1":
            # Se connecter avec un profil existant
            user = select_user()
            if user:
                handle_user_menu(user)
        
        elif choice == "2":
            # Créer un nouveau profil
            user = create_new_profile()
            if user:
                handle_user_menu(user)
        
        elif choice == "3":
            # Configurer la clé API TMDb
            configure_api_key()
        
        elif choice == "4":
            # Quitter
            print("\nMerci d'avoir utilisé notre système de recommandation. Au revoir!")
            break
        
        else:
            print("\nChoix invalide. Veuillez réessayer.")

def handle_user_menu(user):
    """Gère le menu utilisateur."""
    import sys

    while True:
        choice = display_user_menu(user)

        if choice == "0":
            # Quitter immédiatement
            print("\nAu revoir!")
            sys.exit(0)

        elif choice == "1":
            # Recherche de films en ligne            print("\nRecherche en ligne de films recommandés...")
            n = input("Nombre de recommandations (défaut: 5): ")
            try:
                n = int(n)
            except ValueError:
                n = 5
                
            print("\nRecherche en cours sur Internet, veuillez patienter...")
            recommendations = get_recommendations(user['id'], n=n, content_type='movies')
            display_recommendations(recommendations, user)

        elif choice == "2":
            # Recherche de séries en ligne
            print("\nRecherche en ligne de séries recommandées...")
            n = input("Nombre de recommandations (défaut: 5): ")
            try:
                n = int(n)
            except ValueError:
                n = 5
                
            print("\nRecherche en cours sur Internet, veuillez patienter...")
            recommendations = get_recommendations(user['id'], n=n, content_type='series')
            display_recommendations(recommendations, user)

        elif choice == "3":
            # Recherche de films et séries en ligne
            print("\nRecherche en ligne de films et séries recommandés...")
            n = input("Nombre de recommandations (défaut: 5): ")
            try:
                n = int(n)
            except ValueError:
                n = 5
                
            print("\nRecherche en cours sur Internet, veuillez patienter...")
            recommendations = get_recommendations(user['id'], n=n, content_type='all')
            display_recommendations(recommendations, user)

        elif choice == "4":
            # Recherche par service de streaming
            service = select_streaming_service(user)
            content_type = input("\nType de contenu (1: Films, 2: Séries, 3: Les deux): ")

            if content_type == "1":
                content = "movies"
            elif content_type == "2":
                content = "series"
            else:
                content = "all"

            n = input("Nombre de recommandations (défaut: 5): ")
            try:
                n = int(n)
            except ValueError:
                n = 5
                
            if service:
                print(f"\nRecherche en ligne de recommandations sur {service.capitalize()}, veuillez patienter...")
                recommendations = get_recommendations(user['id'], n=n, content_type=content, streaming_service=service)
            else:
                print("\nRecherche en ligne de recommandations sur tous les services, veuillez patienter...")
                recommendations = get_recommendations(user['id'], n=n, content_type=content)

            display_recommendations(recommendations, user)

        elif choice == "5":
            # Mettre à jour les préférences
            update_preferences(user)

        elif choice == "6":
            # Voir le profil
            display_profile(user)

        elif choice == "7":
            # Retour au menu principal
            break

        else:
            print("\nChoix invalide. Veuillez réessayer.")


def configure_api_key():
    """Cette fonction est conservée pour compatibilité mais n'est plus utilisée avec la gestion centralisée de l'API."""
    print("\nCONFIGURATION DE LA CLÉ API TMDb")
    print("✅ La clé API est déjà configurée par l'administrateur du système.")
    print("Vous n'avez pas besoin de fournir votre propre clé API.")
    return

if __name__ == "__main__":
    main()
