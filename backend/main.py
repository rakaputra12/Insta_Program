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
        raise ValueError(f"Datei ist zu groß ({file_size_mb:.2f} MB), "
                         f"maximal erlaubt sind {max_size_mb} MB.")

    # Dateiformat prüfen
    _, extension = os.path.splitext(file_path)
    if extension.lower() not in valid_formats:
        raise ValueError(f"Ungültiges Format '{extension}'. "
                         f"Erlaubt sind: {valid_formats}.")

    # Wenn alle Checks bestanden sind, Rückgabe True
    return True

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

        # Speichern der Datei im Upload-Ordner
        print(f"Saving file to: {media_path}")
        file.save(media_path)

        # Validate die Datei im Upload-Ordner
        try:
            validateImage(media_path)
        except ValueError as ve:
            # Löschen der Datei, falls ungültig
            if os.path.exists(media_path):
                os.remove(media_path)
            return jsonify({"status": "error", "message": str(ve)}), 400

        if scheduled_time:  # Schedule the post
            # Save to the database
            with db_connection.cursor() as cursor:
                cursor.execute(
                "INSERT INTO scheduled_posts (post_type, caption, hashtags, media_path, scheduled_time) "
                "VALUES (%s, %s, %s, %s, %s)",
                (post_type, caption, hashtags, media_path, scheduled_time)  # Save only the unique filename
                )
                db_connection.commit()
            return jsonify({"status": "success", "message": "Post scheduled successfully!"})

        final_caption = f"{caption}\n\n{hashtags}"

        # Upload based on post type
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
        if not scheduled_time and os.path.exists(media_path):  # Delete file only if not scheduled
            os.remove(media_path)

        # Cleanup additional unnecessary files with *.mp4.jpg
        temp_thumbnail_path = media_path + ".jpg"
        if os.path.exists(temp_thumbnail_path):
            os.remove(temp_thumbnail_path)

# Initialisiere den Instagram-Client nur, wenn die Datei direkt ausgeführt wird
if __name__ == "__main__":
    cl = Client()
    cl.load_settings('./info.json')
    USERNAME = "farm_projekt_DHBW"
    PASSWORD = "farmProjekt121224"
    cl.get_timeline_feed()

    try:
        cl.login(USERNAME, PASSWORD)
        print("Logged in successfully!")
    except Exception as e:
        print(f"Login failed: {e}")

    # Starte Flask-App
    app.run(debug=True, port=5000)
