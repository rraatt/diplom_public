import asyncio
import re

from DB.models import WorkKind3, WorkEntry, ReestrEntry, Report

CHECK_STRING = 'Перевірка на фаховість видання'

WORKKIND3_STRING = 'включених до переліку наукових фахових видань України'


def get_issn(entry):
    issn_regex = r"\d{4}-\d{3}[\dXx]"
    found_issn = re.findall(issn_regex, entry)
    return found_issn


async def check_issn_code_present(issn_codes):
    final_result = False
    for issn in issn_codes:
        # Query to check if the ISSN code is present in any of the entries
        query = ReestrEntry.filter(codes__icontains=issn)
        # Execute the query
        result = await query.exists()
        if result:
            final_result = True
    return final_result


async def check_fachovist(present_issn):
    reports = []
    for id in present_issn:
        if not await check_issn_code_present(present_issn[id]):
            reports.append(Report(entry_id=id, check_type=CHECK_STRING,
                                  result='Фаховість видання не підтвердженно'))
    await Report.bulk_create(reports)


async def start_fach_check():
    workkind = await WorkKind3.get(name=WORKKIND3_STRING)
    entries = await WorkEntry.filter(workkind3_id=workkind.id)
    no_issn = []
    present_issn = {}
    for entry in entries:
        issn = get_issn(entry.description)
        if issn:
            present_issn[entry.id] = issn
        else:
            no_issn.append(Report(entry_id=entry.id, check_type=CHECK_STRING, result='Не знайдено ISSN'))
    asyncio.create_task(check_fachovist(present_issn))
    await Report.bulk_create(no_issn)
