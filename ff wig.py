import customtkinter as ctk
from tkinter import messagebox


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ChatApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("LogiTalk")
        self.geometry("1000x650")
        self.minsize(800, 500)

        self.username = ""

        self.show_registration()




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
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(pady=(30, 10))

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
        self.username_entry.pack(pady=10)

        connect_button = ctk.CTkButton(
            self.registration_frame,
            text="Підключитися",
            width=300,
            height=45,
            command=self.connect_user
        )
        connect_button.pack(pady=(10, 30))


    def connect_user(self):
        username = self.username_entry.get().strip()

        if not username:
            messagebox.showwarning(
                "Помилка",
                "Введіть ім'я користувача!"
            )
            return

        self.username = username

        self.registration_frame.destroy()
        self.create_chat()



    def create_chat(self):

        # Заголовок
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
            font=ctk.CTkFont(size=22, weight="bold")
        )
        logo.pack(side="left", padx=20)

        user_label = ctk.CTkLabel(
            self.header,
            text=f"Користувач: {self.username}"
        )
        user_label.pack(side="right", padx=20)


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
            font=ctk.CTkFont(size=18, weight="bold")
        )
        sidebar_title.pack(pady=20)

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

        exit_button = ctk.CTkButton(
            self.sidebar,
            text="Вийти",
            fg_color="#b83b3b",
            hover_color="#8f2c2c",
            command=self.destroy
        )
        exit_button.pack(
            fill="x",
            padx=15,
            pady=5
        )


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
            font=ctk.CTkFont(size=15)
        )
        self.messages.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(15, 10)
        )

        self.messages.configure(state="disabled")


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
        send_button.pack(side="right")


        self.add_message(
            "Система",
            f"Вітаємо, {self.username}! Ви підключилися до чату."
        )



    def add_message(self, sender, message):

        self.messages.configure(state="normal")

        self.messages.insert(
            "end",
            f"{sender}: {message}\n\n"
        )

        self.messages.configure(state="disabled")
        self.messages.see("end")


    def send_message(self):

        message = self.message_entry.get().strip()

        if not message:
            return

        self.add_message(
            self.username,
            message
        )

        self.message_entry.delete(0, "end")



    def clear_chat(self):

        self.messages.configure(state="normal")
        self.messages.delete("1.0", "end")
        self.messages.configure(state="disabled")


    def toggle_theme(self):

        current = ctk.get_appearance_mode()

        if current == "Dark":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()