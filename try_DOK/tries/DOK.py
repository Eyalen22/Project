import os
import customtkinter as ctk
from tkinter import messagebox


class MyFileExplorer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # הגדרות חלון
        self.title("Custom File Explorer")
        self.geometry("700x500")
        ctk.set_appearance_mode("dark")

        # משתנה ששומר איפה אנחנו נמצאים כרגע
        self.current_path = os.path.abspath("C:\\")  # שנה כאן לאות של ה-USB שלך

        # --- חלק עליון: שורת כתובת וכפתור חזור ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=10, pady=10)

        self.back_btn = ctk.CTkButton(self.top_frame, text="⬅ חזור", width=70, command=self.go_back)
        self.back_btn.pack(side="left", padx=5)

        self.path_label = ctk.CTkLabel(self.top_frame, text=self.current_path, font=("Arial", 12))
        self.path_label.pack(side="left", padx=10)

        # --- חלק מרכזי: רשימת הקבצים ---
        self.list_frame = ctk.CTkScrollableFrame(self, width=650, height=350)
        self.list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.load_directory()

    def load_directory(self):
        """פונקציה שטוענת את רשימת הקבצים והתיקיות למסך"""
        # ניקוי המסך לפני טעינה מחדש
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.path_label.configure(text=self.current_path)

        try:
            # מקבלים את רשימת התוכן בתיקייה
            items = os.listdir(self.current_path)

            # מיון: תיקיות קודם, אחר כך קבצים
            items.sort(key=lambda x: os.path.isdir(os.path.join(self.current_path, x)), reverse=True)

            for item in items:
                full_path = os.path.join(self.current_path, item)
                is_dir = os.path.isdir(full_path)

                # בחירת אייקון וצבע
                icon = "📁" if is_dir else "📄"
                btn_color = "#2b2b2b" if is_dir else "transparent"

                # יצירת שורה לכל פריט
                btn = ctk.CTkButton(
                    self.list_frame,
                    text=f"{icon}  {item}",
                    anchor="w",
                    fg_color=btn_color,
                    hover_color="#3e3e3e",
                    command=lambda p=full_path: self.handle_click(p)
                )
                btn.pack(fill="x", pady=2, padx=5)

        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לגשת לתיקייה:\n{e}")
            self.go_back()

    def handle_click(self, path):
        """מה קורה כשלוחצים על פריט"""
        if os.path.isdir(path):
            # אם זו תיקייה - נכנסים אליה
            self.current_path = path
            self.load_directory()
        else:
            # אם זה קובץ - פותחים אותו במערכת
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("שגיאה", "לא ניתן לפתוח את הקובץ")

    def go_back(self):
        """חזרה לתיקייה הקודמת"""
        parent = os.path.dirname(self.current_path)
        # בדיקה שלא הגענו לקצה הכונן
        if parent != self.current_path:
            self.current_path = parent
            self.load_directory()


if __name__ == "__main__":
    app = MyFileExplorer()
    app.mainloop()