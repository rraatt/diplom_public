import asyncio
import itertools
import string

from nltk import word_tokenize
from nltk.metrics.distance import jaccard_distance

from DB.models import WorkEntry, Professor, Report


async def duplication_check_starter():
    """Initiates check for duplicate entries.
    Groups of all works of every author based on workkinds and starts comparison
    """
    professors = await Professor.all()
    for professor in professors:
        work = await WorkEntry.filter(submitter=professor).order_by(
            'workkind_id', 'workkind2_id', 'workkind3_id'
        ).prefetch_related('submitter', 'workkind', 'workkind2', 'workkind3')
        grouped_entries = {}
        for entry in work:
            key = (entry.workkind_id, entry.workkind2_id, entry.workkind3_id)
            if key not in grouped_entries:
                grouped_entries[key] = []
            grouped_entries[key].append(entry)
        for values in grouped_entries.values():
            asyncio.create_task(check_for_duplicates(values))


async def check_for_duplicates(data: list):
    """Checks a group of entries for duplicate entries.
    Generates Report entries for further inspection"""
    combinations = itertools.combinations(data, 2)  # Change 2 to the desired combination length
    tasks = [compare(combination) for combination in combinations]
    results = await asyncio.gather(*tasks)
    reports = []
    for result in results:
        if result[0]:
            reports.append(Report(entry_id=result[1][0].id, check_type='Перевірка на дублікати',
                                  result='Виявленно схожі записи', duplicate_id=result[1][1].id))
    await Report.bulk_create(reports)


async def compare(combination):
    """Compares two entries description via jaccard distance.
    If similarity is over 0.8, entries are flagged as potential duplicates.
    Returns boolean result and duplicates ids"""
    string1 = combination[0].description
    string2 = combination[1].description
    result = False
    # Tokenize the strings into sets of words (you can tokenize them differently based on your needs)
    tokens1 = set(word_tokenize(string1.translate(str.maketrans('', '', string.punctuation))))
    tokens2 = set(word_tokenize(string2.translate(str.maketrans('', '', string.punctuation))))

    # Calculate the Jaccard distance between the sets of tokens
    jaccard_dist = jaccard_distance(tokens1, tokens2)

    # Calculate the Jaccard similarity (since distance is complementary to similarity)
    jaccard_sim = 1 - jaccard_dist
    if jaccard_sim >= 0.8:
        result = True
    return result, combination
