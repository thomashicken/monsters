# Monster Tracker

## Overview
The **Monster Tracker** API allows users to track monsters they’ve slain in fantasy role-playing games. The app supports user authentication, dark mode preferences, and CRUD operations for monster records.

---

## Resources and Attributes

### Monsters
Each monster has the following attributes:

| Attribute    | Type     | Description |
|--------------|----------|-------------|
| `id`         | INTEGER  | Unique identifier (Primary Key) |
| `name`       | TEXT     | Name of the monster (Required) |
| `description`| TEXT     | Optional short description |
| `type`       | TEXT     | Classification (e.g., Dragon, Undead) |
| `strength`   | INTEGER  | Combat power level |
| `weakness`   | TEXT     | Primary weakness |

### Users
Each user has:

| Attribute      | Type     | Description |
|----------------|----------|-------------|
| `id`           | INTEGER  | Unique identifier (Primary Key) |
| `first_name`   | TEXT     | First name |
| `last_name`    | TEXT     | Last name |
| `email`        | TEXT     | Email address (Unique) |
| `password_hash`| TEXT     | Hashed password |
| `dark_mode`    | BOOLEAN  | Whether user prefers dark mode |

---

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS monsters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT,
    strength INTEGER,
    weakness TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    dark_mode BOOLEAN DEFAULT 0
);
```

---

## REST Endpoints

### Monster Endpoints

| Method | Path                 | Description                   |
|--------|----------------------|-------------------------------|
| GET    | `/monsters`          | Get all monsters              |
| GET    | `/monsters/<id>`     | Get monster by ID             |
| POST   | `/monsters`          | Add a new monster             |
| PUT    | `/monsters/<id>`     | Update an existing monster    |
| DELETE | `/monsters/<id>`     | Delete a monster              |
| OPTIONS| `/monsters[/<id>]`   | Preflight CORS check          |

### Auth & Preferences

| Method | Path                 | Description                   |
|--------|----------------------|-------------------------------|
| POST   | `/register`          | Register a new user           |
| POST   | `/login`             | Log in and receive session ID |
| POST   | `/toggle-dark-mode`  | Toggle dark mode preference   |

---

## Password Hashing

This application uses [bcrypt](https://auth0.com/blog/hashing-in-action-understanding-bcrypt/) from the `passlib.hash` module to securely hash and verify passwords.

- **Algorithm:** `bcrypt`
- **Salt:** Automatically generated per password
- **Library:** [`passlib`](https://pypi.org/project/passlib/)

---

## Sessions

Session management is handled via a custom in-memory `SessionStore` using randomly generated Base64-encoded session IDs.

Authenticated endpoints require a `Bearer <session_id>` token in the `Authorization` header.

---

## Example Request (Add Monster)

```http
POST /monsters
Authorization: Bearer <session_id>
Content-Type: application/json

{
  "name": "Frost Wyrm",
  "description": "Undead dragon from the north",
  "type": "Undead",
  "strength": 12,
  "weakness": "Fire"
}
```