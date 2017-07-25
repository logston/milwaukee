import bs4
import requests


URL = 'http://assessments.milwaukee.gov/'


def get_html(addr):
    data = {
        'proptype': 'RE',
        'userdata': addr,
        'imagesubmit.x': '19',
        'imagesubmit.y': '11',
    }
    resp = requests.post(URL + 'querydb.asp', data=data)
    return resp.content.decode()


def get_page_links(html):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return [link['href'] for link in soup.find_all('a')]


def get_tax_keys(page_links):
    tax_keys = []
    next_link = None

    for link in page_links:
        if link.startswith('remast.asp?taxkey='):
            tax_keys.append(link[18:])

        if link.startswith('addrlkp.asp'):
            next_link = link

    return tax_keys, next_link


def main():
    with open('milwaukee.high_low') as fp:
        addrs = [row.strip() for row in fp]

    #addrs = '200 9301 W Manor',

    all_tax_keys = []
    for addr in addrs:
        html = get_html(addr)
        links = get_page_links(html)
        next_link = True
        while next_link:
            tax_keys, next_link = get_tax_keys(links)
            for tax_key in tax_keys:
                print(tax_key, flush=True)
            all_tax_keys.extend(tax_keys)
            if next_link:
                resp = requests.get(URL + next_link)
                html = resp.content.decode()
                links = get_page_links(html)

main()

