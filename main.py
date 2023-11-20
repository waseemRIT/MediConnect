import tkinter as tk
from tkinter import scrolledtext, Entry, Button, Label
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox

TABLES = {}

# Patient Table
TABLES['patient'] = (
    "CREATE TABLE `patient` ("
    "  `patient_id` int NOT NULL AUTO_INCREMENT,"
    "  `name` varchar(255) NOT NULL,"
    "  `birthdate` date NOT NULL,"
    "  `contact_info` varchar(255),"
    "  `medical_history` text,"
    "  `current_medications` text,"
    "  `allergies` text,"
    "  PRIMARY KEY (`patient_id`)"
    ") ENGINE=InnoDB")

# Provider Table
TABLES['provider'] = (
    "CREATE TABLE `provider` ("
    "  `provider_id` int NOT NULL AUTO_INCREMENT,"
    "  `name` varchar(255) NOT NULL,"
    "  `specialty` varchar(255) NOT NULL,"
    "  `contact_info` varchar(255),"
    "  `qualifications` text,"
    "  `availability_hours` varchar(255),"
    "  `hospital_clinic_affiliation` varchar(255),"
    "  PRIMARY KEY (`provider_id`)"
    ") ENGINE=InnoDB")

# Appointment Table
TABLES['appointment'] = (
    "CREATE TABLE `appointment` ("
    "  `appointment_id` int NOT NULL AUTO_INCREMENT,"
    "  `patient_id` int NOT NULL,"
    "  `provider_id` int NOT NULL,"
    "  `appointment_date` datetime NOT NULL,"
    "  `status` varchar(255) NOT NULL,"
    "  `reason_for_appointment` text,"
    "  PRIMARY KEY (`appointment_id`),"
    "  FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`) ON DELETE CASCADE,"
    "  FOREIGN KEY (`provider_id`) REFERENCES `provider` (`provider_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

# Treatment Table
TABLES['treatment'] = (
    "CREATE TABLE `treatment` ("
    "  `treatment_id` int NOT NULL AUTO_INCREMENT,"
    "  `patient_id` int NOT NULL,"
    "  `provider_id` int NOT NULL,"
    "  `description` text,"
    "  `start_date` date NOT NULL,"
    "  `end_date` date,"
    "  `outcome_notes` text,"
    "  PRIMARY KEY (`treatment_id`),"
    "  FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`) ON DELETE CASCADE,"
    "  FOREIGN KEY (`provider_id`) REFERENCES `provider` (`provider_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")

# Billing Record Table
TABLES['billing_record'] = (
    "CREATE TABLE `billing_record` ("
    "  `billing_id` int NOT NULL AUTO_INCREMENT,"
    "  `patient_id` int NOT NULL,"
    "  `date` date NOT NULL,"
    "  `itemized_services` text,"
    "  `total_cost` decimal(10,2) NOT NULL,"
    "  `insurance_details` text,"
    "  `payment_status` varchar(255) NOT NULL,"
    "  PRIMARY KEY (`billing_id`),"
    "  FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")


class MediConnectApp:

    def __init__(self, window):
        self.window = window
        self.window.title("MediConnect Database Interface")
        self.connection = None  # Initialize connection to None
        self.setup_gui()

    def setup_gui(self):
        # GUI layout code here
        # Define the main layout of the GUI
        self.window.geometry('800x600')  # Set window size
        tk.Label(self.window, text="MediConnect Database Interface", font=('Helvetica', 16)).pack()

        # Setup buttons and the display area
        button_frame = tk.Frame(self.window)
        button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.query_result = scrolledtext.ScrolledText(self.window, height=30, width=70)
        self.query_result.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add buttons for each action
        actions = [
            ("View All Patients", self.view_all_patients),
            ("View All Providers", self.view_all_providers),
            ("View All Appointments", self.view_all_appointments),
            ("View All Treatments", self.view_all_treatments),
            ("View All Billing Records", self.view_all_billing_records),
            ("Insert New Patient", self.insert_patient),
            ("Insert New Provider", self.insert_provider),
            ("Insert New Appointment", self.insert_appointment),
            ("Insert New Treatment", self.insert_treatment),
            ("Insert New Billing Record", self.insert_billing_record)
        ]

        # Add entry fields for MySQL connection details
        tk.Label(self.window, text="MySQL Connection Details", font=('Helvetica', 14)).pack()
        tk.Label(self.window, text="Host:").pack()
        self.host_entry = Entry(self.window)
        self.host_entry.pack()
        tk.Label(self.window, text="User:").pack()
        self.user_entry = Entry(self.window)
        self.user_entry.pack()
        tk.Label(self.window, text="Password:").pack()
        self.password_entry = Entry(self.window, show="*")  # Show asterisks for password
        self.password_entry.pack()

        # Add a button to initialize the database
        initialize_button = Button(self.window, text="Initialize Database", command=self.connect_to_database)
        initialize_button.pack()

        for text, command in actions:
            button = tk.Button(button_frame, text=text, command=command, width=25)
            button.pack(pady=5)

    def connect_to_database(self):
        # Database connection code here
        # Get MySQL connection details from the entry fields
        self.db_host = self.host_entry.get()
        self.db_user = self.user_entry.get()
        self.db_password = self.password_entry.get()

        try:
            # Try to connect to the MySQL server
            self.connection = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            self.connection.autocommit = True
            self.initialize_database()
        except Error as e:
            messagebox.showerror("Error", f"Failed to connect to database: {e}")
            self.window.destroy()



    def connect_to_database(self):
        # Database connection code here
        # Get MySQL connection details from the entry fields
        self.db_host = self.host_entry.get()
        self.db_user = self.user_entry.get()
        self.db_password = self.password_entry.get()
        self.db_name = "MediConnect"  # Database name

        # Try to connect to the MySQL server
        try:
            self.connection = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            self.connection.autocommit = True
            self.initialize_database()
        except Error as e:
            messagebox.showerror("Error", f"Failed to connect to database: {e}")
            self.window.destroy()



    def initialize_database(self):
        # Initialize the database and tables if they don't exist
        try:
            cursor = self.connection.cursor()

            # Create the 'MediConnect' database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS MediConnect")

            # Use the 'MediConnect' database
            cursor.execute("USE MediConnect")

            # Create tables if they don't exist
            for table_name, ddl in TABLES.items():
                cursor.execute(ddl)

            cursor.close()
            self.insert_sample_data()
        except Error as e:
            messagebox.showerror("Error", f"Failed to initialize database: {e}")

    def insert_sample_data(self):
        sample_data = {
            'patient': [
                "INSERT INTO patient (name, birthdate, contact_info) VALUES ('John Doe', '1990-01-01', 'john.doe@example.com');",
                "INSERT INTO patient (name, birthdate, contact_info) VALUES ('Jane Smith', '1985-03-15', 'jane.smith@example.com');",
                "INSERT INTO patient (name, birthdate, contact_info) VALUES ('Michael Johnson', '1978-08-20', 'michael.johnson@example.com');",
                "INSERT INTO patient (name, birthdate, contact_info) VALUES ('Emily Davis', '1995-05-10', 'emily.davis@example.com');",
                # Add more sample data for the 'patient' table
            ],
            'provider': [
                "INSERT INTO provider (name, specialty, contact_info) VALUES ('Dr. Smith', 'Cardiology', 'smith@example.com');",
                "INSERT INTO provider (name, specialty, contact_info) VALUES ('Dr. Johnson', 'Pediatrics', 'johnson@example.com');",
                "INSERT INTO provider (name, specialty, contact_info) VALUES ('Dr. Brown', 'Orthopedics', 'brown@example.com');",
                "INSERT INTO provider (name, specialty, contact_info) VALUES ('Dr. Lee', 'Dermatology', 'lee@example.com');",
                # Add more sample data for the 'provider' table
            ],
            'appointment': [
                "INSERT INTO appointment (patient_id, provider_id, appointment_date, status) VALUES (1, 1, '2023-11-30 10:00:00', 'Scheduled');",
                "INSERT INTO appointment (patient_id, provider_id, appointment_date, status) VALUES (2, 2, '2023-12-01 14:30:00', 'Cancelled');",
                "INSERT INTO appointment (patient_id, provider_id, appointment_date, status) VALUES (3, 3, '2023-12-05 11:15:00', 'Scheduled');",
                "INSERT INTO appointment (patient_id, provider_id, appointment_date, status) VALUES (4, 4, '2023-12-10 09:30:00', 'Completed');",
                # Add more sample data for the 'appointment' table
            ],
            'treatment': [
                "INSERT INTO treatment (patient_id, provider_id, description, treatment_date) VALUES (1, 1, 'Regular checkup', '2023-11-15');",
                "INSERT INTO treatment (patient_id, provider_id, description, treatment_date) VALUES (2, 2, 'Vaccination', '2023-12-05');",
                "INSERT INTO treatment (patient_id, provider_id, description, treatment_date) VALUES (3, 3, 'Physical therapy', '2023-12-12');",
                "INSERT INTO treatment (patient_id, provider_id, description, treatment_date) VALUES (4, 4, 'Dermatological procedure', '2023-12-20');",
                # Add more sample data for the 'treatment' table
            ],
            'billing_record': [
                "INSERT INTO billing_record (patient_id, amount_due, due_date, status) VALUES (1, 100.00, '2023-11-30', 'Pending');",
                "INSERT INTO billing_record (patient_id, amount_due, due_date, status) VALUES (2, 75.50, '2023-12-15', 'Paid');",
                "INSERT INTO billing_record (patient_id, amount_due, due_date, status) VALUES (3, 200.00, '2023-12-10', 'Pending');",
                "INSERT INTO billing_record (patient_id, amount_due, due_date, status) VALUES (4, 150.25, '2023-12-20', 'Paid');",
                # Add more sample data for the 'billing_record' table
            ]
        }

        try:
            cursor = self.connection.cursor()
            for table, queries in sample_data.items():
                for query in queries:
                    cursor.execute(query)
            cursor.close()
        except Error as e:
            messagebox.showerror("Error", f"Failed to insert sample data: {e}")

    # Define the view functions to execute the SELECT statements and display the results
    # Each view function should have a corresponding SELECT statement for its table

    def view_all_patients(self):
        self.execute_query("SELECT * FROM patient")

    def view_all_providers(self):
        self.execute_query("SELECT * FROM provider")

    def view_all_appointments(self):
        self.execute_query("SELECT * FROM appointment")

    def view_all_treatments(self):
        self.execute_query("SELECT * FROM treatment")

    def view_all_billing_records(self):
        self.execute_query("SELECT * FROM billing_record")

    def execute_query(self, query, params=()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            if query.lower().startswith("select"):
                records = cursor.fetchall()
                self.display_records(records)
            else:
                self.connection.commit()
            cursor.close()
        except Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def display_records(self, records):
        self.query_result.delete('1.0', tk.END)
        for row in records:
            self.query_result.insert(tk.END, f"{row}\n")

    # Define the insert functions to add new records to each table
    # Each insert function should prompt the user for input and execute an INSERT statement

    def insert_patient(self):
        try:
            # Get input from the user
            name = self.name_entry.get()
            birthdate = self.birthdate_entry.get()
            contact_info = self.contact_info_entry.get()
            medical_history = self.medical_history_entry.get()
            current_medications = self.current_medications_entry.get()
            allergies = self.allergies_entry.get()

            # Validate inputs (you can add more validation as needed)
            if not name or not birthdate:
                messagebox.showerror("Error", "Name and Birthdate are required fields.")
                return

            # SQL query to insert a new patient record
            sql = "INSERT INTO patient (name, birthdate, contact_info, medical_history, current_medications, allergies) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (name, birthdate, contact_info, medical_history, current_medications, allergies)

            # Execute the INSERT statement
            self.execute_query(sql, values)

            # Commit the transaction
            self.commit()

            # Show success message
            messagebox.showinfo("Success", "Patient record added successfully!")

        except Exception as e:
            # Handle any errors that occur during insertion
            messagebox.showerror("Error", f"Error inserting patient record: {str(e)}")

    def insert_provider(self):
        try:
            # Get input from the user
            name = self.name_entry.get()
            specialty = self.specialty_entry.get()
            contact_info = self.contact_info_entry.get()

            # Validate inputs (you can add more validation as needed)
            if not name or not specialty:
                messagebox.showerror("Error", "Name and Specialty are required fields.")
                return

            # SQL query to insert a new provider record
            sql = "INSERT INTO provider (name, specialty, contact_info) VALUES (%s, %s, %s)"
            values = (name, specialty, contact_info)

            # Execute the INSERT statement
            self.execute_query(sql, values)

            # Commit the transaction
            self.commit()

            # Show success message
            messagebox.showinfo("Success", "Provider record added successfully!")

        except Exception as e:
            # Handle any errors that occur during insertion
            messagebox.showerror("Error", f"Error inserting provider record: {str(e)}")

    def insert_appointment(self):
        try:
            # Get input from the user
            patient_id = self.patient_id_entry.get()
            provider_id = self.provider_id_entry.get()
            appointment_date = self.appointment_date_entry.get()
            status = self.status_entry.get()

            # Validate inputs (you can add more validation as needed)
            if not patient_id or not provider_id or not appointment_date:
                messagebox.showerror("Error", "Patient ID, Provider ID, and Appointment Date are required fields.")
                return

            # SQL query to insert a new appointment record
            sql = "INSERT INTO appointment (patient_id, provider_id, appointment_date, status) VALUES (%s, %s, %s, %s)"
            values = (patient_id, provider_id, appointment_date, status)

            # Execute the INSERT statement
            self.execute_query(sql, values)

            # Commit the transaction
            self.commit()

            # Show success message
            messagebox.showinfo("Success", "Appointment record added successfully!")

        except Exception as e:
            # Handle any errors that occur during insertion
            messagebox.showerror("Error", f"Error inserting appointment record: {str(e)}")

    def insert_treatment(self):
        try:
            # Get input from the user
            patient_id = self.patient_id_entry.get()
            provider_id = self.provider_id_entry.get()
            description = self.description_entry.get()
            treatment_date = self.treatment_date_entry.get()

            # Validate inputs (you can add more validation as needed)
            if not patient_id or not provider_id or not treatment_date:
                messagebox.showerror("Error", "Patient ID, Provider ID, and Treatment Date are required fields.")
                return

            # SQL query to insert a new treatment record
            sql = "INSERT INTO treatment (patient_id, provider_id, description, treatment_date) VALUES (%s, %s, %s, %s)"
            values = (patient_id, provider_id, description, treatment_date)

            # Execute the INSERT statement
            self.execute_query(sql, values)

            # Commit the transaction
            self.commit()

            # Show success message
            messagebox.showinfo("Success", "Treatment record added successfully!")

        except Exception as e:
            # Handle any errors that occur during insertion
            messagebox.showerror("Error", f"Error inserting treatment record: {str(e)}")

    def insert_billing_record(self):
        try:
            # Get input from the user
            patient_id = self.patient_id_entry.get()
            amount_due = self.amount_due_entry.get()
            due_date = self.due_date_entry.get()
            status = self.status_entry.get()

            # Validate inputs (you can add more validation as needed)
            if not patient_id or not amount_due or not due_date:
                messagebox.showerror("Error", "Patient ID, Amount Due, and Due Date are required fields.")
                return

            # SQL query to insert a new billing record
            sql = "INSERT INTO billing_record (patient_id, amount_due, due_date, status) VALUES (%s, %s, %s, %s)"
            values = (patient_id, amount_due, due_date, status)

            # Execute the INSERT statement
            self.execute_query(sql, values)

            # Commit the transaction
            self.commit()

            # Show success message
            messagebox.showinfo("Success", "Billing record added successfully!")

        except Exception as e:
            # Handle any errors that occur during insertion
            messagebox.showerror("Error", f"Error inserting billing record: {str(e)}")

    def on_closing(self):
        # Close the connection and the window
        if self.connection and self.connection.is_connected():
            self.connection.close()
        self.window.destroy()


def main():
    root = tk.Tk()
    app = MediConnectApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
