from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "FutureLens Backend Running 🚀"


@app.route("/process", methods=["POST"])
def process():
    data = request.json
    url = data["url"]

    with yt_dlp.YoutubeDL({
        "quiet": True,
        "no_warnings": True
    }) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = []
    for f in info["formats"]:
        if f.get("vcodec") != "none":
            formats.append({
                "id": f["format_id"],
                "format": f.get("format_note", "unknown")
            })

    return jsonify({"formats": formats})


@app.route("/download")
def download():
    url = request.args.get("url")
    format_id = request.args.get("format")

    filename = os.path.join(DOWNLOAD_FOLDER, f"{uuid.uuid4()}.%(ext)s")

    ydl_opts = {
        # 🔥 Clean logs
        "quiet": True,
        "no_warnings": True,

        # 🔥 Fix audio issue (AAC instead of opus)
        "format": f"{format_id}+bestaudio[ext=m4a]/best",

        "outtmpl": filename,
        "merge_output_format": "mp4",

        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        final_file = ydl.prepare_filename(info)

        if not final_file.endswith(".mp4"):
            final_file = final_file.rsplit(".", 1)[0] + ".mp4"

    @after_this_request
    def remove_file(response):
        try:
            if os.path.exists(final_file):
                os.remove(final_file)
                print("Deleted:", final_file)
        except Exception as e:
            print("Error deleting file:", e)
        return response

    return send_file(final_file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)