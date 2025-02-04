from fpdf import FPDF
import os


class PDFGenerator:
    """
    A class to generate a PDF document by combining summary and transcription files.

    Attributes:
        summary_path (str): Path to the summary text file.
        transcription_path (str): Path to the transcription text file.
        output_pdf_path (str): Path where the generated PDF will be saved.
        pdf (FPDF): Instance of the FPDF class for generating PDFs.
    """

    def __init__(self, summary_path, transcription_path, output_pdf_path):
        """
        Initializes the PDFGenerator with paths for summary, transcription, and output PDF.

        Args:
            summary_path (str): Path to the summary text file.
            transcription_path (str): Path to the transcription text file.
            output_pdf_path (str): Path where the generated PDF will be saved.
        """
        self.summary_path = summary_path
        self.transcription_path = transcription_path
        self.output_pdf_path = output_pdf_path
        self.pdf = FPDF()

    def read_file(self, txt_file_path):
        """
        Reads content from a text file.

        Args:
            txt_file_path (str): Path to the text file.

        Returns:
            list: Lines of text from the file.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        if not os.path.exists(txt_file_path):
            raise FileNotFoundError(f"File not found: {txt_file_path}")
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            return file.readlines()

    def add_text_to_pdf(self, title, content):
        """
        Adds a title and content to the PDF.

        Args:
            title (str): The title to be added at the top of the page.
            content (list): Lines of text content to be added to the PDF.
        """
        self.pdf.set_font("Arial", size=12)
        self.pdf.add_page()

        self.pdf.set_font("Arial", style='B', size=16)
        self.pdf.cell(0, 10, title, ln=True, align='C')
        self.pdf.ln(10)

        self.pdf.set_font("Arial", size=12)
        for line in content:
            self.pdf.multi_cell(0, 10, line)

    def generate_pdf(self):
        """
        Generates a PDF combining the summary and transcription content.

        The content from the summary and transcription files is read, added to the PDF,
        and the resulting PDF is saved to the specified output path.

        Raises:
            Exception: If any error occurs during the PDF generation process.
        """
        try:
            summary_content = self.read_file(self.summary_path)
            transcription_content = self.read_file(self.transcription_path)

            self.add_text_to_pdf("Summary", summary_content)
            self.add_text_to_pdf("Transcription", transcription_content)

            self.pdf.output(self.output_pdf_path)
            print(f"PDF successfully created: {self.output_pdf_path}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    summary_file = "summary.txt"
    transcription_file = "transcription.txt"
    output_pdf = "output.pdf"
    
    pdf_generator = PDFGenerator(summary_file, transcription_file, output_pdf)
    pdf_generator.generate_pdf()
