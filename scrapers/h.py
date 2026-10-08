import requests
import os

APIFY_TOKEN = os.environ.get('APIFY_TOKEN', '')  # Mettez votre token Apify ici

def get_hotels(destination):
    """Scrape hotels via Apify ou fallback"""
    if APIFY_TOKEN:
        result = get_hotels_apify(destination)
        if result:
            return result
    return get_hotels_fallback(destination)

def get_hotels_apify(destination):
    """Utilise l'API Apify pour scraper Booking.com"""
    try:
        # Démarrer l'acteur Apify Booking Scraper
        url = f"https://api.apify.com/v2/acts/voyager~booking-scraper/run-sync-get-dataset-items"
        params = {'token': APIFY_TOKEN}
        payload = {
            "search": destination,
            "maxItems": 5,
            "currency": "MAD",
            "language": "fr-fr",
        }
        resp = requests.post(url, json=payload, params=params, timeout=60)
        if resp.status_code == 200:
            items = resp.json()
            hotels = []
            for item in items[:5]:
                hotels.append({
                    'name': item.get('name', 'N/A'),
                    'price': f"{item.get('price', 'N/A')} MAD/nuit",
                    'rating': str(item.get('rating', 'N/A')),
                    'url': item.get('url', '#')
                })
            return hotels if hotels else None
    except Exception as e:
        print(f"Erreur Apify hotels: {e}")
    return None

def get_hotels_fallback(destination):
    """Données de secours si scraping échoue"""
    dest = destination.title()
    return [
        {'name': f'Hôtel Central {dest}', 'price': '450 MAD/nuit', 'rating': '4.2', 'url': '#'},
        {'name': f'Riad {dest} Authentique', 'price': '750 MAD/nuit', 'rating': '4.7', 'url': '#'},
        {'name': f'Auberge de Jeunesse {dest}', 'price': '180 MAD/nuit', 'rating': '3.9', 'url': '#'},
        {'name': f'Hôtel des Arts {dest}', 'price': '620 MAD/nuit', 'rating': '4.4', 'url': '#'},
        {'name': f'Pension Bab {dest}', 'price': '250 MAD/nuit', 'rating': '4.0', 'url': '#'},
    ]
