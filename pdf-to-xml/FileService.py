from dotenv import load_dotenv
import os
from lxml import etree
import xml.etree.ElementTree as ET
from lxml.builder import E
import re
import requests
load_dotenv()

def process_file(pdf_path):
    GROBID_API_URL = 'http://localhost:8070/api/processFulltextDocument'#os.getenv('GROBID_API_URL')
    files = {'input': open(pdf_path, 'rb')}
    response = requests.post(GROBID_API_URL, files=files)
    
    if response.status_code == 200:
        xml_tree = etree.fromstring(response.content)
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        paper_content = extract_paper_content(xml_tree, ns)
        paper_metadata = extract_paper_metadata(xml_tree, ns)
        return prepare_xml(paper_metadata, paper_content)
        
    else:
        raise Exception(f"Error processing file: {response.status_code} {response.reason}")

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

'''
def prepare_xml(paper_metadata, paper_content):
    article = ET.Element("article")

    # Add title group with article title
    title_group = ET.SubElement(article, "title-group")
    article_title = ET.SubElement(title_group, "article-title")
    article_title.text = paper_metadata['title']

    # Add body of the article
    body = ET.SubElement(article, "body")

    # Populate the XML structure with sections
    for title, content in paper_content.items():
        sec = ET.SubElement(body, "sec")
        title_elem = ET.SubElement(sec, "title")
        title_elem.text = title
        p_elem = ET.SubElement(sec, "p")
        p_elem.text = content

    # Convert the XML structure to a string
    # Note: The root of the ElementTree should be 'article', not 'body'
    tree = ET.ElementTree(article)
    xml_str = ET.tostring(article, encoding='unicode')

    return xml_str
'''

def prepare_xml(extracted_details, paper_content):
    jats_article = E.article(
    E.front(
        E('article-meta',
            E('title-group', 
                E('article-title', extracted_details['title'])
            ),
            E('contrib-group',
                *[E('contrib', {'contrib-type': 'author'},
                    E('name',
                        E('surname', author['name'].split()[-1]),
                        E('given-names', ' '.join(author['name'].split()[:-1]))),
                    E('xref', {'ref-type': 'aff'}, author['affiliation']),
                    E('contrib-id', author['orcid'], {'contrib-id-type': 'orcid'})
                  ) for author in extracted_details['authors']
                ]
            ),
            E('pub-date', extracted_details['date_published'], {'pub-type': 'epub'}),
            E('article-id', extracted_details['doi'], {'pub-id-type': 'doi'})
        )
    ),
    E('abstract', 
        E('p', extracted_details['abstract'])
    )
)
    body = E.body()
    for title, content in paper_content.items():
        section = E('sec',
                  E('title', title),
                  E('p', content))
        body.append(section)

    # Adding the body to the JATS XML structure
    jats_article.append(body)

# Pretty printing the updated JATS XML
    return etree.tostring(jats_article, pretty_print=True, encoding='unicode')
    #return etree.tostring(jats_article, pretty_print=True, encoding='unicode')


def get_paper_metadata_with_crossref(doi):
    print(CROSSREF_API_URL)
    crossref_api_url = f"{CROSSREF_API_URL}/{doi}"
    response = requests.get(crossref_api_url)
    response.raise_for_status()  # Raises an HTTPError if the response was unsuccessful

    data = response.json()['message']
    print(data)
    # Create a simple JATS-like XML structure
    article = ET.Element("article")

    # Add title
    article_title = ET.SubElement(article, "article-title")
    article_title.text = data.get('title', [''])[0]

    # Add authors
    authors = ET.SubElement(article, "authors")
    for author in data.get('author', []):
        author_element = ET.SubElement(authors, "author")
        given_name = ET.SubElement(author_element, "given-name")
        given_name.text = author.get('given', '')
        family_name = ET.SubElement(author_element, "family-name")
        family_name.text = author.get('family', '')

    # Add publication date
    published_date = ET.SubElement(article, "published-date")
    date_parts = data.get('published-print', data.get('published-online', {})).get('date-parts', [[]])[0]
    published_date.text = '-'.join(map(str, date_parts))  # Format: YYYY-MM-DD

    publisher = ET.SubElement(article, "publisher")
    publisher.text = data.get('publisher', [''])

    DOI = ET.SubElement(article, "DOI")
    DOI.text = doi

    article_type = ET.SubElement(article, "article-type")
    article_type.text = data.get('type', [''])

    # Convert the XML structure to a string
    return ET.tostring(article, encoding='unicode')