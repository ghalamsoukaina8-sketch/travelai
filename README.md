# TravelAI - Assistant de Voyage Intelligent

## Structure du projet
```
travelai/
├── app.py              ← Backend Flask (routes + API)
├── inter.py            ← Intégration Ollama (IA)
├── scrapers/
│   ├── h.py            ← Scraper Hôtels (Apify/fallback)
│   ├── restau.py       ← Scraper Restaurants (Apify/fallback)
│   └── activite.py     ← Scraper Activités (Apify/fallback)
├── templates/
│   ├── auth.html       ← Page Login/Register
│   ├── dashboard.html  ← Dashboard principal
│   ├── chat.html       ← Chat IA complet
│   ├── trips.html      ← Gestion des voyages
│   ├── recommendations.html ← Recommandations
│   ├── favorites.html  ← Favoris
│   └── checklist.html  ← Checklist de voyage
├── requirements.txt
└── database.json       ← Créé automatiquement
```

## Installation

```powershell
# 1. Activer le venv
.venv-1\Scripts\Activate.ps1

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
python app.py
```

## Accès
Ouvrir : http://127.0.0.1:5000

## Configuration Apify (optionnel - pour scraping réel)
Créer un compte sur https://apify.com (gratuit)
Copier votre token et définir la variable d'environnement :
```powershell
$env:APIFY_TOKEN = "votre_token_apify"
python app.py
```

## IA Ollama (optionnel)
Installer Ollama : https://ollama.com
```powershell
ollama pull llama3.2
```
Sans Ollama, l'app utilise un générateur de plan automatique.

## Fonctionnalités
- ✅ Authentification (Inscription / Connexion)
- ✅ Dashboard avec statistiques
- ✅ Chat IA pour planifier les voyages
- ✅ Gestion des voyages (CRUD)
- ✅ Système de Favoris
- ✅ Checklist de voyage
- ✅ Recommandations de destinations
- ✅ Scraping hôtels/restaurants/activités
- ✅ Base de données JSON locale

## Docker

```bash
cp .env.example .env          # puis éditer SECRET_KEY / APIFY_TOKEN
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2   # une seule fois
```
Application : http://localhost:5000

Les données (`database.json`) sont conservées dans le volume `travelai_data`.
