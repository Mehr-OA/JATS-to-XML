import os
from pathlib import Path
import PyPDF2

directory='papers'

def convert_pdf_files_to_text():
    print('readings pdf file')
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory, filename)
            output_file_path = os.path.join('text files', os.path.splitext(filename)[0] + '.txt')

            with open(file_path, 'rb') as file, open(output_file_path, 'w', encoding='utf-8') as output_file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    output_file.write(page.extract_text())

def main():
    convert_pdf_files_to_text()


if __name__ == "__main__":
    main()
