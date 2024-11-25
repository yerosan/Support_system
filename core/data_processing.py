# Function to extract text from PDF
import PyPDF2
def extract_text_from_pdf(pdf_file):
    print("the file name__-----_", pdf_file)
    # document = fitz.open(file_path)
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    print("The Documents___----_", text)
    return text
