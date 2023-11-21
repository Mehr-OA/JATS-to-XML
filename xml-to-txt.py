import os
import os.path
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup 

def read_xml_files():
    print('reading xml files')
    file = open('../xml-files/2023-11-01T14_07_32_manifest.txt', 'r')
    lines = file.readlines()
    for line in lines:
        xml_files = line.split(',')
    
    for entry in xml_files:
        xml_to_text(entry)

def xml_to_text(xml_file):

    with open('../xml-files/'+xml_file, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    soup = BeautifulSoup(xml_content, 'xml')

    extracted_content = []

    titles = soup.find_all('title')

    for title in titles:
        
        title_text = title.get_text(strip=True)
        extracted_content.append(title_text)

        next_tag = title.find_next_sibling()

        while next_tag and next_tag.name != 'title':
            if next_tag.name == 'p':
                extracted_content.append(next_tag.get_text(strip=True))
            next_tag = next_tag.find_next_sibling()

    file_name = os.path.basename(xml_file)
    output_file=os.path.splitext(file_name)[0]+'.txt'
    with open('output/'+output_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(extracted_content))
      
def main():
    read_xml_files()

if __name__ == "__main__":
    main()
