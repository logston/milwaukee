import bs4
import requests
import urllib
import os


URL = 'http://assessments.milwaukee.gov/'
PDF_URL = 'http://itmdapps.milwaukee.gov/taxAccountBalance/TaxBalServlet'


def get_pdf_link_page_link(tax_key):
    resp = requests.get(URL + 'remast.asp?taxkey={}'.format(tax_key))
    soup = bs4.BeautifulSoup(resp.content.decode(), 'html.parser')
    tax_balance_links = soup.find_all('a', text='Tax Balance')
    if tax_balance_links:
        return tax_balance_links[0]['href']

    return None


def get_pdf_link(link):
    resp = requests.get(link)
    soup = bs4.BeautifulSoup(resp.content.decode('latin-1'), 'html.parser')
    links = soup.find_all('a', href='#', onclick="SUBMITTHIS(this)")
    if links:
        link = links[0]
        query_data = {
            'ichkdgt': link['data_ichkdgt'],
            'itaxkey': link['data_itaxkey'],
            'isubacct': link['data_isubacct'],
            'ismonth': link['data_ismonth']
        }
        query = urllib.parse.urlencode(query_data)
        return PDF_URL + '?' + query

    return None


def fetch_pdf(tax_key, pdf_link):
    resp = requests.get(pdf_link)
    with open('/Volumes/JetDrive/pdfs/{}.pdf'.format(tax_key), 'wb') as fp:
        fp.write(resp.content)


def main():
    with open('uniq_tax_keys.txt') as fp:
        tax_keys = [row.strip() for row in fp if row.strip()]

    #tax_keys = ['5570902000']
    for i, tax_key in enumerate(tax_keys, start=1):
        if os.path.exists('/Volumes/JetDrive/pdfs/{}.pdf'.format(tax_key)):
            continue

        percent_done = '{:3.2f}'.format((i / len(tax_keys)) * 100)
        print(percent_done, tax_key, end='...', flush=True)

        link = get_pdf_link_page_link(tax_key)
        if not link:
            print('No middle link found', flush=True)
            continue

        pdf_link = get_pdf_link(link)
        if not pdf_link:
            print('No pdf link found', flush=True)
            continue

        print('fetching pdf', end='...', flush=True)
        fetch_pdf(tax_key, pdf_link)
        print('Done.', flush=True)

main()

