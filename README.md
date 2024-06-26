# PDF to JATS XML Converter API

This API provides a service to convert PDF documents into JATS XML format. It utilizes GROBID for the initial conversion of PDFs to TEI XML, followed by an XSLT transformation from TEI XML to JATS XML.

## Prerequisites

Before you start using this API, ensure you have the following installed:
- [GROBID](https://github.com/kermitt2/grobid)
- Python 3.x
- Required Python libraries: Flask, lxml

## Usage

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Mehr-OA/pdf-to-jats.git
   cd pdf-to-jats
   
   python app.py
   ```
   
## Files Description

- **app.py**: Contains Flask routing calls for the API. It handles the web server logic.
- **ServiceFile.py**: Contains the logic for converting PDF files to TEI XML using GROBID and then to JATS XML using XSLT.
- **teixml**: Directory containing XSLT templates and other necessary structures for TEI XML.
   