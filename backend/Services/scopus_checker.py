import asyncio
import re
import requests
import os

from DB.models import WorkEntry, Report, WorkKind3

API_KEY = os.getenv('APIKEY')

WORKKIND3_STRING = ('Монографiї (роздiли), що опублiкованi у виданнях, якi включенi в Scopus або Web of Science Core '
                    'Collection')

CHECK_STRING = 'Перевірка на індексацію скопусом'



async def find_identifiers(entries):
    # Regular expressions for matching DOI, ISSN, and ISBN patterns
    doi_regex = r'\b(10\.\d{4,}(?:\.\d+)?\/\S+(?:(?!["&\'<>])\S)?)\b'
    issn_regex = r"\d{4}-\d{3}[\dXx]"
    isbn_regex = r'\b(?:ISBN(?:-10)?:? ?)?(?=[0-9X]{10}|(?:97[89])?[0-9]{9}[- ]?[0-9X])[- 0-9]{17}\b'

    found_identifiers = []
    entries_without_identifiers = []

    for entry in entries:
        entry_id, content = entry.id, entry.description
        found_doi = re.findall(doi_regex, content)
        found_issn = re.findall(issn_regex, content)
        found_isbn = re.findall(isbn_regex, content)

        if found_doi:
            found_identifiers.append({'entry_id': entry_id, 'type': 'DOI', 'identifier': found_doi})
        elif found_issn:
            found_identifiers.append({'entry_id': entry_id, 'type': 'ISSN', 'identifier': found_issn})
        elif found_isbn:
            found_identifiers.append({'entry_id': entry_id, 'type': 'ISBN', 'identifier': found_isbn})
        else:
            entries_without_identifiers.append(entry)

    return found_identifiers, entries_without_identifiers


async def check_scopus(found):
    reports = []
    for entry in found:
        r = requests.get(f"https://api.elsevier.com/content/search/scopus?apiKey={API_KEY}&query={entry['type']}({entry['identifier'][0]})")
        # search = ScopusSearch(f"{entry['type']}({entry['identifier'][0]})", subscriber=False)
        if r.json().get('search-results') and r.json().get('search-results').get('opensearch:totalResults') == '0':
            reports.append(Report(entry_id=entry['entry_id'], check_type=CHECK_STRING, result='Не підтвердженно'))
    await Report.bulk_create(reports)


async def start_scopus_check():
    workkind = await WorkKind3.get(name=WORKKIND3_STRING)
    entries = await WorkEntry.filter(workkind3_id=workkind.id)
    found, not_found = await find_identifiers(entries)
    check = asyncio.create_task(check_scopus(found))
    not_found_reports = [
        Report(entry_id=entry.id, check_type=CHECK_STRING,
               result='Не виявлено унікальний ідентифікатор (DOI/ISSN/ISBN)') for entry in not_found]
    await Report.bulk_create(not_found_reports)
    await check