from tortoise.queryset import QuerySet


def paginate(query, page_number: int, page_size: int):
    offset = (page_number - 1) * page_size
    limit = page_size
    return query.offset(offset).limit(limit)


def calculate_total_pages(total_count: int, page_size: int) -> int:
    return (total_count + page_size - 1) // page_size  # Rounds up the division


def filter_queryset(queryset, filters: str) -> QuerySet:

    if not filters:
        return queryset

    query_filters = {}
    parsed_filters = filters.split('%%')
    for string in parsed_filters:
        key, value = string.split('@@@')
        if key == 'entry__submitter__full_name':
            if len(value.split(' ')) == 1:
                query_filters['entry__submitter__name__icontains'] = value
            elif len(value.split(' ')) == 2:
                name, surname = value.split(' ')
                query_filters['entry__submitter__name__icontains'] = name
                query_filters['entry__submitter__surname__icontains'] = surname
            elif len(value.split(' ')) == 3:
                name, surname, patronymic = value.split(' ')
                query_filters['entry__submitter__name__icontains'] = name
                query_filters['entry__submitter__surname__icontains'] = surname
                query_filters['entry__submitter__patronymic__icontains'] = patronymic
        else:
            query_filters[key] = value

    return queryset.filter(**query_filters)
