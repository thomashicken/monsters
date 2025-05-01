from flask import Flask, jsonify, request, g, make_response
from database import Database
from passlib.hash import bcrypt
from session_store import SessionStore

app = Flask(__name__)
db = Database("monsters.db")
session_store = SessionStore()

@app.after_request
def apply_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route("/monsters", methods=["GET"])
def get_monsters():
    if not load_session():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(db.read_all_records()), 200

@app.route("/monsters/<int:monster_id>", methods=["GET"])
def get_monster(monster_id):
    return jsonify(db.get_record_by_id(monster_id) or {}), 200

@app.route("/monsters", methods=["POST"])
def add_monster():
    if not load_session():
        return jsonify({"error": "Unauthorized"}), 401
    monster = request.json
    monster_id = db.save_record(monster)
    return jsonify({"id": monster_id}), 201

@app.route("/monsters/<int:monster_id>", methods=["PUT"])
def update_monster(monster_id):
    if not load_session():
        return jsonify({"error": "Unauthorized"}), 401
    db.update_record(monster_id, request.json)
    return jsonify({"message": "Updated"}), 200

@app.route("/monsters/<int:monster_id>", methods=["DELETE"])
def delete_monster(monster_id):
    if not load_session():
        return jsonify({"error": "Unauthorized"}), 401
    db.delete_record(monster_id)
    return jsonify({"message": "Deleted"}), 200

@app.route("/monsters", methods=["OPTIONS"])
def handle_options():
    response = make_response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response, 200

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    required = ["first_name", "last_name", "email", "password"]
    
    if not all(data.get(field) and data.get(field).strip() for field in required):
        return jsonify({"error": "All fields must be filled out"}), 400

    existing = db.cursor.execute("SELECT id FROM users WHERE email = ?", (data["email"],)).fetchone()
    if existing:
        return jsonify({"error": "Email already in use"}), 400

    password_hash = bcrypt.hash(data["password"])
    db.cursor.execute('''
        INSERT INTO users (first_name, last_name, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (data["first_name"], data["last_name"], data["email"], password_hash))
    db.conn.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = db.cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user is None or not bcrypt.verify(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password"}), 401

    session_id = session_store.create_session()
    session_data = session_store.get_session_data(session_id)

    # Store user data in session
    session_data["user"] = {
        "id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "dark_mode": bool(user["dark_mode"])
    }

    # Store preferences (starts with DB value)
    session_data["preferences"] = {
        "dark_mode": bool(user["dark_mode"])
    }

    return jsonify({
        "message": "Login successful",
        "session_id": session_id,
        "user": {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "dark_mode": bool(user["dark_mode"])
        }
    })

def load_session():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        session_id = auth_header[len("Bearer "):]
        session_data = session_store.get_session_data(session_id)
        if session_data and "user" in session_data:
            g.session_id = session_id
            g.session_data = session_data
            return True
    return False

@app.route("/toggle-dark-mode", methods=["POST"])
def toggle_dark_mode():
    if not load_session():
        return jsonify({"error": "Unauthorized"}), 401

    prefs = g.session_data.setdefault("preferences", {})
    prefs["dark_mode"] = not prefs.get("dark_mode", g.session_data["user"].get("dark_mode", False))
    
    g.session_data["user"]["dark_mode"] = prefs["dark_mode"]

    # Persist to DB
    db.cursor.execute("UPDATE users SET dark_mode = ? WHERE id = ?", (int(prefs["dark_mode"]), g.session_data["user"]["id"]))
    db.conn.commit()

    return jsonify({"dark_mode": prefs["dark_mode"]})

def run():
    app.run(port=8080, host='0.0.0.0')

if __name__ == '__main__':
    run()