from core import app, config, session
from os import path
from bs4 import BeautifulSoup
from flask import request
from source.static.static_methods import path_to_url
import json
from source.api.exceptions import *
import asyncio
import concurrent.futures
from datetime import datetime
import re

teams_path = path.join(config['url_prefix'], 'teams', 'get')


async def get_teams_pages(count=50, year=2020, country=""):
    temp_data = list()

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                session.get,
                f'https://ctftime.org/stats/{year}/{country.upper()}?page={_}'
            )
            for _ in range(1, (count // 50) + 1 if count // 50 != 0 else 2)
        ]
        for response in await asyncio.gather(*futures):
            temp_data.append(response)

    return temp_data


# Official method
def get_team_by_id(id):
    return json.loads(session.get(f'https://ctftime.org/api/v1/teams/{id}/').text)


@app.route(path_to_url(path.join(teams_path, 'top', '<year>', '<country>', '<count>')), methods=['GET'])
def get_top_teams_by_country(year, country, count):
    absolute_data = list()

    try:
        if 1 > int(count) < 1000 or 2000 > int(year) > datetime.now().year:
            raise BaseException
    except:
        return IncorrectInput(request.remote_addr, [year, country.upper(), count]).message()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for x in loop.run_until_complete(get_teams_pages(int(count), year, country)):
        if x.status_code != 200:
            break
        soup = BeautifulSoup(x.text, 'html.parser')

        table = soup.find('table', attrs={'class': 'table'})
        rows = table.find_all('tr')[1:]
        absolute_data.append(rows)

    absolute_data = [item for sublist in absolute_data for item in sublist][0:int(count)]

    data = list()

    for row in absolute_data:
        _ = list([x for x in row.find_all('td') if x.text])
        data.append({'world_place': _[0].text, 'country_place': _[1].text, 'name': _[2].text, 'points': _[3].text,
                     'events': _[4].text})

    return json.dumps({'count': len(absolute_data),
                       'content': data
                       })


@app.route(path_to_url(path.join(teams_path, 'top', '<year>', '<count>')), methods=['GET'])
def get_top_teams(year, count):
    absolute_data = list()

    try:
        if 1 > int(count) < 1000 or 2000 > int(year) > datetime.now().year:
            raise BaseException
    except:
        return IncorrectInput(request.remote_addr, [year, count]).message()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for x in loop.run_until_complete(get_teams_pages(int(count), year)):
        if x.status_code != 200:
            break
        soup = BeautifulSoup(x.text, 'html.parser')

        table = soup.find('table', attrs={'class': 'table'})
        rows = table.find_all('tr')[1:]
        absolute_data.append(rows)

    absolute_data = [item for sublist in absolute_data for item in sublist][0:int(count)]

    data = list()

    for row in absolute_data:
        _ = list([x for x in row.find_all('td') if x.text or x.find('a')])
        try:
            data.append({'world_place': _[0].text, 'name': _[1].text, 'country': _[2].find('a').find('img').get('alt'),
                         'points': _[3].text,
                         'events': _[4].text})
        except AttributeError:
            data.append({'world_place': _[0].text, 'name': _[1].text, 'country': 'None',
                         'points': _[2].text,
                         'events': _[3].text})

    return json.dumps({'count': len(absolute_data),
                       'content': data
                       })


@app.route(path_to_url(path.join(teams_path, 'team', '<id>', '<type>')), methods=['GET'])
def get_team(id, type):
    if type != 'name' and type != 'id':
        return IncorrectInput(ip=request.remote_addr, data=[id, type]).message('Type must be "name" or "id"')

    # Get CSRF token for the POST request
    soup = BeautifulSoup(session.get('https://ctftime.org/stats/2020/RU?page=1').text, 'html.parser')
    csrf = soup.find(attrs={"name": "csrfmiddlewaretoken"}).get('value')

    name = None

    if type == 'id':
        try:
            name = get_team_by_id(id)['name']
        except:
            return IncorrectInput(ip=request.remote_addr, data=[id, type]).message('Incorrect ' + type)
    else:
        name = id

    repl = session.post('https://ctftime.org/team/list/', {'csrfmiddlewaretoken': csrf, 'team_name': name})

    if repl.url == 'https://ctftime.org/team/list/' :
        return IncorrectInput(ip=request.remote_addr, data=[id, type]).message('Incorrect ' + type)

    soup = BeautifulSoup(
        repl.text,
        'html.parser')

    if type == 'name':
        id = str(repl.url).replace('https://ctftime.org/team/', '')

    # Current country place
    country_place = soup.find('a', href=re.compile(r'/stats/[A-Z]+')).find(text=re.compile(r'[0-9]+'))

    data = get_team_by_id(id)
    data['country_place'] = country_place

    return json.dumps(data)


