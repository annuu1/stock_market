import os
import customtkinter as ctk
import json
import pdfkit
from customtkinter import filedialog

# Debugging: Check current directory and available files
print("Current Working Directory:", os.getcwd())
print("Files in the directory:", os.listdir())

try:
    from codes import codes
    print("Import successful")
except ModuleNotFoundError as e:
    print(f"Import failed: {e}")

class Dependency_manager():
    def __init__(self):
        pass

class Computation(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x300")
        self.columnconfigure((0, 1, 2, 3, 4), weight=1)
        main_frame = MainFrame(self)

class MainFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, sticky="nsew", columnspan=5)
        
        self.json_path = None

        # grid config
        self.columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.ask_file = ctk.CTkLabel(self, text="Open File:", width=50)
        self.ask_file.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")

        self.open_file_button = ctk.CTkButton(self, text="Select File", command=self.get_file)
        self.open_file_button.grid(row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew")

        self.gender = ctk.CTkComboBox(self, values=["Male", "Female"])
        self.gender.grid(row=0, column=3, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.gender.set(value="Male")

        self.regime = ctk.CTkComboBox(self, values=["Old Regime", "New Regime"])
        self.regime.grid(row=0, column=4, padx=(5, 5), pady=(5, 5), sticky="nsew")
        self.regime.set(value="New Regime")
        ctk.CTkLabel(self, text="Enter Ack").grid(row=1, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")

        self.acknowledgement = ctk.CTkEntry(self)
        self.acknowledgement.grid(row=1, column=1, padx=(5, 5), pady=(5, 5), sticky="nsew")

        self.generate_pdf = ctk.CTkButton(self, text="Generate Pdf", command=self.create_pdf)
        self.generate_pdf.grid(row=5, column=0, columnspan=5, padx=(5, 5), pady=(5, 5), sticky="nsew")

    def create_pdf(self):
        methods = Methods()

        path = self.json_path
        gender = self.gender.get()
        regime = self.regime.get()
        acknowledgement = self.acknowledgement.get()
        print(acknowledgement)
        
        methods.create_pdf(path, gender, regime, acknowledgement)
    
    def get_file(self):
        self.json_path = filedialog.askopenfilenames(initialdir=r"C:\Users\avnin\Downloads",
                                                     title="Select a File",
                                                     filetypes=(("JSON files", "*.json*"),
                                                                ("all files", "*.*")))
        if self.json_path:  # Check if any file is selected
            self.json_path = str(self.json_path[0])

class Methods:
    def __init__(self):
        pass

    def generate_comp_pdf(self, customer_name, ay, address, mob, email, pan, status, dob, res_status, father, gender, ac, ifsc, filing_status, aadhar, regime, acknowledgement, IncomeFromBusinessProf, income, other_income, exempt_income, gross_income, deductions, rounded_off, special_rates_tax, total_tax, rebate, tax_payable, tds, tds_round, gross_total_income, total_net_income, bank, business_details, other_income_details):
        template_path = r'D:\Study\Python Projects\filings\computation_template.html'
        output_path = f"C:\\Users\\avnin\\Desktop\\computations\\{customer_name} COMP {ay}.pdf"

        # Replace placeholders in the template
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()
            template_content = template_content.replace('{{name}}', str(customer_name))
            template_content = template_content.replace('{{ay}}', str(ay))
            template_content = template_content.replace('{{address}}', str(address))
            template_content = template_content.replace('{{mob}}', str(mob))
            template_content = template_content.replace('{{email}}', email)
            template_content = template_content.replace('{{pan}}', pan)
            template_content = template_content.replace('{{status}}', status)
            template_content = template_content.replace('{{dob}}', dob)
            template_content = template_content.replace('{{res_status}}', res_status)
            template_content = template_content.replace('{{father}}', father)
            template_content = template_content.replace('{{gender}}', gender)
            template_content = template_content.replace('{{ac}}', ac)
            template_content = template_content.replace('{{ifsc}}', ifsc)
            template_content = template_content.replace('{{filing_status}}', str(filing_status))
            template_content = template_content.replace('{{aadhar}}', aadhar)
            template_content = template_content.replace('{{regime}}', regime)
            template_content = template_content.replace('{{acknowledgement}}', acknowledgement)
            template_content = template_content.replace('{{IncomeFromBusinessProf}}', str(IncomeFromBusinessProf))
            template_content = template_content.replace('{{income}}', str(income))
            template_content = template_content.replace('{{other_income}}', str(other_income))
            template_content = template_content.replace('{{exempt_income}}', str(exempt_income))
            template_content = template_content.replace('{{gross_income}}', str(gross_income))
            template_content = template_content.replace('{{deductions}}', str(deductions))
            template_content = template_content.replace('{{rounded_off}}', str(rounded_off))
            template_content = template_content.replace('{{special_rates_tax}}', str(special_rates_tax))
            template_content = template_content.replace('{{total_tax}}', str(total_tax))
            template_content = template_content.replace('{{rebate}}', str(rebate))
            template_content = template_content.replace('{{tax_payable}}', str(tax_payable))
            template_content = template_content.replace('{{tds}}', str(tds))
            template_content = template_content.replace('{{tds_round}}', str(tds_round))
            template_content = template_content.replace('{{gross_total_income}}', str(gross_total_income))
            template_content = template_content.replace('{{total_net_income}}', str(total_net_income))
            template_content = template_content.replace('{{bank}}', bank)
            # Add business details and other income details
            template_content = template_content.replace('{{business_details}}', business_details)
            template_content = template_content.replace('{{other_income_details}}', other_income_details)

        # Generate PDF
        config = pdfkit.configuration(wkhtmltopdf=r'D:\my files\Applications\wkhtmltopdf.exe')
        pdfkit.from_string(template_content, output_path, configuration=config)

    def create_pdf(self, file_path, gender, regime, acknowledgement):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        absolute_file_path = os.path.join(script_dir, file_path)
        print("Absolute file path:", absolute_file_path)
        print("Current working directory:", os.getcwd())
        
        try:
            with open(absolute_file_path, 'r', encoding='utf-8') as json_file:
                itr_data = json.load(json_file)
                # Extract values
                customer_name = itr_data['ITR']['ITR4']['Verification']['Declaration'].get('AssesseeVerName', 'N/A')
               
