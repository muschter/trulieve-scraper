import requests
from bs4 import BeautifulSoup
from api import query
from locations import id_map

# ALL VALID PAGES, grabs all items from each URL
SCRAPE_PAGES = [
    'https://shop.trulieve.com/featured?product_list_limit=all',
    'https://shop.trulieve.com/flower?product_list_limit=all',
    'https://shop.trulieve.com/concentrate?product_list_limit=all',
    'https://shop.trulieve.com/vape-carts?product_list_limit=all',
    'https://shop.trulieve.com/edibles?product_list_limit=all',
    'https://shop.trulieve.com/oral?product_list_limit=all',
    'https://shop.trulieve.com/topicals?product_list_limit=all'
]


ITEM_LINKS = []

for page in SCRAPE_PAGES:
    page_req = requests.get(page)
    soup = BeautifulSoup(page_req.text, 'html.parser')
    inventory_items = soup.find_all('a', {'class': 'product-item-photo'})

    ITEM_LINKS.extend([item.attrs['href'] for item in inventory_items if item.attrs.get('href')])


ITEM_LINKS = set(ITEM_LINKS)  # remove duplicates
for item_link in ITEM_LINKS:
    req = requests.get(item_link)
    if req.status_code != 200:
        continue

    parser = BeautifulSoup(req.text, 'html.parser')
    sku_element = parser.find('p', {'class': 'product-sku'})
    if not sku_element:
        continue

    sku_id = sku_element.text.strip('SKU ')
    # we now have the SKU, we can figure out where it's in stock
    stock = query(sku=sku_id)
    in_stock_locations = []
    for pair in stock:
        _id = pair['id']
        if _id not in id_map:
            continue

        quantity = pair['stock']
        if quantity <= 0:
            continue

        in_stock_locations.append(id_map[_id])

    if in_stock_locations:
        info = f'Available at: {", ".join(in_stock_locations)}'
    else:
        info = '*Out of stock STATEWIDE*'

    print(sku_id, info)
