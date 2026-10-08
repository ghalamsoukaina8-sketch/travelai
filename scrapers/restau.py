import requests
import os

APIFY_TOKEN = os.environ.get('APIFY_TOKEN', '')

def get_restaurants(destination):
    if APIFY_TOKEN:
        result = get_restaurants_apify(destination)
        if result:
            return result
    return get_restaurants_fallback(destination)

def get_restaurants_apify(destination):
    try:
        url = "https://api.apify.com/v2/acts/compass~tripadvisor-scraper/run-sync-get-dataset-items"
        params = {'token': APIFY_TOKEN}
        payload = {
            "query": f"restaurants {destination}",
            "maxItems": 5,
            "language": "fr"
        }
        resp = requests.post(url, json=payload, params=params, timeout=60)
        if resp.status_code == 200:
            items = resp.json()
            restaurants = []
            for item in items[:5]:
                restaurants.append({
                    'name': item.get('name', 'N/A'),
                    'rating': str(item.get('rating', 'N/A')),
                    'cuisine': item.get('cuisine', 'Local'),
                    'price_range': item.get('priceRange', '$$')
                })
            return restaurants if restaurants else None
    except Exception as e:
        print(f"Erreur Apify restaurants: {e}")
    return None

def get_restaurants_fallback(destination):
    dest = destination.title()
    return [
        {'name': f'Al Fassia {dest}', 'rating': '4.5', 'cuisine': 'Marocain', 'price_range': '$$'},
        {'name': f'Café Central {dest}', 'rating': '4.2', 'cuisine': 'International', 'price_range': '$'},
        {'name': f'Restaurant Dar {dest}', 'rating': '4.6', 'cuisine': 'Traditionnel', 'price_range': '$$$'},
        {'name': f'Le Comptoir {dest}', 'rating': '4.0', 'cuisine': 'Fusion', 'price_range': '$$'},
        {'name': f'Souk Food {dest}', 'rating': '4.3', 'cuisine': 'Street Food', 'price_range': '$'},
    ]
