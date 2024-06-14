from dotenv import load_dotenv
import os
from lxml import etree
import xml.etree.ElementTree as ET
from lxml.builder import E
import re
import requests
import os.path
load_dotenv()

directory='paper-pdfs'
GROBID_API_URL = 'http://localhost:8070/api/processFulltextDocument'

def pdf_to_xml(pdf_file):
    file = open(pdf_file, 'rb')
    response = requests.post(GROBID_API_URL, files={'input': file})
    if response.status_code == 200:
        xml_tree = etree.fromstring(response.content)
        return convert_tei_to_jats(xml_tree, 'temp.xml')
    else:
        return "File cannot be parsed"


def pdf_to_txt():
    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory, filename)
            #print(file_path)
            output_file_path = os.path.join('textfiles', os.path.splitext(filename)[0] + '.txt')
            with open(file_path, 'rb') as file, open(output_file_path, 'w', encoding='utf-8') as output_file:
                #print(file)
                files = {'input': file}
                response = requests.post(GROBID_API_URL, files=files)
                if response.status_code == 200:
                    print(True)
                    xml_tree = etree.fromstring(response.content)
                    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
                    paper_content = extract_paper_content(xml_tree, ns)
                    paper_metadata = extract_paper_metadata(xml_tree, ns)

                    textcontent=""
                    textcontent=textcontent+"Abstract\n"
                    textcontent=textcontent+paper_metadata['abstract']+"\n\n"
                    for title, content in paper_content.items():
                        textcontent=textcontent+title+"\n"
                        textcontent=textcontent+content+"\n\n"
                    output_file.write(textcontent)

    return ""

def extract_paper_metadata(tree, namespaces):
    details = {}
    # Extracting paper title
    title_elem = tree.find('.//tei:title[@type="main"]', namespaces)
    details['title'] = title_elem.text if title_elem is not None else 'Not available'

    # Extracting authors
    authors = []
    for author_elem in tree.findall('.//tei:teiHeader//tei:author', namespaces):
        author = {}
        pers_name = author_elem.find('.//tei:persName', namespaces)
        if pers_name is not None:
            author['name'] = pers_name.findtext('.//tei:forename', namespaces=namespaces, default='Not available') + " " + pers_name.findtext('.//tei:surname', namespaces=namespaces, default='Not available')
        author['orcid'] = author_elem.findtext('.//tei:idno[@type="orcid"]', namespaces=namespaces, default='Not available')
        author['affiliation'] = author_elem.findtext('.//tei:affiliation/tei:orgName', namespaces=namespaces, default='Not available')
        authors.append(author)
    details['authors'] = authors

    abstract_elem = tree.find('.//tei:abstract', namespaces)
    abstract_text = etree.tostring(abstract_elem, method='text', encoding='unicode').strip() if abstract_elem is not None else 'Not available'
    details['abstract'] = abstract_text
    # Extracting DOI
    details['doi'] = tree.findtext('.//tei:idno[@type="DOI"]', namespaces=namespaces, default='Not available')

    # Extracting date published
    publication_date = tree.findtext('.//tei:date[@type="published"]', namespaces=namespaces, default='Not available')
    # Removing any non-date characters
    details['date_published'] = re.sub('[^0-9-]', '', publication_date)
    return details

def extract_paper_content(tree, ns):
    sections = {}
    # Iterate over each head tag in the body
    for head in tree.xpath('//tei:body/tei:div/tei:head', namespaces=ns):
        heading = head.text.strip() if head.text else "Unnamed Section"
        content = []

        # Find all the subsequent p tags until the next head tag
        for sibling in head.itersiblings():
            if sibling.tag == '{http://www.tei-c.org/ns/1.0}p':
                paragraph = sibling.xpath('string(.)', namespaces=ns).strip()
                content.append(paragraph)
            elif sibling.tag == '{http://www.tei-c.org/ns/1.0}head':
                break

        sections[heading] = "\n".join(content)

    return sections

def convert_tei_to_jats(tei_xml_path, output_path):
    with open(tei_xml_path, 'rb') as file:
        tei_xml = etree.XML(file.read())

    with open('teixml.xml', 'rb') as file:
        xslt = etree.XSLT(etree.XML(file.read()))

    jats_xml = xslt(tei_xml)

    
    return etree.tostring(jats_xml, pretty_print=True)