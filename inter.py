import ollama

SYSTEM_PROMPT = """Tu es TravelAI, un expert planificateur de voyage.
Quand on te donne une destination, un budget, le nombre de personnes,
la durée et des données réelles (hôtels, restaurants, activités),
tu génères un plan de voyage détaillé jour par jour avec :
- Hébergement recommandé avec prix réel
- Restaurants recommandés par jour avec prix
- Activités touristiques avec prix
- Répartition du budget total
Réponds toujours en français de manière structurée et claire."""

def generate_plan(destination, budget, membres, duree, hotels, restaurants, activities):
    hotels_text = "\n".join([f"- {h['name']} : {h['price']}" for h in hotels]) if hotels else "Aucun hôtel trouvé"
    restaurants_text = "\n".join([f"- {r['name']} : {r['rating']} étoiles" for r in restaurants]) if restaurants else "Aucun restaurant trouvé"
    activities_text = "\n".join([f"- {a['name']}" for a in activities]) if activities else "Aucune activité trouvée"

    message = f"""
Planifie un voyage avec ces informations :
- Destination : {destination}
- Budget total : {budget} MAD
- Nombre de personnes : {membres}
- Durée : {duree} jours

Hôtels disponibles :
{hotels_text}

Restaurants disponibles :
{restaurants_text}

Activités disponibles :
{activities_text}

Génère un plan complet jour par jour en utilisant ces données réelles.
"""

    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': message}
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Erreur Ollama: {e}")
        return generate_plan_fallback(destination, budget, membres, duree, hotels, restaurants, activities)

def generate_plan_fallback(destination, budget, membres, duree, hotels, restaurants, activities):
    """Plan de secours si Ollama n'est pas disponible"""
    hotel = hotels[0] if hotels else {'name': f'Hôtel {destination}', 'price': '500 MAD/nuit'}
    rest = [r['name'] for r in restaurants[:2]] if restaurants else [f'Restaurant local à {destination}']
    acts = [a['name'] for a in activities[:3]] if activities else [f'Visite de {destination}']
    
    plan = f"""🗺️ Plan de voyage pour {destination} - {duree} jours

📍 HÉBERGEMENT RECOMMANDÉ
{hotel['name']} — {hotel['price']}

"""
    budget_int = int(str(budget).replace(' ', '').replace(',', '.').split('.')[0]) if budget else 1000
    per_day = budget_int // int(duree) if duree else budget_int
    
    for day in range(1, int(duree) + 1):
        plan += f"""
📅 JOUR {day}
🌅 Matin : Petit-déjeuner à l'hôtel, puis {acts[(day-1) % len(acts)]}
🍽️ Déjeuner : {rest[(day-1) % len(rest)]}
🌇 Après-midi : Exploration libre de {destination}
🍷 Dîner : Restaurant local (budget ~{per_day // 4} MAD)
"""
    
    plan += f"""
💰 RÉPARTITION DU BUDGET ({budget} MAD pour {membres} personne(s))
- Hébergement ({duree} nuits) : {int(duree) * int(hotel['price'].split()[0]) if hotel['price'][0].isdigit() else budget_int // 3} MAD
- Restaurants : {budget_int // 3} MAD
- Activités : {budget_int // 4} MAD
- Transport : {budget_int // 6} MAD
- Divers : {budget_int // 8} MAD

✅ Bon voyage à {destination} !
"""
    return plan
