#!/usr/bin/env python3
"""
Test minimal pour diagnostiquer les imports
"""
import sys
import os

print("🔍 Diagnostic des imports...")
print(f"Python version: {sys.version}")
print(f"Répertoire actuel: {os.getcwd()}")

# Test 1: Ajouter le path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
print("✅ Path ajouté")

# Test 2: Vérifier les fichiers
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
print(f"Backend path: {backend_path}")
print(f"Backend existe: {os.path.exists(backend_path)}")

if os.path.exists(backend_path):
    files = os.listdir(backend_path)
    print(f"Fichiers dans backend: {files[:10]}...")

# Test 3: Import de base
try:
    import json
    print("✅ Import json OK")
except Exception as e:
    print(f"❌ Import json: {e}")

# Test 4: Import des données utilisateur
try:
    from data.user_database import load_users
    print("✅ Import user_database OK")
    users = load_users()
    print(f"✅ Utilisateurs chargés: {len(users)}")
except Exception as e:
    print(f"❌ Import user_database: {e}")

# Test 5: Import du config
try:
    from config import TMDB_API_KEY
    print("✅ Import config OK")
    print(f"TMDB key présente: {'Oui' if TMDB_API_KEY else 'Non'}")
except Exception as e:
    print(f"❌ Import config: {e}")

# Test 6: Import API manager
try:
    from src.api_providers.multi_api_manager import MultiAPIManager
    print("✅ Import MultiAPIManager OK")
except Exception as e:
    print(f"❌ Import MultiAPIManager: {e}")

print("\n🏁 Diagnostic terminé!")
