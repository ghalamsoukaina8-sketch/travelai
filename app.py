from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json, os, hashlib, uuid
from datetime import datetime
from inter import generate_plan
from scrapers.h import get_hotels
from scrapers.restau import get_restaurants
from scrapers.activite import get_activities

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-change-me')

DB_FILE = os.environ.get('DB_FILE', 'database.json')

def load_db():
    if not os.path.exists(DB_FILE):
        return {'users': [], 'trips': [], 'favorites': [], 'checklist': []}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user():
    if 'user_id' not in session:
        return None
    db = load_db()
    return next((u for u in db['users'] if u['id'] == session['user_id']), None)

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if get_user():
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth.html')
    data = request.json
    db = load_db()
    user = next((u for u in db['users']
                 if u['email'] == data['email']
                 and u['password'] == hash_password(data['password'])), None)
    if not user:
        return jsonify({'success': False, 'message': 'Email ou mot de passe incorrect'}), 401
    session['user_id'] = user['id']
    return jsonify({'success': True})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    db = load_db()
    if any(u['email'] == data['email'] for u in db['users']):
        return jsonify({'success': False, 'message': 'Email déjà utilisé'}), 400
    user = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'email': data['email'],
        'password': hash_password(data['password']),
        'created_at': datetime.now().isoformat()
    }
    db['users'].append(user)
    save_db(db)
    session['user_id'] = user['id']
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── PAGES ─────────────────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    if not get_user():
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/chat')
def chat():
    if not get_user():
        return redirect(url_for('login'))
    return render_template('chat.html')

@app.route('/trips')
def trips():
    if not get_user():
        return redirect(url_for('login'))
    return render_template('trips.html')

@app.route('/recommendations')
def recommendations():
    if not get_user():
        return redirect(url_for('login'))
    return render_template('recommendations.html')

@app.route('/favorites')
def favorites():
    if not get_user():
        return redirect(url_for('login'))
    return render_template('favorites.html')

@app.route('/checklist')
def checklist():
    if not get_user():
        return redirect(url_for('login'))
    return render_template('checklist.html')

# ── API ───────────────────────────────────────────────────────────────────────

@app.route('/api/user')
def api_user():
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    return jsonify({'name': user['name'], 'email': user['email']})

@app.route('/api/planifier', methods=['POST'])
def planifier():
    if not get_user():
        return jsonify({'error': 'Non authentifié'}), 401
    data = request.json
    destination = data.get('destination', '')
    budget = data.get('budget', '1000')
    membres = data.get('membres', '1')
    duree = data.get('duree', '5')

    hotels = get_hotels(destination)
    restaurants = get_restaurants(destination)
    activities = get_activities(destination)
    plan = generate_plan(destination, budget, membres, duree, hotels, restaurants, activities)

    return jsonify({'plan': plan, 'hotels': hotels, 'restaurants': restaurants, 'activities': activities})

# Trips API
@app.route('/api/trips', methods=['GET'])
def get_trips():
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    db = load_db()
    user_trips = [t for t in db['trips'] if t['user_id'] == user['id']]
    return jsonify(user_trips)

@app.route('/api/trips', methods=['POST'])
def add_trip():
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    data = request.json
    db = load_db()
    trip = {
        'id': str(uuid.uuid4()),
        'user_id': user['id'],
        'destination': data.get('destination'),
        'date_start': data.get('date_start'),
        'date_end': data.get('date_end'),
        'budget': data.get('budget'),
        'type': data.get('type', 'Solo'),
        'status': 'planned',
        'created_at': datetime.now().isoformat()
    }
    db['trips'].append(trip)
    save_db(db)
    return jsonify(trip)

@app.route('/api/trips/<trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    db = load_db()
    db['trips'] = [t for t in db['trips'] if not (t['id'] == trip_id and t['user_id'] == user['id'])]
    save_db(db)
    return jsonify({'success': True})

# Favorites API
@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    db = load_db()
    return jsonify([f for f in db['favorites'] if f['user_id'] == user['id']])

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    data = request.json
    db = load_db()
    fav = {
        'id': str(uuid.uuid4()),
        'user_id': user['id'],
        'name': data.get('name'),
        'type': data.get('type', 'destination'),
        'info': data.get('info', ''),
        'created_at': datetime.now().isoformat()
    }
    db['favorites'].append(fav)
    save_db(db)
    return jsonify(fav)

@app.route('/api/favorites/<fav_id>', methods=['DELETE'])
def delete_favorite(fav_id):
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    db = load_db()
    db['favorites'] = [f for f in db['favorites'] if not (f['id'] == fav_id and f['user_id'] == user['id'])]
    save_db(db)
    return jsonify({'success': True})

# Checklist API
@app.route('/api/checklist', methods=['GET'])
def get_checklist():
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    trip_id = request.args.get('trip_id', 'default')
    db = load_db()
    items = [c for c in db['checklist'] if c['user_id'] == user['id'] and c.get('trip_id') == trip_id]
    return jsonify(items)

@app.route('/api/checklist', methods=['POST'])
def add_checklist():
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    data = request.json
    db = load_db()
    item = {
        'id': str(uuid.uuid4()),
        'user_id': user['id'],
        'trip_id': data.get('trip_id', 'default'),
        'task': data.get('task'),
        'category': data.get('category', 'Général'),
        'priority': data.get('priority', 'normal'),
        'completed': False,
        'created_at': datetime.now().isoformat()
    }
    db['checklist'].append(item)
    save_db(db)
    return jsonify(item)

@app.route('/api/checklist/<item_id>', methods=['PATCH'])
def update_checklist(item_id):
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    data = request.json
    db = load_db()
    for item in db['checklist']:
        if item['id'] == item_id and item['user_id'] == user['id']:
            item.update(data)
            break
    save_db(db)
    return jsonify({'success': True})

@app.route('/api/checklist/<item_id>', methods=['DELETE'])
def delete_checklist(item_id):
    user = get_user()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    db = load_db()
    db['checklist'] = [c for c in db['checklist'] if not (c['id'] == item_id and c['user_id'] == user['id'])]
    save_db(db)
    return jsonify({'success': True})

# Scraping API
@app.route('/api/scrape', methods=['POST'])
def scrape():
    if not get_user():
        return jsonify({'error': 'Non authentifié'}), 401
    data = request.json
    destination = data.get('destination', '')
    hotels = get_hotels(destination)
    restaurants = get_restaurants(destination)
    activities = get_activities(destination)
    return jsonify({'hotels': hotels, 'restaurants': restaurants, 'activities': activities})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)),
            debug=os.environ.get('FLASK_DEBUG', '0') == '1')
