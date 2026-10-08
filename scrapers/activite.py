import requests
import os

APIFY_TOKEN = os.environ.get('APIFY_TOKEN', '')

def get_activities(destination):
    if APIFY_TOKEN:
        result = get_activities_apify(destination)
        if result:
            return result
    return get_activities_fallback(destination)

def get_activities_apify(destination):
    try:
        url = "https://api.apify.com/v2/acts/compass~tripadvisor-scraper/run-sync-get-dataset-items"
        params = {'token': APIFY_TOKEN}
        payload = {
            "query": f"activities attractions {destination}",
            "maxItems": 5,
            "language": "fr"
        }
        resp = requests.post(url, json=payload, params=params, timeout=60)
        if resp.status_code == 200:
            items = resp.json()
            activities = []
            for item in items[:5]:
                activities.append({
                    'name': item.get('name', 'N/A'),
                    'type': item.get('category', 'Attraction'),
                    'rating': str(item.get('rating', 'N/A'))
                })
            return activities if activities else None
    except Exception as e:
        print(f"Erreur Apify activities: {e}")
    return None

def get_activities_fallback(destination):
    dest = destination.title()
    return [
        {'name': f'Visite de la Médina de {dest}', 'type': 'Culture', 'rating': '4.7'},
        {'name': f'Musée de {dest}', 'type': 'Musée', 'rating': '4.4'},
        {'name': f'Souk de {dest}', 'type': 'Shopping', 'rating': '4.5'},
        {'name': f'Excursion Désert depuis {dest}', 'type': 'Nature', 'rating': '4.8'},
        {'name': f'Hammam Traditionnel à {dest}', 'type': 'Bien-être', 'rating': '4.6'},
    ]
