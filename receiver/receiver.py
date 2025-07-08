from flask import Flask, request
from threading import Thread
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
import os
import shutil
import time

app_flask = Flask(__name__)
UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PICTURES_FOLDER = os.path.expanduser("~/Pictures")

class Viewer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img = Image(opacity=0)
        self.add_widget(self.img)
        Clock.schedule_interval(self.update_img, 1)

        self.last_shown = ""

    def update_img(self, dt):
        files = sorted(
            [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER)],
            key=os.path.getmtime,
            reverse=True
        )
        if files:
            latest = files[0]
            if latest != self.last_shown:
                self.img.source = latest
                self.img.reload()
                self.animate_img()
                self.last_shown = latest

    def animate_img(self):
        self.img.opacity = 0
        anim = Animation(opacity=1, duration=0.5)
        anim.start(self.img)

@app_flask.route("/upload", methods=["POST"])
def receive_img():
    file = request.files['file']
    timestamp = int(time.time() * 1000)
    filename = f"image_{timestamp}.png"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    print(f"📥 Gambar diterima: {filename}")

    # Salin ke folder galeri
    try:
        shutil.copy(save_path, os.path.join(PICTURES_FOLDER, filename))
        print(f"📷 Disalin ke galeri: {PICTURES_FOLDER}")
    except Exception as e:
        print(f"⚠️ Gagal salin ke galeri: {e}")

    return "OK", 200

def run_server():
    app_flask.run(host="0.0.0.0", port=5000)

class HPReceiverApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return Viewer()

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    HPReceiverApp().run()
