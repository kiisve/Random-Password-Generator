#!/usr/bin/env python3
# Random Password Generator - GUI с использованием Tkinter
# Автор: [Бобылева Станислава] 
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
from datetime import datetime

# Константы pools символов
DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SPECIALS = '!@#$%^&*()-_=+[]{};:,.?/'

DEFAULT_MIN_LEN = 4
DEFAULT_MAX_LEN = 64

HISTORY_FILE = 'history.json'


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("Random Password Generator")

        # Параметры
        self.length_var = tk.IntVar(value=12)
        self.include_digits = tk.BooleanVar(value=True)
        self.include_letters = tk.BooleanVar(value=True)
        self.include_specials = tk.BooleanVar(value=False)

        self.history = self.load_history()

        # UI Раздел 1: Контроль генератора
        controls_frame = ttk.LabelFrame(root, text="Параметры пароля")
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Ползунок длины
        length_label = ttk.Label(controls_frame, text="Длина пароля:")
        length_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.length_slider = ttk.Scale(controls_frame, from_=DEFAULT_MIN_LEN, to=DEFAULT_MAX_LEN,
                                       orient="horizontal", command=self._on_length_change, variable=self.length_var)
        self.length_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.length_slider.set(self.length_var.get())

        self.length_value_label = ttk.Label(controls_frame, text=str(self.length_var.get()))
        self.length_value_label.grid(row=0, column=2, padx=5, pady=5)

        # Чекбоксы для классов символов
        checks_frame = ttk.Frame(controls_frame)
        checks_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky="w")

        self.digits_cb = ttk.Checkbutton(checks_frame, text="Цифры (0-9)", variable=self.include_digits)
        self.digits_cb.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.letters_cb = ttk.Checkbutton(checks_frame, text="Буквы (a-z, A-Z)", variable=self.include_letters)
        self.letters_cb.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        self.specials_cb = ttk.Checkbutton(checks_frame, text="Спец. символы (!@#$...)", variable=self.include_specials)
        self.specials_cb.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # Кнопка генерации
        self.generate_btn = ttk.Button(controls_frame, text="Генерировать", command=self.generate_password)
        self.generate_btn.grid(row=0, column=3, padx=10, pady=5, sticky="e")

        # UI Раздел 2: Отображение сгенерированного пароля
        result_frame = ttk.LabelFrame(root, text="Сгенерированный пароль")
        result_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(result_frame, textvariable=self.password_var, width=60, font=("Consolas", 12))
        self.password_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.password_entry.config(state="readonly")

        # UI Раздел 3: История
        history_frame = ttk.LabelFrame(root, text="История генераций")
        history_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Таблица истории (Treeview)
        columns = ("password", "length", "digits", "letters", "specials", "time")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            # Ширину можно подрегулировать
            self.tree.column(col, width=100, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Прокрутка для таблицы
        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        history_frame.rowconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)

        # Инициализация таблицы историей
        self.refresh_history_table()

        # Обновление размера при изменении окна
        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def _on_length_change(self, event=None):
        # Обновляем отображение текущего значения длины
        try:
            val = int(float(self.length_slider.get()))
        except Exception:
            val = self.length_var.get()
        self.length_var.set(val)
        self.length_value_label.config(text=str(val))

    def generate_password(self):
        length = int(self.length_var.get())

        pool = ""
        if self.include_digits.get():
            pool += DIGITS
        if self.include_letters.get():
            pool += LETTERS
        if self.include_specials.get():
            pool += SPECIALS

        if not pool:
            messagebox.showerror("Ошибка", "Не выбраны классы символов. Выберите хотя бы один из: цифры, буквы, спец. символы.")
            return

        if length < DEFAULT_MIN_LEN or length > DEFAULT_MAX_LEN:
            messagebox.showerror("Ошибка", f"Длина должна быть в диапазоне [{DEFAULT_MIN_LEN}, {DEFAULT_MAX_LEN}].")
            return

        # Генерация пароля
        password = ''.join(random.choice(pool) for _ in range(length))

        # Отобразим пароль в окне
        self.password_var.set(password)
        self.password_entry.config(state="normal")
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        self.password_entry.config(state="readonly")

        # Сохраняем в истории
        entry = {
            "password": password,
            "length": length,
            "digits": bool(self.include_digits.get()),
            "letters": bool(self.include_letters.get()),
            "specials": bool(self.include_specials.get()),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(entry)
        self.save_history()
        self.add_history_row(entry)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception:
                pass
        return []

    def save_history(self):
        # Максимальная история может быть ограничена, если нужно
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Ошибка сохранения истории:", e)

    def refresh_history_table(self):
        # Очистить текущие записи
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Загрузка всех записей
        for entry in self.history:
            self.add_history_row_to_table(entry)

    def add_history_row(self, entry):
        self.history.append(entry)  # Ensure in-memory list updated
        self.save_history()
        self.add_history_row_to_table(entry)

    def add_history_row_to_table(self, entry):
        # Можно отображать частично маску пароля для безопасности в таблице
        display_password = entry["password"]
        self.tree.insert('', 'end', values=(
            display_password,
            entry["length"],
            entry["digits"],
            entry["letters"],
            entry["specials"],
            entry["time"]
        ))

def main():
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()