import asyncio
from DB.models import ReestrEntry
import aiohttp
from bs4 import BeautifulSoup


async def parse_reestr():
    await ReestrEntry.all().delete()
    page = 1
    url = f'https://nfv.ukrintei.ua/search?page={page}'
    headers = {'User-Agent': 'Mozilla/5.0', 'Cookie': 'itemsOnPage=100;'}
    response, xsrf_token_cookie = await fetch_html(url, headers=headers)

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Cookie': f'XSRF-TOKEN={xsrf_token_cookie}; itemsOnPage=100;',
    }

    await parse_page(response)

    soup = BeautifulSoup(response, 'lxml')
    # Find the last page item link
    last_page_item = soup.find_all('li', class_='page-item')[-2]  # The last element before the "Next" link

    # Get the URL of the last page item
    last_page = last_page_item.find('a').string
    tasks = []

    for i in range(1, int(last_page)):
        page = i + 1
        url = f'https://nfv.ukrintei.ua/search?page={page}'
        response, xsrf_token_cookie = await fetch_html(url, headers=headers)
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Cookie': f'XSRF-TOKEN={xsrf_token_cookie}; itemsOnPage=100;',
        }
        tasks.append(asyncio.create_task(parse_page(response)))
    await asyncio.gather(*tasks)


async def parse_page(response):
    entries = []
    soup = BeautifulSoup(response, 'lxml')
    search_block_elements = soup.find_all('div', attrs={'name': 'searchBlockElement'})

    for block in search_block_elements:
        name_search_text = block.find('div', {'name': 'nameSearchMain'}).find('a').string.strip()

        # Extracting ISSN text
        issn_texts = block.find('div', {'name': 'issnSearchMain'}).find_all('span', {'name': 'fontColorSearch'})
        issn_search_texts = [issn_text.b.string.strip() for issn_text in issn_texts]

        # Extracting Категорiя text
        category_text = block.find('div', {'name': 'galuzSearchMain'}).find('i',
                                                                            string='Категорiя: ').find_next_sibling(
            'span', {'name': 'fontColorSearch'}).string.strip()

        if category_text != 'НЕФАХОВЕ':
            entries.append(ReestrEntry(name=name_search_text, codes=' '.join(issn_search_texts)))
    await ReestrEntry.bulk_create(entries)


async def fetch_html(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html = await response.text()
            xsrf_token_cookie = response.cookies.get('XSRF-TOKEN')
            return html, xsrf_token_cookie


if __name__ == '__main__':
    asyncio.run(parse_reestr())
