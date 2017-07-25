import glob
from subprocess import Popen, PIPE
import os


pdfs = ['/Volumes/JetDrive/pdfs/0070001000.pdf']


def parse_pdf(path):
    with open(path, 'rb') as fp:
        ps2ascii = Popen(['ps2ascii'], stdin=PIPE, stdout=PIPE,
                stderr=PIPE, shell=True)
        ps2ascii.stdin.write(fp.read())
        ps2ascii.stdin.close()
        pdf_text = ps2ascii.stdout.read().decode()
        ps2ascii.stdout.close()
        ps2ascii.wait()
        return pdf_text


def main():
    pdfs = glob.iglob('/Volumes/JetDrive/pdfs/*.pdf')
    for pdf in pdfs:
        text = parse_pdf(pdf)
        if 'delinquent' in text.lower():
            print(pdf.split('/')[-1], flush=True)

main()

