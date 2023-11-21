import tkinter as tk
from tkinter import messagebox, scrolledtext, Entry, Button, Label, LabelFrame, Frame
import mysql.connector
from mysql.connector import Error

# Define your table creation SQL commands in a dictionary
TABLES = {
    'patient': (
        "CREATE TABLE `patient` ("
        "  `patient_id` int NOT NULL AUTO_INCREMENT,"
        "  `name` varchar(255) NOT NULL,"
        "  `birthdate` date NOT NULL,"
        "  `contact_info` varchar(255),"
        "  `medical_history` text,"
        "  `current_medications` text,"
        "  `allergies` text,"
        "  PRIMARY KEY (`patient_id`)"
        ") ENGINE=InnoDB"
    ),
    'provider': (
        "CREATE TABLE `provider` ("
        "  `provider_id` int NOT NULL AUTO_INCREMENT,"
        "  `name` varchar(255) NOT NULL,"
        "  `specialty` varchar(255) NOT NULL,"
        "  `contact_info` varchar(255),"
        "  `qualifications` text,"
        "  `availability_hours` varchar(255),"
        "  `hospital_clinic_affiliation` varchar(255),"
        "  PRIMARY KEY (`provider_id`)"
        ") ENGINE=InnoDB"
    ),
    'appointment': (
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
        ") ENGINE=InnoDB"
    ),
    'treatment': (
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
        ") ENGINE=InnoDB"
    ),
    'billing_record': (
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
        ") ENGINE=InnoDB"
    )
}


