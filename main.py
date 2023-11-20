import tkinter as tk
from tkinter import messagebox, scrolledtext
import mysql.connector
from mysql.connector import Error

class MediConnectApp:
    def __init__(self, window):
        self.window = window
        self.window.title("MediConnect Database Interface")
        self.connection = None

        # Database Connection Fields
        tk.Label(window, text="Host:").grid(row=0, column=0)
        tk.Label(window, text="Username:").grid(row=1, column=0)
        tk.Label(window, text="Password:").grid(row=2, column=0)
        tk.Label(window, text="Database:").grid(row=3, column=0)
        self.host_entry = tk.Entry(window)
        self.host_entry.grid(row=0, column=1)
        self.username_entry = tk.Entry(window)
        self.username_entry.grid(row=1, column=1)
        self.password_entry = tk.Entry(window, show="*")
        self.password_entry.grid(row=2, column=1)
        self.database_entry = tk.Entry(window)
        self.database_entry.grid(row=3, column=1)
        tk.Button(window, text="Connect", command=self.connect_to_database).grid(row=4, column=1, sticky=tk.W)

        # Query Execution
        tk.Label(window, text="Enter Query:").grid(row=5, column=0)
        self.query_entry = tk.Entry(window, width=50)
        self.query_entry.grid(row=5, column=1, columnspan=2)
        tk.Button(window, text="Execute", command=self.execute_query).grid(row=5, column=3)

        # Query Result Display
        tk.Label(window, text="Query Results:").grid(row=6, column=0)
        self.query_result = scrolledtext.ScrolledText(window, height=10, width=80)
        self.query_result.grid(row=7, column=0, columnspan=4)

    def connect_to_database(self):
        host = self.host_entry.get()
        user = self.username_entry.get()
        password = self.password_entry.get()
        database = self.database_entry.get()

        try:
            self.connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
            messagebox.showinfo("Connection", "Successfully connected to the database")
        except Error as e:
            messagebox.showerror("Error", str(e))
            self.connection = None

    def execute_query(self):
        if self.connection and self.connection.is_connected():
            query = self.query_entry.get()
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                self.display_results(results)
            except Error as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "Not connected to the database")

    def display_results(self, results):
        self.query_result.delete(1.0, tk.END)  # Clear previous results
        for row in results:
            self.query_result.insert(tk.END, str(row) + "\n")

def main():
    root = tk.Tk()
    app = MediConnectApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
