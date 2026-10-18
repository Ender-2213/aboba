import socket
import threading
import base64
import io
import os

import customtkinter as ctk
from tkinter import messagebox
from tkinter.filedialog import askdirectory


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


HOST = "127.0.0.1"
PORT = 5000


class ChatClient:
    """
    Окремий TCP-клієнт.
    GUI не працює безпосередньо з socket.
    """

    def __init__(self, on_message):
        self.sock = None
        self.username = ""
        self.running = False
        self.on_message = on_message

    def connect(self, username):
        self.username = username

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))

            self.running = True

            # Передаємо ім'я серверу
            self.send_text(
                f"LOGIN|{username}"
            )

            # Окремий потік для отримання повідомлень
            threading.Thread(
                target=self.receive_loop,
                daemon=True
            ).start()

            return True

        except Exception as e:
            print("Помилка підключення:", e)
            return False

    def send_text(self, message):
        """
        Відправка текстового повідомлення.
        """

        if not self.sock:
            return

        try:
            data = (message + "\n").encode("utf-8")
            self.sock.sendall(data)

        except Exception as e:
            print("Помилка відправки:", e)

    def send_message(self, message):
        """
        Відправити повідомлення в чат.
        """

        if not message:
            return

        self.send_text(
            f"MESSAGE|{self.username}|{message}"
        )

    def receive_loop(self):
        """
        Постійно очікує повідомлення від сервера.
        """

        buffer = ""

        while self.running:

            try:
                data = self.sock.recv(4096)

                if not data:
                    break

                buffer += data.decode("utf-8")

                # Розділяємо повідомлення по \n
                while "\n" in buffer:

                    message, buffer = buffer.split(
                        "\n",
                        1
                    )

                    if message:
                        self.on_message(message)

            except Exception as e:
                print("З'єднання закрито:", e)
                break

        self.running = False

    def send_file(self, filepath):
        """
        Передача файлу через socket.

        Файл:
        1. читаємо через io
        2. кодуємо base64
        3. передаємо серверу
        """

        if not self.sock:
            return

        try:

            with open(filepath, "rb") as file:

                file_data = file.read()

            # base64
            encoded = base64.b64encode(
                file_data
            ).decode("ascii")

            filename = os.path.basename(filepath)

            message = (
                f"FILE|"
                f"{self.username}|"
                f"{filename}|"
                f"{encoded}"
            )

            self.send_text(message)

        except Exception as e:
            print("Помилка передачі файлу:", e)

    def disconnect(self):

        self.running = False

        if self.sock:

            try:
                self.sock.close()

            except:
                pass

            self.sock = None


class ChatApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("LogiTalk")
        self.geometry("1000x650")
        self.minsize(800, 500)

        self.username = ""

        # TCP клієнт
        self.client = ChatClient(
            self.receive_message
        )

        self.show_registration()

    # ==============================
    # РЕЄСТРАЦІЯ
    # ==============================

    def show_registration(self):

        self.registration_frame = ctk.CTkFrame(
            self,
            corner_radius=20
        )

        self.registration_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        title = ctk.CTkLabel(
            self.registration_frame,
            text="LogiTalk",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        title.pack(
            pady=(30, 10)
        )

        subtitle = ctk.CTkLabel(
            self.registration_frame,
            text="Введіть ім'я користувача",
            font=ctk.CTkFont(size=15)
        )

        subtitle.pack(pady=10)

        self.username_entry = ctk.CTkEntry(
            self.registration_frame,
            width=300,
            height=45,
            placeholder_text="Ваше ім'я"
        )

        self.username_entry.pack(
            pady=10
        )

        connect_button = ctk.CTkButton(
            self.registration_frame,
            text="Підключитися",
            width=300,
            height=45,
            command=self.connect_user
        )

        connect_button.pack(
            pady=(10, 30)
        )

    # ==============================
    # ПІДКЛЮЧЕННЯ
    # ==============================

    def connect_user(self):

        username = self.username_entry.get().strip()

        if not username:

            messagebox.showwarning(
                "Помилка",
                "Введіть ім'я користувача!"
            )

            return

        # Підключаємо TCP клієнт
        connected = self.client.connect(
            username
        )

        if not connected:

            messagebox.showerror(
                "Помилка",
                "Не вдалося підключитися до сервера!"
            )

            return

        self.username = username

        self.registration_frame.destroy()

        self.create_chat()

    # ==============================
    # CHAT GUI
    # ==============================

    def create_chat(self):

        self.header = ctk.CTkFrame(
            self,
            height=60,
            corner_radius=0
        )

        self.header.pack(
            side="top",
            fill="x"
        )

        logo = ctk.CTkLabel(
            self.header,
            text="LogiTalk",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        logo.pack(
            side="left",
            padx=20
        )

        user_label = ctk.CTkLabel(
            self.header,
            text=f"Користувач: {self.username}"
        )

        user_label.pack(
            side="right",
            padx=20
        )

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # ==============================
        # SIDEBAR
        # ==============================

        self.sidebar = ctk.CTkFrame(
            self.main_frame,
            width=220,
            corner_radius=15
        )

        self.sidebar.pack(
            side="left",
            fill="y",
            padx=(0, 10)
        )

        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="Налаштування",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        sidebar_title.pack(
            pady=20
        )

        appearance_button = ctk.CTkButton(
            self.sidebar,
            text="🌙 Темна тема",
            command=self.toggle_theme
        )

        appearance_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        clear_button = ctk.CTkButton(
            self.sidebar,
            text="🗑 Очистити чат",
            command=self.clear_chat
        )

        clear_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        # Кнопка вибору папки
        folder_button = ctk.CTkButton(
            self.sidebar,
            text="📁 Вибрати папку",
            command=self.select_folder
        )

        folder_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        # Кнопка файлу
        file_button = ctk.CTkButton(
            self.sidebar,
            text="📎 Надіслати файл",
            command=self.send_file
        )

        file_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        exit_button = ctk.CTkButton(
            self.sidebar,
            text="Вийти",
            fg_color="#b83b3b",
            hover_color="#8f2c2c",
            command=self.close_app
        )

        exit_button.pack(
            fill="x",
            padx=15,
            pady=5
        )

        # ==============================
        # CHAT
        # ==============================

        self.chat_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=15
        )

        self.chat_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.messages = ctk.CTkTextbox(
            self.chat_frame,
            corner_radius=10,
            font=ctk.CTkFont(size=15),
            wrap="word"
        )

        self.messages.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(15, 10)
        )

        self.messages.configure(
            state="disabled"
        )

        # ==============================
        # INPUT
        # ==============================

        input_frame = ctk.CTkFrame(
            self.chat_frame,
            fg_color="transparent"
        )

        input_frame.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.message_entry = ctk.CTkEntry(
            input_frame,
            height=45,
            placeholder_text="Введіть повідомлення..."
        )

        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        self.message_entry.bind(
            "",
            lambda event: self.send_message()
        )

        send_button = ctk.CTkButton(
            input_frame,
            text="Надіслати",
            width=120,
            height=45,
            command=self.send_message
        )

        send_button.pack(
            side="right"
        )

        self.add_message(
            "Система",
            f"Вітаємо, {self.username}! Ви підключилися до чату."
        )

    # ==============================
    # ОТРИМАННЯ ПОВІДОМЛЕНЬ
    # ==============================

    def receive_message(self, message):

        # Callback виконується з іншого потоку,
        # тому GUI змінюємо через after()

        self.after(
            0,
            self.process_message,
            message
        )

    def process_message(self, message):

        parts = message.split("|", 3)

        if parts[0] == "MESSAGE":

            if len(parts) >= 3:

                sender = parts[1]
                text = parts[2]

                self.add_message(
                    sender,
                    text
                )

        elif parts[0] == "SYSTEM":

            if len(parts) >= 2:

                self.add_message(
                    "Система",
                    parts[1]
                )

        elif parts[0] == "FILE":

            if len(parts) >= 4:

                sender = parts[1]
                filename = parts[2]
                encoded = parts[3]

                self.receive_file(
                    sender,
                    filename,
                    encoded
                )

    # ==============================
    # НАДСИЛАННЯ ПОВІДОМЛЕННЯ
    # ==============================

    def send_message(self):

        message = self.message_entry.get().strip()

        if not message:
            return

        # Відправляємо серверу
        self.client.send_message(
            message
        )

        self.message_entry.delete(
            0,
            "end"
        )

    # ==============================
    # ДОДАВАННЯ ПОВІДОМЛЕННЯ
    # ==============================

    def add_message(
        self,
        sender,
        message
    ):

        self.messages.configure(
            state="normal"
        )

        self.messages.insert(
            "end",
            f"{sender}: {message}\n\n"
        )

        self.messages.configure(
            state="disabled"
        )

        self.messages.see(
            "end"
        )

    # ==============================
    # ФАЙЛ
    # ==============================

    def send_file(self):

        from tkinter.filedialog import askopenfilename

        filepath = askopenfilename()

        if not filepath:
            return

        self.client.send_file(
            filepath
        )

        self.add_message(
            "Система",
            f"Файл відправлено: {os.path.basename(filepath)}"
        )

    def receive_file(
        self,
        sender,
        filename,
        encoded
    ):

        try:

            # base64 -> bytes
            file_data = base64.b64decode(
                encoded
            )

            # io.BytesIO
            file_stream = io.BytesIO(
                file_data
            )

            self.add_message(
                "Файл",
                f"{sender} надіслав файл: {filename}"
            )

            # Тут можна зберегти файл
            # у вибрану користувачем папку

            if hasattr(self, "download_folder"):

                filepath = os.path.join(
                    self.download_folder,
                    filename
                )

                with open(
                    filepath,
                    "wb"
                ) as file:

                    file.write(
                        file_stream.read()
                    )

                self.add_message(
                    "Система",
                    f"Файл збережено: {filepath}"
                )

        except Exception as e:

            print(
                "Помилка отримання файлу:",
                e
            )

    # ==============================
    # ВИБІР ПАПКИ
    # ==============================

    def select_folder(self):

        folder = askdirectory(
            title="Виберіть папку для файлів"
        )

        if folder:

            self.download_folder = folder

            self.add_message(
                "Система",
                f"Папка для файлів: {folder}"
            )

    # ==============================
    # ОЧИСТКА
    # ==============================

    def clear_chat(self):

        self.messages.configure(
            state="normal"
        )

        self.messages.delete(
            "1.0",
            "end"
        )

        self.messages.configure(
            state="disabled"
        )

    # ==============================
    # ТЕМА
    # ==============================

    def toggle_theme(self):

        current = ctk.get_appearance_mode()

        if current == "Dark":

            ctk.set_appearance_mode(
                "light"
            )

        else:

            ctk.set_appearance_mode(
                "dark"
            )

    # ==============================
    # ВИХІД
    # ==============================

    def close_app(self):

        self.client.disconnect()

        self.destroy()


if __name__ == "__main__":

    app = ChatApp()

    app.mainloop()