class DatabaseManager:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            self.connection.autocommit = True
            self.initialize_database()
            messagebox.showinfo("Database Connection", "Successfully connected to the database.")
        except Error as e:
            messagebox.showerror("Database Connection", f"An error occurred: {e}")

    def initialize_database(self):
        cursor = self.connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
        cursor.execute(f"USE {self.db_name}")

        for table_name, ddl in TABLES.items():
            try:
                cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
                    print(f"Table {table_name} already exists.")
                else:
                    print(err.msg)
        cursor.close()

    def execute_query(self, query, params=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            if query.lower().startswith('select'):
                return cursor.fetchall()
            else:
                self.connection.commit()
        except Error as e:
            messagebox.showerror("Database Operation", f"An error occurred: {e}")
        finally:
            cursor.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()


class MediConnectApp:
    def __init__(self, master):
        self.master = master
        self.master.title("MediConnect Database Interface")
        self.db_manager = None
        self.setup_gui()

    def setup_gui(self):
        self.master.geometry('800x600')

        Label(self.master, text="MediConnect Database Interface", font=('Helvetica', 16)).pack()

        # Connection details frame
        connection_frame = LabelFrame(self.master, text="MySQL Connection Details", padx=5, pady=5)
        connection_frame.pack(padx=10, pady=10, fill="x")

        Label(connection_frame, text="Host:").grid(row=0, column=0, sticky="w")
        self.host_entry = Entry(connection_frame)
        self.host_entry.grid(row=0, column=1, sticky="ew")

        Label(connection_frame, text="User:").grid(row=1, column=0, sticky="w")
        self.user_entry = Entry(connection_frame)
        self.user_entry.grid(row=1, column=1, sticky="ew")

        Label(connection_frame, text="Password:").grid(row=2, column=0, sticky="w")
        self.password_entry = Entry(connection_frame, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew")

        Label(connection_frame, text="Database:").grid(row=3, column=0, sticky="w")
        self.db_name_entry = Entry(connection_frame)
        self.db_name_entry.grid(row=3, column=1, sticky="ew")

        connect_button = Button(connection_frame, text="Connect", command=self.connect_to_database)
        connect_button.grid(row=4, column=1, sticky="ew", pady=5)

        # Result area
        self.query_result = scrolledtext.ScrolledText(self.master, height=15)
        self.query_result.pack(fill="both", expand=True)
        # Function buttons
        button_frame = Frame(self.master, padx=5, pady=5)
        button_frame.pack(fill="x")

        Button(button_frame, text="View All Patients", command=self.view_all_patients).pack(side="left", padx=5)
        Button(button_frame, text="Add New Patient", command=self.add_new_patient_form).pack(side="left", padx=5)
        Button(button_frame, text="View All Providers", command=self.view_all_providers).pack(side="left", padx=5)
        Button(button_frame, text="Add New Provider", command=self.add_new_provider).pack(side="left", padx=5)
        Button(button_frame, text="View All Appointments", command=self.view_all_appointments).pack(side="left", padx=5)
        Button(button_frame, text="Add New Appointment", command=self.add_new_appointment).pack(side="left", padx=5)
        Button(button_frame, text="View All Treatments", command=self.view_all_treatments).pack(side="left", padx=5)
        Button(button_frame, text="Add New Treatment", command=self.add_new_treatment).pack(side="left", padx=5)
        Button(button_frame, text="View All Billing Records", command=self.view_all_billing_records).pack(side="left",
                                                                                                          padx=5)
        Button(button_frame, text="Add New Billing Record", command=self.add_new_billing_record).pack(side="left",
                                                                                                      padx=5)

    # Define the view functions to execute the SELECT statements and display the results
    def view_all_patients(self):
        self.execute_and_display_query("SELECT * FROM patient")

    def view_all_providers(self):
        self.execute_and_display_query("SELECT * FROM provider")

    def view_all_appointments(self):
        self.execute_and_display_query("SELECT * FROM appointment")

    def view_all_treatments(self):
        self.execute_and_display_query("SELECT * FROM treatment")

    def view_all_billing_records(self):
        self.execute_and_display_query("SELECT * FROM billing_record")

    # Define methods for adding new records
    def add_new_patient_form(self):
        # This function will create a new window asking for the details of the new patient
        self.new_patient_window = tk.Toplevel(self.master)
        self.new_patient_window.title("Add New Patient")

        Label(self.new_patient_window, text="Name:").grid(row=0, column=0)
        self.patient_name_entry = Entry(self.new_patient_window)
        self.patient_name_entry.grid(row=0, column=1)

        Label(self.new_patient_window, text="Birthdate (YYYY-MM-DD):").grid(row=1, column=0)
        self.patient_birthdate_entry = Entry(self.new_patient_window)
        self.patient_birthdate_entry.grid(row=1, column=1)

        Label(self.new_patient_window, text="Contact Info:").grid(row=2, column=0)
        self.patient_contact_entry = Entry(self.new_patient_window)
        self.patient_contact_entry.grid(row=2, column=1)

        Button(self.new_patient_window, text="Submit", command=self.add_new_patient).grid(row=3, column=1)

    def add_new_patient(self):
        name = self.patient_name_entry.get()
        birthdate = self.patient_birthdate_entry.get()
        contact_info = self.patient_contact_entry.get()

        # Implement input validation here as necessary
        insert_query = "INSERT INTO patient (name, birthdate, contact_info) VALUES (%s, %s, %s)"
        self.db_manager.execute_query(insert_query, (name, birthdate, contact_info))

        # Close the add new patient form
        self.new_patient_window.destroy()

        messagebox.showinfo("Success", "New patient added successfully.")

    def add_new_provider_form(self):
        # Create the provider form and save the entries as attributes of the instance
        self.new_provider_window = tk.Toplevel(self.master)
        self.new_provider_window.title("Add New Provider")

        Label(self.new_provider_window, text="Name:").grid(row=0, column=0)
        self.provider_name_entry = Entry(self.new_provider_window)
        self.provider_name_entry.grid(row=0, column=1)

        Label(self.new_provider_window, text="Specialty:").grid(row=1, column=0)
        self.provider_specialty_entry = Entry(self.new_provider_window)
        self.provider_specialty_entry.grid(row=1, column=1)

        Label(self.new_provider_window, text="Contact Info:").grid(row=2, column=0)
        self.provider_contact_entry = Entry(self.new_provider_window)
        self.provider_contact_entry.grid(row=2, column=1)

        Button(self.new_provider_window, text="Submit", command=self.add_new_provider).grid(row=3, column=1)

    def add_new_provider(self):
        # Get the values from the entries and insert into the database
        name = self.provider_name_entry.get()
        specialty = self.provider_specialty_entry.get()
        contact_info = self.provider_contact_entry.get()

        if not all([name, specialty, contact_info]):  # Simple validation to ensure all fields are filled
            messagebox.showerror("Error", "All fields are required.")
            return

        insert_query = "INSERT INTO provider (name, specialty, contact_info) VALUES (%s, %s, %s)"
        try:
            self.db_manager.execute_query(insert_query, (name, specialty, contact_info))
            messagebox.showinfo("Success", "New provider added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.new_provider_window.destroy()  # Ensure the window is destroyed even if there's an error

    # Add new appointment form
    def add_new_appointment_form(self):
        self.new_appointment_window = tk.Toplevel(self.master)
        self.new_appointment_window.title("Add New Appointment")

        Label(self.new_appointment_window, text="Patient ID:").grid(row=0, column=0)
        self.appointment_patient_id_entry = Entry(self.new_appointment_window)
        self.appointment_patient_id_entry.grid(row=0, column=1)

        Label(self.new_appointment_window, text="Provider ID:").grid(row=1, column=0)
        self.appointment_provider_id_entry = Entry(self.new_appointment_window)
        self.appointment_provider_id_entry.grid(row=1, column=1)

        Label(self.new_appointment_window, text="Appointment Date (YYYY-MM-DD HH:MM:SS):").grid(row=2, column=0)
        self.appointment_date_entry = Entry(self.new_appointment_window)
        self.appointment_date_entry.grid(row=2, column=1)

        Label(self.new_appointment_window, text="Status:").grid(row=3, column=0)
        self.appointment_status_entry = Entry(self.new_appointment_window)
        self.appointment_status_entry.grid(row=3, column=1)

        Button(self.new_appointment_window, text="Submit", command=self.add_new_appointment).grid(row=4, column=1)

    def add_new_appointment(self):
        patient_id = self.appointment_patient_id_entry.get()
        provider_id = self.appointment_provider_id_entry.get()
        appointment_date = self.appointment_date_entry.get()
        status = self.appointment_status_entry.get()

        insert_query = """
        INSERT INTO appointment (patient_id, provider_id, appointment_date, status) 
        VALUES (%s, %s, %s, %s)
        """
        self.db_manager.execute_query(insert_query, (patient_id, provider_id, appointment_date, status))

        self.new_appointment_window.destroy()
        messagebox.showinfo("Success", "New appointment added successfully.")

    def add_new_treatment_form(self):
        self.new_treatment_window = tk.Toplevel(self.master)
        self.new_treatment_window.title("Add New Treatment")

        Label(self.new_treatment_window, text="Patient ID:").grid(row=0, column=0)
        self.treatment_patient_id_entry = Entry(self.new_treatment_window)
        self.treatment_patient_id_entry.grid(row=0, column=1)

        Label(self.new_treatment_window, text="Provider ID:").grid(row=1, column=0)
        self.treatment_provider_id_entry = Entry(self.new_treatment_window)
        self.treatment_provider_id_entry.grid(row=1, column=1)

        Label(self.new_treatment_window, text="Description:").grid(row=2, column=0)
        self.treatment_description_entry = Entry(self.new_treatment_window)
        self.treatment_description_entry.grid(row=2, column=1)

        Label(self.new_treatment_window, text="Start Date (YYYY-MM-DD):").grid(row=3, column=0)
        self.treatment_start_date_entry = Entry(self.new_treatment_window)
        self.treatment_start_date_entry.grid(row=3, column=1)

        Label(self.new_treatment_window, text="End Date (YYYY-MM-DD):").grid(row=4, column=0)
        self.treatment_end_date_entry = Entry(self.new_treatment_window)
        self.treatment_end_date_entry.grid(row=4, column=1)

        Label(self.new_treatment_window, text="Outcome Notes:").grid(row=5, column=0)
        self.treatment_outcome_notes_entry = Entry(self.new_treatment_window)
        self.treatment_outcome_notes_entry.grid(row=5, column=1)

        Button(self.new_treatment_window, text="Submit", command=self.add_new_treatment).grid(row=6, column=1)

    def add_new_treatment(self):
        patient_id = self.treatment_patient_id_entry.get()
        provider_id = self.treatment_provider_id_entry.get()
        description = self.treatment_description_entry.get()
        start_date = self.treatment_start_date_entry.get()
        end_date = self.treatment_end_date_entry.get()
        outcome_notes = self.treatment_outcome_notes_entry.get()

        insert_query = """
        INSERT INTO treatment (patient_id, provider_id, description, start_date, end_date, outcome_notes) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db_manager.execute_query(insert_query,
                                      (patient_id, provider_id, description, start_date, end_date, outcome_notes))

        self.new_treatment_window.destroy()
        messagebox.showinfo("Success", "New treatment record added successfully.")

    # Add new billing record form
    def add_new_billing_record_form(self):
        self.new_billing_record_window = tk.Toplevel(self.master)
        self.new_billing_record_window.title("Add New Billing Record")

        Label(self.new_billing_record_window, text="Patient ID:").grid(row=0, column=0)
        self.billing_patient_id_entry = Entry(self.new_billing_record_window)
        self.billing_patient_id_entry.grid(row=0, column=1)

        Label(self.new_billing_record_window, text="Date (YYYY-MM-DD):").grid(row=1, column=0)
        self.billing_date_entry = Entry(self.new_billing_record_window)
        self.billing_date_entry.grid(row=1, column=1)

        Label(self.new_billing_record_window, text="Total Cost:").grid(row=2, column=0)
        self.billing_total_cost_entry = Entry(self.new_billing_record_window)
        self.billing_total_cost_entry.grid(row=2, column=1)

        Label(self.new_billing_record_window, text="Payment Status:").grid(row=3, column=0)
        self.billing_payment_status_entry = Entry(self.new_billing_record_window)
        self.billing_payment_status_entry.grid(row=3, column=1)

        Button(self.new_billing_record_window, text="Submit", command=self.add_new_billing_record).grid(row=4, column=1)

    def add_new_billing_record(self):
        patient_id = self.billing_patient_id_entry.get()
        date = self.billing_date_entry.get()
        total_cost = self.billing_total_cost_entry.get()
        payment_status = self.billing_payment_status_entry.get()

        insert_query = """
        INSERT INTO billing_record (patient_id, date, total_cost, payment_status) 
        VALUES (%s, %s, %s, %s)
        """
        self.db_manager.execute_query(insert_query, (patient_id, date, total_cost, payment_status))

        self.new_billing_record_window.destroy()
        messagebox.showinfo("Success", "New billing record added successfully.")

    # Utility function to execute a query and display the results in the scrolled text area
    def execute_and_display_query(self, query):
        try:
            records = self.db_manager.execute_query(query)
            self.query_result.delete('1.0', tk.END)
            for record in records:
                self.query_result.insert(tk.END, f"{record}\n")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while executing the query: {e}")

    def connect_to_database(self):
        host = self.host_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        db_name = self.db_name_entry.get()

        self.db_manager = DatabaseManager(host, user, password, db_name)
        self.db_manager.connect()

    def dummy_command(self):
        messagebox.showinfo("Info", "This is a placeholder function.")

    def on_closing(self):
        if self.db_manager:
            self.db_manager.close()
        self.master.destroy()


def main():
    root = tk.Tk()
    app = MediConnectApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
