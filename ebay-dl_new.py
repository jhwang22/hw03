#libraries
import argparse
import requests
from bs4 import BeautifulSoup
import json

def parse_itemssold(text):
    # takes as input string, returns number of items sold as stated in string
    num = ''
    for char in text:
        if char in '1234567890':
            num += char
    if 'sold' in text:
        return int(num)
    else:
        return 0


def parse_price(text):
    #return price in input text as integer number of cents. No price present -> return 0:
    if '$' not in text:
        return 0
    #extract numbers
    dollar = text.find('$')
    space = text.find(' ')
    text_price = text[dollar:space] if space != -1 else text[dollar:]

    num = ''
    for char in text_price:
        if char in '1234567890':
            num += char
    return int(num)
    
        
if __name__ == '__main__':

    #get command line arguments
    parser = argparse.ArgumentParser(description='Download information from ebay and convert to JSON.')
    parser.add_argument('search_term')
    parser.add_argument('--num_pages', default = 10)
    args = parser.parse_args()
    print('args.search_term=', args.search_term)

    # empty variable for list of items found on all web pages
    items = []

    #loopty loop over ebay pages
    for page_number in range(1, int(args.num_pages)+1):
        #build url
        url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw='
        url += args.search_term 
        url += '&_sacat=0&rt=nc&_pgn=' 
        url += str(page_number)
        print('url=', url)

        #download html
        r = requests.get(url)
        status = r.status_code
        print('status=', status)
        html = r.text

        # html bs4 processing
        # needed info: --
        soup = BeautifulSoup(html, "html.parser")
        #loop over all items in page
        tags_items = soup.select('.s-item')
        for tag_item in tags_items:

            name = None
            tags_name = tag_item.select('.s-item__title')
            for tag in tags_name:
                name = tag.text

            freereturns = False
            tags_returns = tag_item.select('.s-item__free-returns')
            for tag in tags_returns:
                freereturns = True

            
            price = None
            tags_price = tag_item.select('.s-item__price')
            for tag in tags_price:
                price = parse_price(tag.text)

            
            status = None
            tags_status = tag_item.select('.SECONDARY_INFO')
            for tag in tags_status:
                condition = tag.text

            
            shipping = 0
            tags_shipping = tag_item.select('.s-item__shipping')
            for tag in tags_shipping:
                shipping = parse_price(tag.text)


            items_sold = None
            tags_itemssold = tag_item.select('.s-item__hotness')
            for tag in tags_itemssold:
                items_sold = parse_itemssold(tag.text)

            #make library
            item = {
                'name': name,
                'free_returns': freereturns,
                'items_sold': items_sold,
                'status': status,
                'price': price,
                'shipping': shipping
            }
            items.append(item)

          
        #status-monitoring print statements
        print('len(tag_items)=', len(tags_items))
        print('len(items)=', len(items))
        #for item in items:
        #    print('item=', item)



    #write the json file
    filename = args.search_term+'.json'
    with open(filename, 'w', encoding='ascii') as f:
        f.write(json.dumps(items))