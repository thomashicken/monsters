import sqlite3

class Database:
   def __init__(self, db_name="monsters.db"):
      self.db_name = db_name
      self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
      self.conn.row_factory = sqlite3.Row  # Makes fetchall() return dictionaries
      self.cursor = self.conn.cursor()
      self._create_table()

   def _create_table(self):
      self.cursor.execute('''
         CREATE TABLE IF NOT EXISTS monsters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               description TEXT,
               type TEXT,
               strength INTEGER,
               weakness TEXT
         )
      ''')
      self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
               first_name TEXT NOT NULL,
               last_name TEXT NOT NULL,
               email TEXT NOT NULL UNIQUE,
               password_hash TEXT NOT NULL,
               dark_mode BOOLEAN DEFAULT 0
         )
      ''')
      self.conn.commit()

   def save_record(self, monster):
      self.cursor.execute('''
         INSERT INTO monsters (name, description, type, strength, weakness)
         VALUES (?, ?, ?, ?, ?)
      ''', (monster["name"], monster.get("description", ""), monster.get("type", ""), monster.get("strength", 0), monster.get("weakness", "")))
      self.conn.commit()
      return self.cursor.lastrowid

   def read_all_records(self):
      self.cursor.execute("SELECT * FROM monsters ORDER BY id ASC")
      rows = self.cursor.fetchall()

      if not rows:
         return []  # Return an empty list if no records are found
      
      # Convert each sqlite3.Row object into a standard dictionary
      records = []
      for row in rows:
         record = dict(row)
         records.append(record)
      
      return records

   def get_record_by_id(self, monster_id):
      self.cursor.execute("SELECT * FROM monsters WHERE id = ?", [monster_id])
      row = self.cursor.fetchone()

      if not row:
         return None  # Return None if no record is found

      # Convert the sqlite3.Row object into a standard dictionary
      record = dict(row)

      return record

   def update_record(self, monster_id, data):
      print(f"Updating DB for ID {monster_id} with data: {data}")

      self.cursor.execute('''
         UPDATE monsters 
         SET name = ?, description = ?, type = ?, strength = ?, weakness = ? 
         WHERE id = ?
      ''', (
         data["name"],
         data.get("description", ""),
         data.get("type", ""),
         data.get("strength", 0),
         data.get("weakness", ""),
         monster_id
      ))

      self.conn.commit()

   def delete_record(self, monster_id):
      self.cursor.execute("DELETE FROM monsters WHERE id = ?", (monster_id,))
      self.conn.commit()

   def close_connection(self):
      self.conn.close()