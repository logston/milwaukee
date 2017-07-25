import csv
import collections


with open('milwaukee.csv') as fp:
    reader = csv.DictReader(fp)
    rows = list(reader)

def get_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

master = collections.defaultdict(dict)
for row in rows:
    fullname = row.get('fullname')
    fullname = ' '.join(list(fullname.split()[:-1]))
    lfromadd = get_int(row.get('lfromadd'))
    ltoadd = get_int(row.get('ltoadd'))
    rfromadd = get_int(row.get('rfromadd'))
    rtoadd = get_int(row.get('rtoadd'))

    low = None
    if lfromadd and rfromadd:
        low = lfromadd if lfromadd < rfromadd else rfromadd
    elif lfromadd:
        low = lfromadd
    elif rfromadd:
        low = rfromadd

    high_low_dict = master.get(fullname)
    if high_low_dict is None:
        master[fullname] = {}

    if low:
        current_low = master.get(fullname).get('low')
        if not current_low or low <= current_low:
            master.get(fullname)['low'] = low

    high = None
    if ltoadd and rtoadd:
        high = ltoadd if ltoadd >= rtoadd else rtoadd
    elif ltoadd:
        high = ltoadd
    elif rtoadd:
        high = rtoadd

    if high:
        current_high = master.get(fullname).get('high')
        if not current_high or high > current_high:
            master.get(fullname)['high'] = high

for key, value in master.items():
    print(value.get('low'), value.get('high'), key)


