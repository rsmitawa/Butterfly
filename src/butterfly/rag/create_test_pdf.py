from fpdf import FPDF
import os


create_test_invoice():
    pdf = FPDF()
    
    # Add a page with regular text
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="INVOICE", ln=1, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Customer: Aaron Hawkins", ln=1, align="L")
    pdf.cell(200, 10, txt="Invoice #: 4820", ln=1, align="L")
    pdf.cell(200, 10, txt="Date: 2024-04-05", ln=1, align="L")
    pdf.cell(200, 10, txt="Amount: $1,500.00", ln=1, align="L")
    
    # Save the PDF
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'raw')
    pdf.output(os.path.join(output_dir, "invoice_Aaron_Hawkins_4820.pdf"))

if __name__ == "__main__":
    create_test_invoice()
