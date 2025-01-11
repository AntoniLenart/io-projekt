from fpdf import FPDF
import os


class PDFGenerator:
    def __init__(self, summary_path, transcription_path, output_pdf_path):
        self.summary_path = summary_path
        self.transcription_path = transcription_path
        self.output_pdf_path = output_pdf_path
        self.pdf = FPDF()

    def read_file(self, file_path):
        """Reads content from a text file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()

    def add_text_to_pdf(self, title, content):
        """Adds a title and content to the PDF."""
        self.pdf.set_font("Arial", size=12)
        self.pdf.add_page()

        # Add title
        self.pdf.set_font("Arial", style='B', size=16)
        self.pdf.cell(0, 10, title, ln=True, align='C')
        self.pdf.ln(10)

        # Add content
        self.pdf.set_font("Arial", size=12)
        for line in content:
            self.pdf.multi_cell(0, 10, line)

    def generate_pdf(self):
        """Generates a PDF combining summary and transcription."""
        try:
            # Read files
            summary_content = self.read_file(self.summary_path)
            transcription_content = self.read_file(self.transcription_path)

            # Add content to PDF
            self.add_text_to_pdf("Summary", summary_content)
            self.add_text_to_pdf("Transcription", transcription_content)

            # Save PDF
            self.pdf.output(self.output_pdf_path)
            print(f"PDF successfully created: {self.output_pdf_path}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    # File paths
    summary_file = "summary.txt"
    transcription_file = "transcription.txt"
    output_pdf = "output.pdf"

    # Create and generate PDF
    pdf_generator = PDFGenerator(summary_file, transcription_file, output_pdf)
    pdf_generator.generate_pdf()
