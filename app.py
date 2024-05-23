from flask import Flask,render_template,request
from PIL import Image
import io,base64,csv,ImageSeperator,fitz

OddPagesLinks = {
    'PH': 'https://drive.google.com/drive/folders/1w65XYlpQFhlfA-sGSETY9ktSyGwZbp5N?usp=drive_link',
    'ST': 'https://drive.google.com/drive/folders/1hlEebf1UhjLHd-tQIo7id1_oqB8Tg6fx?usp=drive_link',
    'MA': 'https://drive.google.com/drive/folders/1GxuLNFNKJUhP95otajkbheo5rruqv1EC?usp=drive_link',
    'AR': 'https://drive.google.com/drive/folders/1rvvN7DAu8nrK_KmhvKuizqqwz-Vd37Op?usp=drive_link',
    'EN': 'https://drive.google.com/drive/folders/1qOsNTJcLtdmVjsmeMltmYBpL2zByw6Rl?usp=drive_link',
    'CS': 'https://drive.google.com/drive/folders/1ctXvfWj5719086SqZVVGZfjvYjab6ByN?usp=drive_link',
}

def get_page_index(serialNum,subject,formType):
    
    direc = ''
    if subject == 'ST':
        direc = 'sub_ST'
    else:
        if subject != 'EN' and formType in(forbidden := ['E','F','G','H']):
            formType =  ['A','B','C','D'][forbidden.index(formType)]
        direc = f'sub_{subject}/{formType}'

    pageIndex = ''
    found = False
    with open(f"{direc}/output.csv",newline='') as spreadsheet:
        reader = csv.reader(spreadsheet,delimiter=',')
        for row in reader:
            if str(serialNum) == row[1]:
                pageIndex = int(row[0])
                found = True
    if found:
        return [pageIndex,direc]
    else:
        if subject == 'ST':
            return ['','']#fail
        else:
            pageIndex,direc = checkOthersubFolders(serialNum,subject,formType)
            return [pageIndex,direc]


def checkOthersubFolders(serialNum,subject,formType):
    subs = ['A','B','C','D']
    if subject == 'EN':
        subs.extend(['E','F','G','H'])
    subs.remove(formType)
    
    pageIndex = ''
    correct_dir = ''
    for sub in subs:
        with open(f"sub_{subject}/{sub}/output.csv",newline='') as spreadsheet:
            reader = csv.reader(spreadsheet,delimiter=',')
            for row in reader:
                if str(serialNum) == row[1]:
                    pageIndex = int(row[0])
                    correct_dir = f"sub_{subject}/{sub}"
    return [pageIndex,correct_dir]

def get_page_image(pageIndex, direc):
    doc = fitz.open(f"{direc}/exams.pdf")
    pdfPage = doc[pageIndex]
    image = ImageSeperator.to_image(pdfPage)
    return image

def image_to_bytes(image):
    data = io.BytesIO()
    image.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return encoded_img_data.decode('utf-8')


app = Flask(__name__)

@app.route('/',methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/',methods=['POST'])
def get_paper():
    serialNum = request.form['SerialNumber']
    subject = request.form['subject']
    formType = request.form['FormType']

    pageIndex,direc = get_page_index(serialNum,subject,formType)
    found = False
    if pageIndex == '': #fail
        oddLink = OddPagesLinks[subject]
        return render_template('home.html',oddLink = oddLink ,foundPage = found)
    else:
        found = True
        page_image = get_page_image(pageIndex,direc)
        image_bytes = image_to_bytes(page_image)
        return render_template('home.html',img_uri=image_bytes,foundPage = found)

