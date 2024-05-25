from DB.models import Professor, WorkKind, WorkKind2, WorkKind3, WorkEntry


async def fill_db(group):
    """Function to fill entries of one professor, accepts a dataframe segment with one professor id,
    if professor doesn't exist in the database creates a new entry,
    utilizes id of professor and id of entry from original Excel file"""
    first_entry = group.iloc[0]
    submitter, _ = await Professor.get_or_create(id=first_entry.Professor_id, name=first_entry.Name,
                                                 surname=first_entry.Surname, patronymic=first_entry.Patronymic,
                                                 department=first_entry.Department)
    instances = []
    for _, entry in group.iterrows():
        workkind, _ = await WorkKind.get_or_create(name=entry.WorkKind)
        workkind2, _ = await WorkKind2.get_or_create(name=entry.WorkKind2)
        workkind3, _ = await WorkKind3.get_or_create(name=entry.WorkKind3)
        # Create instances of your Tortoise model for each row in the DataFrame
        instance = WorkEntry(id=entry.ENTRY_ID, submitter_id=submitter.id, workkind_id=workkind.id,
                             workkind2_id=workkind2.id, workkind3_id=workkind3.id,
                             description=entry.Description, year=entry.Year)
        instances.append(instance)
    try:
        await WorkEntry.bulk_create(instances)
    except Exception as e:
        print("An error occurred during bulk creation:", e)
