import asyncio
import string
import re
import aiohttp
from bs4 import BeautifulSoup

from DB.models import Rada


async def fetch_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


def find_sequence(text):
    """Check for Academic Councils code via regex"""
    pattern = r'(?<!\d)(?:[\u0400-\u04FF]{1,2})?[.\s]?\d{2}\.\d{3}\.\d{1,3}(?!\d)'

    # Find all matches in the text using the regular expression
    matches = re.findall(pattern, text)
    if matches:
        return matches[0]
    return None


async def parse_node(link):
    html = await fetch_html(link)
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find('div', class_='field-item even', property='content:encoded')
    await Rada.create(code=find_sequence(div.text).replace(" ", ""),
                      content=div.text.translate(str.maketrans('', '', string.punctuation)).replace(' ', ''))


async def parse_list(url_list):
    for url in url_list:
        await asyncio.sleep(30)
        await parse_node(url)


async def parse_rada():
    await Rada.all().delete()
    url = 'https://rada.kpi.ua/node/1148'
    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find('div', class_='field-item even', property='content:encoded')
    links = []
    # Iterate over all <p> tags within the div
    for p_tag in div.find_all('p'):
        # Find all <a> tags within the <p> tags
        for a_tag in p_tag.find_all('a'):
            # Get the URL from the href attribute of the <a> tag
            links.append(a_tag['href'])
            # Print the URL
    await asyncio.create_task(parse_list(links))
