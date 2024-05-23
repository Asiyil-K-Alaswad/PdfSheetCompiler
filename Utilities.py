from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import csv,fitz,json,re
import main


subs = ['PH','MA','AR','EN','ST','CS']
formTypes = ['A','B','C','D','E','F','G','H']

def how_many_odds():
    for sub in subs:
        try:
            if sub == 'ST':
                with open(f"sub_{sub}/output.csv") as fil:
                    reader = csv.reader(fil)
                    for row in reader:
                        numOfodds = len(row)-1
                        print(f"sub_ST has {numOfodds} odd pages.")
                        break
            else:
                if sub != 'EN':
                    ft = formTypes[:4]
                for  formType in ft:
                    with open(f"sub_{sub}/{formType}/output.csv") as fil:
                        reader = csv.reader(fil)
                        for row in reader:
                            numOfodds = len(row)-1
                            print(f"sub_{sub}/{formType} has {numOfodds} odd pages.")
                            break
        except:
            print(f'failed {sub}')

how_many_odds()

def extractOdds():
    for sub in subs:
        try:
            if sub == 'ST':
                main.ExtractOddPages(f'sub_ST')
            else:
                if sub != 'EN':
                    ft = formTypes[:4]
                for  formType in ft:
                    main.ExtractOddPages(f"sub_{sub}/{formType}")
        except:
            print(f'failed {sub}')
extractOdds()

def bleh():
    with open('res.csv',mode='a' ,newline="")as f:
        writer=csv.writer(f)
        writer.writerow(['bleh','page'])
