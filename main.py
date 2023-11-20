import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error


class MediConnectApp:
    def __init__(self, window):
        self.window = window
        self.window.title("MediConnect Database Interface")

        # Labels
        tk.Label(window, text="Host:").grid(row=0, column=0)
        tk.Label(window, text="Username:").grid(row=1, column=0)
        tk.Label(window, text="Password:").grid(row=2, column=0)
        tk.Label(window, text="Database:").grid(row=3, column=0)

        # Entries
        self.host_entry = tk.Entry(window)
        self.host_entry.grid(row=0, column=1)
        self.username_entry = tk.Entry(window)
        self.username_entry.grid(row=1, column=1)
        self.password_entry = tk.Entry(window, show="*")
        self.password_entry.grid(row=2, column=1)
        self.database_entry = tk.Entry(window)
        self.database_entry.grid(row=3, column=1)

        # Connect Button
        tk.Button(window, text="Connect", command=self.connect_to_database).grid(row=4, column=1, sticky=tk.W)

    def connect_to_database(self):
        host = self.host_entry.get()
        user = self.username_entry.get()
        password = self.password_entry.get()
        database = self.database_entry.get()

        try:
            connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
            messagebox.showinfo("Connection", "Successfully connected to the database")
            connection.close()
        except Error as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = MediConnectApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
