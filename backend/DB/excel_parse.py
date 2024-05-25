import asyncio
from io import BytesIO

import pandas

from DB.db import fill_db

# Columns form excel to use when parsing
COLUMNS = [0, 1, 2, 3, 4, 6, 14, 16, 17, 18, 26]

# Names to assign for DF, reference if adjusting columns for data parsing
COLUMN_NAMES = ["ENTRY_ID", "Year", "Professor_id", "WorkKind", "WorkKind2", "WorkKind3", "Description", "Surname",
                "Name", "Patronymic", "Department"]


async def get_df(contents: bytes):
    data = pandas.read_excel(BytesIO(contents), sheet_name=None, usecols=COLUMNS, names=COLUMN_NAMES)
    return data


async def process_data(data: dict):
    for pages in data.values():
        grouped = pages.groupby("Professor_id")
        for person_id, group_df in grouped:
            asyncio.create_task(fill_db(group_df))


async def main():
    data = await get_df()
    await process_data(data)
    # print(type(data['16-17'].iloc[0].Professor_id))


if __name__ == '__main__':
    asyncio.run(main())
