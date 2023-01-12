import os
import json
import time
import urllib
from termcolor import colored
from dotenv import load_dotenv
from gw2api import GuildWars2Client
from prettytable import PrettyTable

import utils.lib

load_dotenv()
os.system('color')
LANG = os.getenv('LANG')
REFRESH = int(os.getenv('REFRESH'))
GROUPED = os.getenv('GROUPED')
GW2_API_KEY = os.getenv('GW2_API_KEY')
client = GuildWars2Client(api_key=GW2_API_KEY, lang=LANG)


def log(text):
    print('\r'+text, end='\x1b[1K')


def calc_stats(config, item):
    name, value = item['name'], item['value']
    needed = config.get(str(item['id']))
    progress_value = value / needed * 100
    progress = format(min(progress_value, 100), '.2f')
    done = progress_value >= 100
    color = 'green' if done else 'red'
    sort_value = value * 100 if done else progress_value
    return {
        'name': str(name),
        'value': str(value)+'/'+str(needed),
        'progress': str(progress).rjust(6)+'%',
        'color': str(color),
        '_sort_value_': sort_value,
    }


def calc_all_stats(config, items):
    all_stats = []
    for item in items:
        stats = calc_stats(config, item)
        all_stats.append(stats)
    return all_stats


def resolve_material(material):
    item = client.items.get(id=material['id'])
    return {'id': material['id'], 'name': item['name'], 'value': material['count']}


def resolve_currency(currency):
    item = client.currencies.get(id=currency['id'])
    return {'id': currency['id'], 'name': item['name'], 'value': currency['value']}


def sum_materials(materials, more_materials):
    all_materials = {}
    for material in materials:
        all_materials[material['id']] = material
    for more_material in more_materials:
        if more_material['id'] in all_materials:
            all_materials[more_material['id']]['count'] += more_material['count']
        else:
            all_materials[more_material['id']] = more_material
    return list(all_materials.values())


def get_all_characters_inventory():
    all_items = {}
    characters = client.characters.get()
    for character in characters:
        log(f"[4/8]: Retrieving character inventory of {character}...")
        url = client.BASE_URL + '/v2/characters/' + urllib.parse.quote(character) + '/inventory'
        inventory = client.characters.get(url=url)
        for bag in inventory['bags']:
            for item in bag['inventory']:
                if item is not None:
                    if item['id'] in all_items:
                        all_items[item['id']]['count'] += item['count']
                    else:
                        all_items[item['id']] = item
    return list(all_items.values())


def get_material_items(collecting):
    log('[3/8]: Retrieving shared account inventory...')
    shared_inventory = client.accountinventory.get()
    shared_inventory = list(filter(lambda material: material is not None and str(material['id']) in collecting, shared_inventory))

    log('[4/8]: Retrieving character inventories...')
    characters_inventory = get_all_characters_inventory()
    characters_inventory = list(filter(lambda material: material is not None and str(material['id']) in collecting, characters_inventory))

    log('[5/8]: Retrieving account bank vault...')
    bank = client.accountbank.get()
    bank = list(filter(lambda material: material is not None and str(material['id']) in collecting, bank))

    log('[6/8]: Retrieving account vault...')
    materials = client.accountmaterials.get()
    materials = list(filter(lambda material: material is not None and str(material['id']) in collecting, materials))

    log('[7/8]: Merging all relevant items...')
    all_materials = sum_materials(materials, bank)
    all_materials = sum_materials(all_materials, characters_inventory)
    all_materials = sum_materials(all_materials, shared_inventory)

    log('[8/8]: Resolving all item names...')
    all_materials = map(resolve_material, all_materials)
    return all_materials


def get_currency_items(collecting):
    log('[1/8]: Retrieving relevant account wallet currencies...')
    currencies = client.accountwallet.get()
    currencies = filter(lambda currency: str(currency['id']) in collecting, currencies)

    log('[2/8]: Resolving all currency names...')
    items = map(resolve_currency, currencies)
    return items


def verify_token():
    tokeninfo = client.tokeninfo.get()
    if 'text' in tokeninfo:
        raise ValueError(tokeninfo['text'])
    permissions_needed = ['account', 'characters', 'inventories', 'wallet']
    permissions_given = tokeninfo['permissions']
    if not set(permissions_needed).issubset(permissions_given):
        raise ValueError(
            'Insufficient permissions: Set your API key permissions to at least: ' + str(permissions_needed))


def load_config(configurations):
    try:
        for conf_id, conf_name in enumerate(configurations):
            print(f"Choose ID: {conf_id} for {conf_name}.")
        choosed_configuration = int(input("Enter the ID corresponding the the configuration to load: "))
        with open(f'./configurations/{configurations[choosed_configuration]}') as file:
            return json.load(file)
    except Exception as e:
        print(e)
        raise ValueError(f'Invalid config: {configurations[choosed_configuration]}')


def pretty_print_stats(all_stats, title="Name"):
    all_stats.sort(reverse=True, key=lambda stats: stats['_sort_value_'])
    field_names = [
        colored(title, attrs=["bold"]),
        colored("Value", attrs=["bold"]),
        colored("Progress", attrs=["bold"]),
    ]
    table = PrettyTable(field_names)
    table.align = "r"
    table.align[field_names[0]] = "l"
    for stats in all_stats:
        table.add_row([stats['name'], stats['value'], colored(stats['progress'], stats['color'])])
    print(table)


def pause(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        log(f'(Refreshing in {timer})')
        time.sleep(1)
        t -= 1
    log('Refreshing...')


if __name__ == '__main__':
    print()
    configs = utils.lib.get_available_config()
    verify_token()
    config = load_config(configs)

    while True:
        currency_items = get_currency_items(config['currencies'])
        currency_stats = calc_all_stats(config['currencies'], currency_items)
        material_items = get_material_items(config['materials'])
        material_stats = calc_all_stats(config['materials'], material_items)

        print(colored("\rActive config: ", attrs=["bold"]) + config['description'] + " by " + config['author'])
        if GROUPED.lower() == 'true':
            pretty_print_stats(currency_stats, "Currency")
            pretty_print_stats(material_stats, "Materials")
        else:
            pretty_print_stats(currency_stats + material_stats)
        print("Rerun this Script to manually update stats.\n")

        if REFRESH > 0:
            pause(REFRESH)
        else:
            break






