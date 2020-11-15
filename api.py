import requests
from locations import id_map

# api information
VALID_ACTIONS = ('inventory', 'multi_inventory')
API_BASE = 'https://shop.trulieve.com/mjf/index.php?action='

# http status codes
STATUS_OK = 200


def query(action='multi_inventory', sku='', location_id=None):
    if action not in VALID_ACTIONS:
        return TypeError(f'Invalid action: {action}')

    if not sku:
        return TypeError('SKU cannot be empty!')

    arguments = ''
    if action == 'inventory':  # seems like this action has been deprecated, doesn't return anything
        if location_id is None:
            return TypeError('Invalid location ID.')
        elif location_id not in id_map:
            return NotImplemented(f'Unhandled location ID: {location_id}')

        arguments += f'&mjf_location_id={location_id}'

    arguments += f'&mjf_sku={sku}'

    request = requests.get(API_BASE + action + arguments)
    if request.status_code != STATUS_OK:
        return ValueError(f'Invalid HTTP response: {request.status_code}')

    return request.json()


if __name__ == '__main__':  # debugging
    resp = query(sku='FINP-0072')

    ids = []
    for pair in resp:
        _id = pair['id']
        if _id not in id_map:
            continue

        stock = pair["stock"]
        if stock <= 0:
            stock = 'OUT OF STOCK'

        listing = f'{id_map[_id]}: {stock}'
        print(listing)
