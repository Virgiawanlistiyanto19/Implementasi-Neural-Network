# Install Library dulu dengan pip install nama library
# Jalankan di HP pakai Termux/Pydroid3
from flask import Flask, request
from threading import Thread
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
import os

# Folder akan di simpan
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

LATEST_FILE = None
app_flask = Flask(__name__)
# Icon untuk file dan video, pastikan gambar ini ada di folder yang sama
FILE_ICON = "file_icon.png"
VIDEO_ICON = "video_icon.png"


# Flask ini untuk menerima file dari Komputer
@app_flask.route("/upload", methods=["POST"])
def upload_file():
    global LATEST_FILE
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    LATEST_FILE = filepath
    return "File uploaded successfully!", 200


def run_flask():
    app_flask.run(host="0.0.0.0", port=5000, debug=False)


class Viewer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.image = Image(opacity=0)
        self.add_widget(self.image)
        Clock.schedule_interval(self.check_for_new_file, 1)

    def check_for_new_file(self, dt):
        global LATEST_FILE
        if LATEST_FILE:
            ext = LATEST_FILE.split(".")[-1].lower()
            print(f"📥 File diterima: {LATEST_FILE} (.{ext})")

            if ext in ["png", "jpg", "jpeg", "bmp"]:
                self.fade_in_image(LATEST_FILE)
            elif ext in ["mp4", "avi", "mov", "mkv", "webm"]:
                if os.path.exists(VIDEO_ICON):
                    self.fade_in_image(VIDEO_ICON)
                else:
                    print("⚠️ video_icon.png tidak ditemukan")
            else:
                if os.path.exists(FILE_ICON):
                    self.fade_in_image(FILE_ICON)
                else:
                    print("⚠️ file_icon.png tidak ditemukan")
            LATEST_FILE = None

    def fade_in_image(self, path):
        self.image.source = path
        self.image.opacity = 0
        anim = Animation(opacity=1, duration=0.5)
        anim.start(self.image)


class ReceiverApp(App):
    def build(self):
        Window.size = (600, 400)
        Window.clearcolor = (0, 0, 0, 1)  # hitam polos
        self.title = "📲 HP Receiver"
        return Viewer()


if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    ReceiverApp().run()
