import os
from flask import Flask, request, jsonify
from instagrapi import Client
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Funktion zur Validierung von Bildern
def validateImage(file_path: str) -> bool:
    """
    Prüft, ob das gegebene Bild den Instagram-Anforderungen entspricht:
      - Dateigröße <= 5 MB
      - Unterstütztes Format (z.B. .jpg, .jpeg, .png)

    Gibt True zurück, wenn das Bild gültig ist, wirft sonst einen ValueError.
    """
    valid_formats = ('.jpg', '.jpeg', '.png')
    max_size_mb = 5

    # Existiert die Datei?
    if not os.path.isfile(file_path):
        raise ValueError(f"Datei '{file_path}' wurde nicht gefunden.")

    # Größe überprüfen (in MB)
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValueError(
            f"Datei ist zu groß ({file_size_mb:.2f} MB), "
            f"maximal erlaubt sind {max_size_mb} MB."
        )

    # Dateiformat prüfen
    _, extension = os.path.splitext(file_path)
    if extension.lower() not in valid_formats:
        raise ValueError(
            f"Ungueltiges Format '{extension}'. "
            f"Erlaubt sind: {valid_formats}."
        )

    # Wenn alle Checks bestanden sind, Rückgabe True
    return True


# **Hier wird der Instagram-Client global initialisiert**
cl = Client()
try:
    cl.load_settings('./info.json')
    USERNAME = "farm_projekt_DHBW"
    PASSWORD = "farmProjekt121224"
    cl.login(USERNAME, PASSWORD)
    print("Logged in successfully!")
except Exception as e:
    print(f"Login failed: {e}")

# Flask-App erstellen
app = Flask(__name__)
CORS(app)

# PostgreSQL-Datenbankverbindung
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "insta_db"

# Verbindung zur Datenbank herstellen
try:
    db_connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    print("Connected to the database successfully!")
except Exception as e:
    print(f"Database connection failed: {e}")

UPLOAD_FOLDER = "./temp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/upload", methods=["POST"])
def upload_post():
    try:
        post_type = request.form.get("post_type")
        caption = request.form.get("caption", "")
        hashtags = request.form.get("hashtags", "")
        file = request.files.get("media")
        scheduled_time = request.form.get("scheduled_time")

        if not file:
            return jsonify({"status": "error", "message": "No media file provided"}), 400

        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        media_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)

        # Speichern der Datei
        print(f"Saving file to: {media_path}")
        file.save(media_path)

        # Prüfung der Bild-/Dateigültigkeit
        try:
            validateImage(media_path)
        except ValueError as ve:
            # Bei ungültigem Format oder überschrittener Größe -> 400
            if os.path.exists(media_path):
                os.remove(media_path)
            return jsonify({"status": "error", "message": str(ve)}), 400

        # Wenn scheduled_time gesetzt ist: Speichere in DB für späteren Upload (Beispiel)
        if scheduled_time:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO scheduled_posts
                        (post_type, caption, hashtags, media_path, scheduled_time)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (post_type, caption, hashtags, media_path, scheduled_time)
                )
                db_connection.commit()

            return jsonify({"status": "success", "message": "Post scheduled successfully!"})

        # Ansonsten direkt hochladen
        final_caption = f"{caption}\n\n{hashtags}"
        if post_type == "image":
            cl.photo_upload(media_path, final_caption)
        elif post_type == "video":
            cl.video_upload(media_path, final_caption)
        else:
            return jsonify({"status": "error", "message": "Invalid post type"}), 400

        return jsonify({"status": "success", "message": "Post uploaded successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        # Datei nur löschen, wenn sie direkt hochgeladen wurde
        # (wenn es gescheduled ist, braucht die DB den Pfad!)
        if not request.form.get("scheduled_time") and os.path.exists(media_path):
            os.remove(media_path)

# Nur App starten, wenn Datei direkt ausgeführt wird
if __name__ == "__main__":
    app.run(debug=True, port=5000)
