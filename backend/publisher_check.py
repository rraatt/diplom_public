import re
from datetime import date
from pypdf import PdfReader
from DB.models import MoEPublishers

def extract_date_from_filename(filename):
    match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', filename)
    if match:
        day, month, year = map(int, match.groups())
        return date(year, month, day)
    else:
        return None

async def store_pdf(file_name):
    reader = PdfReader(file_name)
    content = ""
    for page in range(len(reader.pages)):
        content = content + reader.pages[page].extract_text().translate(str.maketrans('', '', '\n'))
    entry_date = extract_date_from_filename(file_name)
    entry = await MoEPublishers.create(content=content, date=entry_date)


# print(crossref_commons.retrieval.get_publication_as_json('ISBN 978-617-7506-24-8'))


