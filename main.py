from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import csv,fitz,json,re
import ImageSeperator,cropper,Scanner,optik


standard_image_shift = 40/2
def GenerateImageVariants(img,dir,options):
    '''
    takes a page image and generates 8 different cropped variants that are displaced by some amount in the 8 standard directions
    '''
    for X in range(-1,2):
        for Y in range(-1,2):
            # crop and modify
            if ('tilt' in options.keys()):
                cropped_image = cropper.crop(img, options,standard_image_shift*Y, standard_image_shift*X, tilt=options['tilt'])
            else:
                cropped_image = cropper.crop(img, options, standard_image_shift * Y, standard_image_shift * X)
            modified_image = cropper.place_boxes(cropped_image, options)
            modified_image.save(f"{dir}/image({X},{Y}).jpg")

def CompileFile(dir):
    '''
    Compiles an entire pdf file.
    - requirements:
        . a pdf file named 'exams' in the given directory
        . a json file named 'settings' in the given directory
        . an xtmpl file named 'template' in the given directory
    - process:
     . the function will process each page indivisually, making a cropped and processed temporary version before executing an instance of the java sheet scanner
     . after all pages are processed a csv file named 'output' is created where:
        - the first row is the index of pages that weren't processed successfully
        - the other rows have the index of the page and the extracted serial number sequentially
    '''
    # open pdf file
    doc = fitz.open(f"{dir}/exams.pdf")
    with open(f"{dir}/settings.json", mode='r') as file:
        options = json.load(file)

    validPages = []
    oddPages = []
    # for each page
    for index, page in enumerate(doc):
        # convert to image
        img = ImageSeperator.to_image(page)
        #generate variants
        GenerateImageVariants(img,'temp',options)
        # run scanner
        Scanner.execute_FormScanner(f"{dir}/template.xtmpl","temp","res.csv")
        # extract serial number from scanning image variants
        serialNum = ''
        with open('res.csv','r',newline='') as tempcsv:
            reader = csv.reader(tempcsv,delimiter=';')
            for i,row in enumerate(reader):
                if '' in row[0:2]:
                    row[0:2] = ['2', '2']
                if row[2] == '':
                    row[2] = 3
                if '' in row[4:6]:
                    row[4:6] = ['9','9']
                if(i >= 1) and (not('' in row)):
                    serialNum = ''.join(row[1:])

        print(f"page {index} has a serial number of {serialNum} ")
        #validate serial number
        if len(serialNum) == 10 and re.match(r'^([\s\d]+)$', serialNum) : # check if serial number is valid with no | or ,
            validPages.append( (index,serialNum) )
        else:
            oddPages.append( index )
    #make spreadsheet
    with open(f"{dir}/output.csv", 'w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        odds = ['odd']
        odds.extend(oddPages)
        csvWriter.writerow(odds)
        for pi,sn in validPages:
            csvWriter.writerow([pi,sn])


def CompilePage(dir,pageIndex):
    '''
    compiles a single page in a pdf file
    '''
    # open pdf file
    doc = fitz.open(f"{dir}/exams.pdf")
    with open(f"{dir}/settings.json", mode='r') as file:
        options = json.load(file)

    validPages = []
    oddPages = []
    page = doc[pageIndex]
    # convert to image
    img = ImageSeperator.to_image(page)
    #generate variants
    GenerateImageVariants(img,'temp',options)
    # run scanner
    Scanner.execute_FormScanner(f"{dir}/template.xtmpl","temp","res.csv")
    # extract serial number from scanning image variants
    serialNum = ''
    with open('res.csv','r',newline='') as tempcsv:
        reader = csv.reader(tempcsv,delimiter=';')
        for i,row in enumerate(reader):
            if '' in row[0:2]:
                row[0:2] = ['2','2']
            if '' in row[4:6]:
                row[4:6] = ['9', '9']
            print(row)
            if(i >= 1) and (not('' in row)):
                serialNum = ''.join(row[1:])

    print(f"page {pageIndex} has a serial number of {serialNum} ")
    #validate serial number
    if len(serialNum) == 10 and re.match(r'^([\s\d]+)$', serialNum) : # check if serial number is valid with no | or ,
        validPages.append( (pageIndex,serialNum) )
    else:
        oddPages.append( pageIndex )
    #log out come
    print(validPages)
    print(oddPages)

def ProcessPDFToDirectory(directory,bp,start=0):
    '''
    goes through a pdf file and extracts every page as an image and saves it in a 'images' sub directory
    '''
    doc = fitz.open(f"{directory}/exams.pdf")
    with open(f"{directory}/settings.json", mode='r') as file:
        options = json.load(file)
    oddPages = []
    for index, page in enumerate(doc):
        if index < start:
            continue
        img = ImageSeperator.to_image(page)
        modified_image = cropper.place_boxes(img, options)
        img.thumbnail((1000,1414.3337))
        modified_image.save(f"{directory}/images/{index}.jpg" , optimize = True, quality = 50)
        if(index > start+bp):
            break

def ExtractOddPages(directory):
    oddIndecies = []
    with open(f"{directory}/output.csv" , newline='') as file:
        reader = csv.reader(file)
        for i,row in enumerate(reader):
            if i == 0:
                oddIndecies = [ int(i) for i in row[1:] ]

    with open(f"{directory}/exams.pdf", 'rb') as pdf_file:
        reader = PdfReader(pdf_file)
        writer = PdfWriter()

        # Extract and add desired pages
        for index in oddIndecies:
            writer.add_page(reader.pages[index])

        with open(f"{directory}/OddPages.pdf", 'wb') as output_file:
            writer.write(output_file)


# CompileFile("sub_AR/D")
# CompilePage("sub_PH/D",780)
ProcessPDFToDirectory('sub_CS/D',25,0)
# ExtractOddPages("sub_EN/H")
