from flask import Flask, request
from threading import Thread
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
import os

app_flask = Flask(_name_)
IMAGE_FILE = "lautest.png"

class Viewer(BoxLayout):
    def _init_(self, **kwargs):
        super()._init_(**kwargs)
        self.img = Image(opacity=0)
        self.add_widget(self.img)
        Clock.schedule_interval(self.update_img, 1)

    def update_img(self, dt):
        if os.path.exists(IMAGE_FILE):
            self.img.source = IMAGE_FILE
            self.img.reload()
            self.animate_img()

    def animate_img(self):
        self.img.opacity = 0
        anim = Animation(opacity=1, duration=0.5)
        anim.start(self.img)

@app_flask.route("/upload", methods=["POST"])
def receive_img():
    file = request.files['file']
    file.save(IMAGE_FILE)
    print("📥 Gambar diterima.")
    return "OK", 200

def run_server():
    app_flask.run(host="0.0.0.0", port=5000)

class HPReceiverApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return Viewer()

if _name_ == "_main_":
    Thread(target=run_server, daemon=True).start()
    HPReceiverApp().run()
