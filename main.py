from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from multiprocessing import Pool
import csv,fitz,json,re,argparse,multiprocessing,os
import ImageSeperator,cropper,Scanner,shutil


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
                modified_image = cropper.place_boxes(cropped_image, options)
                modified_image.save(f"{dir}/image({X},{Y})_tilt.jpg")
                cropped_image = cropper.crop(img, options,standard_image_shift*Y, standard_image_shift*X)
                modified_image = cropper.place_boxes(cropped_image, options)
                modified_image.save(f"{dir}/image({X},{Y}).jpg")
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
        if ValidateSerialNum(serialNum) : # check if serial number is valid with no | or ,
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

def SampleCompilePage(dir,pageIndex):
    '''
    compiles a single page in a pdf file (for debugging and testing purposes)
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

def CompilePage(dir,index):
    # open pdf file
    doc = fitz.open(f"{dir}/exams.pdf")
    with open(f"{dir}/settings.json", mode='r') as file:
        options = json.load(file)
    page = doc[index]
    # convert to image
    img = ImageSeperator.to_image(page)
    #generate variants
    GenerateImageVariants(img,f'temp',options)
    # run scanner
    try:
        Scanner.execute_FormScanner(f"{dir}/template.xtmpl",f"temp",f"res.csv")
    except:
        print('f"page {index} couldn\t be processed')
        return (index , '')
    # extract serial number from scanning image variants
    serialNum = ''
    with open(f"res.csv",'r',newline='') as tempcsv:
        reader = csv.reader(tempcsv,delimiter=';')
        for i,row in enumerate(reader):
            row = TryCompleteSerialNum(row)
            if(i >= 1) and (not('' in row)):
                serialNum = ''.join(row[1:])
    #validate serial number
    if ValidateSerialNum(serialNum) : # check if serial number is valid with no | or ,
        print(f"page {index} has a serial number of {serialNum} ")
        return (index , serialNum)
    else:
        print(f"page {index} has a serial number of {serialNum} which is INVALID")
        return (index , '')

def ExtractPagesIntoPDF(dir,pageIndecies,pdfName):
    with open(f"{dir}/exams.pdf", 'rb') as pdf_file:
        reader = PdfReader(pdf_file)
        writer = PdfWriter()

        # Extract and add desired pages
        for index in pageIndecies:
            writer.add_page(reader.pages[index])

    with open(f"{dir}/{pdfName}.pdf", 'wb') as output_file:
        writer.write(output_file)

def ExtractPagesIntoFolder(dir,outDir ,pageIndecies=[] ,process=False ,options=None, end = 999999):
    if not os.path.isdir(f'{outDir}'):
        os.mkdir(f'{outDir}')
    doc = fitz.open(f"{dir}/exams.pdf")
    for index, page in enumerate(doc):
        if index > end:
            break
        if (not index in pageIndecies) and (pageIndecies != []):
            continue
        img = ImageSeperator.to_image(page)
        if process:
            img = cropper.crop(img,options)
            img = cropper.place_boxes(img,options)
            img.save(f"{outDir}/{index}.jpg")
        else:
            img.thumbnail((1000,1414.3337))
            img.save(f"{outDir}/{index}.jpg" , optimize = True, quality = 50)

def TryCompleteSerialNum(row):
    if '' in row[0:2]:
        row[0:2] = ['2', '2']
    if '' in row[3:5]:
        row[3:5] = ['9','9']
    return row

def ValidateSerialNum(serialNum):
    if len(serialNum) == 10 and re.match(r'^([\s\d]+)$', serialNum) and serialNum[0] == '2':
        return True
    else:
        return False

def parseFormScannerCSV(dir,csvDir):
    validPages = []
    oddPages = []
    #loop through sheet
    with open(csvDir,mode='r',newline='') as sheet:
        reader = csv.reader(sheet,delimiter=';')
        for i,row in enumerate(reader):
            row[1:] = TryCompleteSerialNum(row[1:])
            if (i >= 1):
                serialNum = ''.join(row[1:])
                if ValidateSerialNum(serialNum):
                    validPages.append( (row[0][0:-4],serialNum) )
                else:
                    oddPages.append( row[0][0:-4] )
    # create output.csv in dir
    with open(f"{dir}/output.csv", 'w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in validPages:
            csvWriter.writerow(row)
    #return odd pages
    return [validPages , oddPages]

def create_parser():
    parser = argparse.ArgumentParser(prog='PDFSheetsCompiler'
                                     ,description='compile pdf sheets to extract thier serial number')
    parser.add_argument('dir')
    parser.add_argument('-m','--mode')#,default='',choices=[])
    parser.add_argument('-c','--cores',default=3,choices=[ str(i) for i in range(1,multiprocessing.cpu_count())])
    parser.add_argument('-e','--end',help='which page index to stop at')
    return parser

def reset_temp_folder(args):
    shutil.rmtree('temp')
    os.makedirs('temp')
    for i in range(int(args.cores)):
        os.makedirs(f'temp/{i}')

# CompileFile("sub_AR/D")
# CompilePage("sub_PH/D",780)
# ProcessPDFToDirectory('sub_CS/D',25,0)
# ExtractOddPages("sub_EN/H")

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if args.mode == 'one':
        reset_temp_folder(args)
        with open(f"{args.dir}/settings.json", mode='r') as file:
            options = json.load(file)
        #convert all pages to images in the temp folder
        ExtractPagesIntoFolder(args.dir,'temp',process=True, options=options,end=int(args.end))
        #process all pages once
        Scanner.execute_FormScanner(f"{args.dir}/template.xtmpl","temp",f"res.csv")
        #parse the output.csv
        validPages,Oddpages = parseFormScannerCSV(args.dir,'res.csv')

        reset_temp_folder(args)
        print(f'operating on {Oddpages} with a size of {len(Oddpages)}')
        #process odd pages one by one
        old = []
        old.extend(Oddpages)
        with open(f'{args.dir}/output.csv',mode='a',newline='') as file:
            writer = csv.writer(file)
            for i in old:
                try:
                    print(f'working on page {i}')
                    index,serialNum = CompilePage(args.dir,int(i))
                    if(serialNum != ''):
                        Oddpages.remove(i)
                        validPages.append((i,serialNum))
                        writer.writerow([index,serialNum])
                except :
                    print(f'{i} faced a problem')
        print(f'{len(Oddpages)} odd pages are left \n they are: {Oddpages}')


        #extract valid pages as images
        ExtractPagesIntoFolder(args.dir,f'{args.dir}/pages',[ int(i) for i,sn in validPages])
        # #extract invalid pages as pdf
        ExtractPagesIntoPDF(args.dir,[int(i) for i in Oddpages],f'OddPages_{args.dir}'.replace('/','_'))

        reset_temp_folder(args)
