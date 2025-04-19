# save as check_db.py
import sqlite3

conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()
cursor.execute("SELECT title_en, ingredients FROM recipes")
rows = cursor.fetchall()
for row in rows:
    print(f"Title: {row[0]}, Ingredients: {row[1]}")
conn.close()