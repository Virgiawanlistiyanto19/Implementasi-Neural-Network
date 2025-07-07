#Install library dahulu pip nama library
import cv2
import numpy as np
import requests
import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from threading import Thread
from tensorflow.keras.models import load_model

# 📈 Load model yang sudah dilatih
model = load_model("Gesture_nn_model (1).h5")
labels = ["open", "mencengkram", "genggam", "geser_kanan", "geser_kiri", "lepas"]


window = tk.Tk()
window.title("Gesture Transfer to HP")
window.geometry("1000x700")
status_label = tk.Label(
    window,
    text="✊ Genggam = Pilih, Geser ➡️, 🖐️ Lepas untuk kirim",
    font=("Arial", 14),
)
status_label.pack(pady=10)
canvas = tk.Canvas(window, width=1000, height=500, bg="black")
canvas.pack(pady=10)

cap = cv2.VideoCapture(0)

drag_mode = False
gesture_time = None
sent = False
image_id = None
img_tk = None
selected_file = None
selected_preview_image = None

IP_HP = ""  # isi dengan IP HP satu jaringan
URL_UPLOAD = f"http://{IP_HP}:5000/upload"



def fade_in_preview(img_pil):
    global image_id, img_tk
    w, h = canvas.winfo_width(), canvas.winfo_height()
    img_pil = img_pil.resize((w, h)).convert("RGBA")
    alpha_values = list(range(0, 256, 20))

    def animate():
        global image_id, img_tk
        nonlocal alpha_values
        if not alpha_values:
            return
        alpha = alpha_values.pop(0)
        img = img_pil.copy()
        img.putalpha(alpha)
        img_tk = ImageTk.PhotoImage(img)
        if image_id is None:
            image_id = canvas.create_image(
                w // 2, h // 2, anchor="center", image=img_tk
            )
        else:
            canvas.itemconfig(image_id, image=img_tk)
        canvas.image = img_tk
        window.after(30, animate)

    animate()



def fade_out_and_upload():
    global selected_file, selected_preview_image, image_id, img_tk
    img_pil = selected_preview_image.resize(
        (canvas.winfo_width(), canvas.winfo_height())
    ).convert("RGBA")
    alpha_values = list(range(255, 0, -20))

    def animate():
        nonlocal alpha_values
        if not alpha_values:
            try:
                with open(selected_file, "rb") as file_data:
                    res = requests.post(URL_UPLOAD, files={"file": file_data})
                    if res.ok:
                        status_label.config(text="✅ File terkirim ke HP!")
                    else:
                        status_label.config(text="⚠️ Gagal kirim ke HP!")
            except Exception as e:
                status_label.config(text=f"⚠️ Error: {e}")
            return
        alpha = alpha_values.pop(0)
        img = img_pil.copy()
        img.putalpha(alpha)
        img_tk = ImageTk.PhotoImage(img)
        canvas.itemconfig(image_id, image=img_tk)
        canvas.image = img_tk
        window.after(30, animate)

    animate()



def camera_loop():
    global drag_mode, sent, selected_file, gesture_time, selected_preview_image

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img_resized = cv2.resize(rgb_frame, (64, 64))
        img_normalized = img_resized / 255.0
        img_exp = np.expand_dims(img_normalized, axis=0)

        pred = model.predict(img_exp, verbose=0)[0]
        gesture_idx = np.argmax(pred)
        gesture = labels[gesture_idx]
        confidence = pred[gesture_idx]

        cv2.putText(
            frame,
            f"{gesture} ({confidence:.2f})",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        if gesture == "genggam" and not drag_mode:
            drag_mode = True
            gesture_time = time.time()
            selected_file = filedialog.askopenfilename(
                title="Pilih File untuk Dikirim",
                filetypes=[
                    (
                        "All Supported",
                        "*.png *.jpg *.jpeg *.bmp *.mp4 *.avi *.docx *.pdf *.pptx",
                    ),
                    ("Image Files", "*.png *.jpg *.jpeg *.bmp"),
                    ("Video Files", "*.mp4 *.avi"),
                    ("Word Document", "*.docx"),
                    ("PDF Document", "*.pdf"),
                    ("PowerPoint", "*.pptx"),
                ],
            )
            if selected_file:
                ext = selected_file.split(".")[-1].lower()
                if ext in ["png", "jpg", "jpeg", "bmp"]:
                    selected_preview_image = Image.open(selected_file)
                    fade_in_preview(selected_preview_image)
                else:
                    selected_preview_image = Image.new("RGB", (640, 480), color="gray")
                    fade_in_preview(selected_preview_image)
                status_label.config(text="👉 File dipilih, Geser ➡️ atau 🖐️ untuk kirim")
            else:
                drag_mode = False

        elif gesture in ["geser_kanan", "geser_kiri"] and drag_mode:
            arah = "➡️" if gesture == "geser_kanan" else "⬅️"
            status_label.config(text=f"🖐️ Geser {arah}, lepas untuk kirim")

        elif gesture == "open" and drag_mode and time.time() - gesture_time > 0.5:
            if not sent and selected_file:
                fade_out_and_upload()
                sent = True
                drag_mode = False

        if gesture != "open":
            sent = False

        cv2.imshow("Gesture Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        window.update_idletasks()
        window.update()

    cap.release()
    cv2.destroyAllWindows()


Thread(target=camera_loop, daemon=True).start()
window.mainloop()
