import os
import shutil
import zipfile
import base64
from flask import Flask, render_template, request
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent,
    FileName, FileType, Disposition
)

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
CUT_FOLDER = "cuts"


# --------------------------
# DOWNLOAD AUDIO FROM YOUTUBE
# --------------------------
def download_audio(singer, num_videos):
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    search_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True
    }

    with YoutubeDL(search_opts) as ydl:
        search = ydl.extract_info(
            f"ytsearch{num_videos*3}:{singer}",
            download=False
        )

    entries = search.get("entries", [])
    urls = []

    for e in entries:
        if e and e.get("url"):
            urls.append(e["url"])
        if len(urls) == num_videos:
            break

    download_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(id)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "ignoreerrors": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128"
        }]
    }

    with YoutubeDL(download_opts) as ydl:
        for url in urls:
            try:
                ydl.download([url])
            except:
                continue


# --------------------------
# CREATE MASHUP
# --------------------------
def create_mashup(singer, num_videos, duration):
    os.makedirs(CUT_FOLDER, exist_ok=True)

    download_audio(singer, num_videos)

    files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(".mp3")]

    if len(files) == 0:
        raise Exception("No audio downloaded")

    for file in files:
        audio = AudioSegment.from_mp3(os.path.join(DOWNLOAD_FOLDER, file))
        cut_audio = audio[:duration * 1000]
        cut_audio.export(os.path.join(CUT_FOLDER, file), format="mp3")

    final_audio = AudioSegment.empty()

    for file in os.listdir(CUT_FOLDER):
        if file.endswith(".mp3"):
            segment = AudioSegment.from_mp3(os.path.join(CUT_FOLDER, file))
            final_audio += segment

    output_file = "mashup.mp3"
    final_audio.export(output_file, format="mp3")

    zip_file = "mashup.zip"
    with zipfile.ZipFile(zip_file, "w") as zipf:
        zipf.write(output_file)

    shutil.rmtree(DOWNLOAD_FOLDER, ignore_errors=True)
    shutil.rmtree(CUT_FOLDER, ignore_errors=True)
    os.remove(output_file)

    return zip_file


# --------------------------
# SEND EMAIL (SENDGRID)
# --------------------------
def send_email(to_email, zip_file):

    if not os.path.exists(zip_file):
        return False

    message = Mail(
        from_email=os.getenv("FROM_EMAIL"),
        to_emails=to_email,
        subject="Your Mashup File",
        html_content="Your mashup is attached."
    )

    with open(zip_file, "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data).decode()

    attachment = Attachment(
        FileContent(encoded),
        FileName("mashup.zip"),
        FileType("application/zip"),
        Disposition("attachment")
    )

    message.attachment = attachment

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
        return True
    except:
        return False


# --------------------------
# ROUTE
# --------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        singer = request.form["singer"]
        num_videos = int(request.form["videos"])
        duration = int(request.form["duration"])
        email = request.form["email"]

        try:
            zip_file = create_mashup(singer, num_videos, duration)

            sent = send_email(email, zip_file)

            if os.path.exists(zip_file):
                os.remove(zip_file)

            if sent:
                return render_template(
                    "success.html",
                    message="Mashup created and sent to your email."
                )
            else:
                return render_template(
                    "success.html",
                    message="Mashup created but email could not be sent."
                )

        except Exception:
            return render_template(
                "success.html",
                message="Could not create mashup (YouTube may have blocked requests)."
            )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)