#jalankan di HP menggunaka termux/pydroid 3
from flask import Flask, request
from threading import Thread
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
import os

#Folder untuk menyimpan file
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

LATEST_FILES = []  
app_flask = Flask(__name__)


FILE_ICON = "file_icon.png"
VIDEO_ICON = "video_icon.png"



@app_flask.route("/upload", methods=["POST"])
def upload_file():
    global LATEST_FILES
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    LATEST_FILES.append(filepath)
    print(f"✅ File diterima: {filepath}")
    return "File uploaded successfully!", 200



def run_flask():
    app_flask.run(host="0.0.0.0", port=5000, debug=False)


class Viewer(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anchor_x = 'center'
        self.anchor_y = 'center'

        self.image = Image(
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.8, 0.8)  # 80% dari layar
        )
        self.add_widget(self.image)

        Clock.schedule_interval(self.check_for_new_file, 1)

    def check_for_new_file(self, dt):
        global LATEST_FILES
        if LATEST_FILES:
            filepath = LATEST_FILES.pop(0)  # ambil 1 file dari queue
            ext = filepath.split(".")[-1].lower()
            print(f"📥 Menampilkan file: {filepath} (.{ext})")

            if ext in ["png", "jpg", "jpeg", "bmp"]:
                self.fade_in_image(filepath)
            elif ext in ["mp4", "avi", "mov", "mkv", "webm"]:
                if os.path.exists(VIDEO_ICON):
                    self.fade_in_image(VIDEO_ICON)
                else:
                    print("⚠ video_icon.png tidak ditemukan")
            else:
                if os.path.exists(FILE_ICON):
                    self.fade_in_image(FILE_ICON)
                else:
                    print("⚠ file_icon.png tidak ditemukan")

    def fade_in_image(self, path):
        self.image.opacity = 0
        self.image.source = path
        self.image.reload()
        anim = Animation(opacity=1, duration=0.8, t='in_out_quad')
        anim.start(self.image)


class ReceiverApp(App):
    def build(self):
        Window.size = (600, 400)
        Window.clearcolor = (0, 0, 0, 1) 
        self.title = "📲 HP Receiver"
        return Viewer()


if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    ReceiverApp().run()
