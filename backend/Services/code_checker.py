import asyncio

from DB.models import WorkEntry, Rada, Report
from Services.rada_parser import find_sequence

CHECK_STRING = 'Перевірка на участь у вченній раді'


def separate_entries(list_of_dicts, code_set):
    entries_in_set = []
    entries_not_in_set = []

    for d in list_of_dicts:
        code = next(iter(d))  # Extract the code from the dictionary
        if code in code_set:
            entries_in_set.append(d)
        else:
            entries_not_in_set.append(d)

    return entries_in_set, entries_not_in_set


async def check_rada_db(entries):
    """Checks if detected code is present in parsed db.
    returns a list of entries, that weren't found"""
    kpi_radas = await Rada.all()
    present_in_works = set()
    for d in entries:
        present_in_works.update(d.keys())
    kpi_codes = {entry.code for entry in kpi_radas}
    common_codes = present_in_works.intersection(kpi_codes)
    in_rada_db, not_in_db = separate_entries(entries, common_codes)
    asyncio.create_task(check_participation(in_rada_db))
    return not_in_db


async def check_participation(entries):
    """Checks if entry submitter is mentioned on rada.kpi page regarding the academic council"""
    reports = []
    for entry in entries:
        entry_code = next(iter(entry.keys()))
        entry = next(iter(entry.values()))
        entry_author = await entry.submitter
        rada_entry = await Rada.get(code=entry_code)
        if not entry_author.get_full_name().replace(" ", "") in rada_entry.content:
            reports.append(Report(entry_id=entry.id, check_type=CHECK_STRING, result='Не підтвердженно'))
    await Report.bulk_create(reports)


async def check_codes():
    """Initiates check for academic councils codes and checks submitters participation
    in the council, if council was held in KPI and was posted on rada.kpi website.
    Creates Report entries in database for further inspection
    """
    rada_codes = []
    async for entry in WorkEntry.all():
        sequence = find_sequence(entry.description)
        if sequence:
            rada_codes.append({sequence.replace(" ", ""): entry})
    not_in_db = await check_rada_db(rada_codes)
    reports = []
    for entry in not_in_db:
        reports.append(Report(entry_id=next(iter(entry.values())).id, check_type=CHECK_STRING, result='Не знайдено у списку вчених рад'))
    await Report.bulk_create(reports)


# async def transform_rada():
#     entries = []
#     async for entry in Rada.all():
#         entry.content = entry.content.replace(" ", "")
#         entries.append(entry)
#     await Rada.bulk_update(entries, fields=['content'])