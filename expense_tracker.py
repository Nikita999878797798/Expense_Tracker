import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Файл для хранения данных
        self.data_file = "expenses.json"
        self.expenses = self.load_expenses()

        # Категории
        self.categories = ["Еда", "Транспорт", "Развлечения", "Коммунальные услуги", "Здоровье", "Покупки", "Другое"]

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_table_frame()
        self.create_stats_frame()

        # Загрузить данные в таблицу
        self.refresh_table()

    def create_input_frame(self):
        """Форма для добавления расходов"""
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма (₽):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar(value=self.categories[0])
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=self.categories, width=15)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="➕ Добавить расход", command=self.add_expense)
        self.add_button.grid(row=0, column=6, padx=10, pady=5)

    def create_filter_frame(self):
        """Фильтрация"""
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar(value="Все")
        categories_filter = ["Все"] + self.categories
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=categories_filter, width=15)
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по дате (начало)
        ttk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_from = ttk.Entry(filter_frame, width=12)
        self.filter_date_from.grid(row=0, column=3, padx=5, pady=5)

        # Фильтр по дате (конец)
        ttk.Label(filter_frame, text="До:").grid(row=0, column=4, padx=5, pady=5)
        self.filter_date_to = ttk.Entry(filter_frame, width=12)
        self.filter_date_to.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка применить фильтр
        self.filter_button = ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.refresh_table)
        self.filter_button.grid(row=0, column=6, padx=10, pady=5)

        # Кнопка сброса фильтра
        self.reset_button = ttk.Button(filter_frame, text="🔄 Сбросить", command=self.reset_filters)
        self.reset_button.grid(row=0, column=7, padx=5, pady=5)

    def create_table_frame(self):
        """Таблица с расходами"""
        table_frame = ttk.LabelFrame(self.root, text="Список расходов", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы (Treeview)
        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)

        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Сумма", text="Сумма (₽)")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Сумма", width=100, anchor="center")
        self.tree.column("Категория", width=120, anchor="center")
        self.tree.column("Дата", width=100, anchor="center")

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления записи
        self.delete_button = ttk.Button(self.root, text="🗑 Удалить выбранную запись", command=self.delete_expense)
        self.delete_button.pack(pady=5)

    def create_stats_frame(self):
        """Статистика - сумма расходов за период"""
        stats_frame = ttk.LabelFrame(self.root, text="Статистика", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)

        self.stats_label = ttk.Label(stats_frame, text="Сумма расходов за выбранный период: 0.00 ₽", font=("Arial", 12, "bold"))
        self.stats_label.pack()

    def add_expense(self):
        """Добавление нового расхода"""
        try:
            # Получаем данные
            amount_str = self.amount_entry.get().strip()
            category = self.category_var.get()
            date_str = self.date_entry.get().strip()

            # Проверка суммы
            if not amount_str:
                messagebox.showwarning("Ошибка", "Введите сумму!")
                return

            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Ошибка", "Сумма должна быть положительным числом!")
                return

            # Проверка даты
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2025-05-04)")
                return

            # Создаём ID (на основе текущего времени)
            import time
            expense_id = str(int(time.time()))

            # Добавляем расход
            expense = {
                "id": expense_id,
                "amount": amount,
                "category": category,
                "date": date_str
            }
            self.expenses.append(expense)

            # Сохраняем в JSON
            self.save_expenses()

            # Очищаем поле суммы
            self.amount_entry.delete(0, tk.END)

            # Обновляем таблицу
            self.refresh_table()

            messagebox.showinfo("Успех", f"Расход {amount} ₽ добавлен!")

        except ValueError:
            messagebox.showwarning("Ошибка", "Сумма должна быть числом!")

    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления!")
            return

        # Получаем ID из таблицы
        item = self.tree.item(selected[0])
        expense_id = item["values"][0]

        # Удаляем из списка
        self.expenses = [e for e in self.expenses if e["id"] != expense_id]

        # Сохраняем в JSON
        self.save_expenses()

        # Обновляем таблицу
        self.refresh_table()

        messagebox.showinfo("Успех", "Запись удалена!")

    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Получаем отфильтрованные расходы
        filtered = self.apply_filters()

        # Заполняем таблицу
        for expense in filtered:
            self.tree.insert("", tk.END, values=(
                expense["id"],
                f"{expense['amount']:.2f}",
                expense["category"],
                expense["date"]
            ))

        # Обновляем статистику
        self.update_stats(filtered)

    def apply_filters(self):
        """Применение фильтров к расходам"""
        filtered = self.expenses.copy()

        # Фильтр по категории
        category_filter = self.filter_category_var.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e["category"] == category_filter]

        # Фильтр по дате (от)
        date_from_str = self.filter_date_from.get().strip()
        if date_from_str:
            try:
                date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= date_from]
            except ValueError:
                pass  # Игнорируем неверный формат

        # Фильтр по дате (до)
        date_to_str = self.filter_date_to.get().strip()
        if date_to_str:
            try:
                date_to = datetime.strptime(date_to_str, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= date_to]
            except ValueError:
                pass

        return filtered

    def update_stats(self, expenses_list):
        """Подсчёт суммы расходов за отфильтрованный период"""
        total = sum(e["amount"] for e in expenses_list)
        self.stats_label.config(text=f"Сумма расходов за выбранный период: {total:.2f} ₽")

    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_category_var.set("Все")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()

    def load_expenses(self):
        """Загрузка расходов из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_expenses(self):
        """Сохранение расходов в JSON"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
