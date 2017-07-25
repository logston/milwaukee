import bs4
import requests
import urllib
import os
import glob
from subprocess import Popen, PIPE


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
    return resp.content


def parse_pdf(content):
    ps2ascii = Popen(['ps2ascii'], stdin=PIPE, stdout=PIPE,
            stderr=PIPE, shell=True)
    ps2ascii.stdin.write(content)
    ps2ascii.stdin.close()
    pdf_text = ps2ascii.stdout.read().decode()
    ps2ascii.stdout.close()
    ps2ascii.wait()
    return pdf_text


def main():
    with open('uniq_tax_keys.txt') as fp:
        tax_keys = [row.strip() for row in fp if row.strip()]

    with open('no-pull.txt') as fp:
        no_pull_tax_keys = set(row.strip() for row in fp if row.strip())

    for i, tax_key in enumerate(tax_keys, start=1):
        if tax_key in no_pull_tax_keys:
            continue

        percent_done = '{:3.2f}'.format((i / len(tax_keys)) * 100)
        print(percent_done, tax_key, end='...', flush=True)

        link = get_pdf_link_page_link(tax_key)
        if not link:
            print('No middle link found', flush=True)
            with open('no-pull.txt', 'a') as fp:
                fp.write(tax_key + '\n')
            continue

        pdf_link = get_pdf_link(link)
        if not pdf_link:
            print('No pdf link found', flush=True)
            with open('no-pull.txt', 'a') as fp:
                fp.write(tax_key + '\n')
            continue

        print('fetching pdf', end='...', flush=True)
        content = fetch_pdf(tax_key, pdf_link)

        print('parsing pdf', end='...', flush=True)
        text = parse_pdf(content)

        if 'delinquent' in text.lower():
            print('delinquent found, saving', end='...', flush=True)
            with open('pdfs/{}.pdf'.format(tax_key), 'wb') as fp:
                fp.write(content)
        else:
            print('up to date', end='...', flush=True)

        with open('no-pull.txt', 'a') as fp:
            fp.write(tax_key + '\n')
 
        print('Done.', flush=True)

main()


