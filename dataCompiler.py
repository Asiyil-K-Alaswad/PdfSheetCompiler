from PIL import Image
import csv,fitz,json
import ImageSeperator,cropper,optik

Upshift,Downshift = 20,-65
UpC,DownC = 30,15

def Main():
    print(
        f"exam sheets compiler \nStructure\n- each subject is a subfolder in this directory\n- each subject folder has an exams.pdf file to be read\n- each folder has a settings.json file similar to the one in the sample folder to tweak cropping\n- an output.csv file will be created in the subject folder once compilation is over")
    sub = input('please enter which subfolder to compile: ')
    debug = input('Debug Mode? (y/n)')
    debug = True if debug == 'y' else False
    doc = fitz.open(f"{sub}/exams.pdf")
    with open(f"{sub}/settings.json", mode='r') as file:
        options = json.load(file)
        print(options)
    oddPages = []
    with open(f"{sub}/output.csv", 'w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for index, page in enumerate(doc):
            img = ImageSeperator.to_image(page)
            shift = 0
            C = DownC
            while True: #would run 5 times max
                cropped_image = cropper.crop(img, options,shift)
                modified_image = cropper.place_boxes(cropped_image, options)
                # if debug:
                #     modified_image.show()
                modified_image.save("current.jpg")
                try:
                    serialNum = optik.ExtractSerialNumber("current.jpg",debug,C)
                    csvWriter.writerow([index, serialNum])
                    print(f"page {index} has a serial number of {serialNum}")
                    break
                except:
                    if C==DownC:
                        C=UpC
                        continue
                    if shift==Upshift:
                        shift= Downshift
                        continue
                    elif shift==0:
                        shift= Upshift
                        continue
                    print(f"page {index} is odd..")
                    oddPages.append(index)
                    break
        odds = ['odd']
        odds.extend(oddPages)
        csvWriter.writerow(odds)
        print(f"found {len(oddPages)} odd pages")

def singleTime(num):
    print(
        f"exam sheets compiler \nStructure\n- each subject is a subfolder in this directory\n- each subject folder has an exams.pdf file to be read\n- each folder has a settings.json file similar to the one in the sample folder to tweak cropping\n- an output.csv file will be created in the subject folder once compilation is over")
    sub = 'sub_EN/F'
    debug = ''
    debug = True if debug == 'y' else False
    doc = fitz.open(f"{sub}/exams.pdf")
    with open(f"{sub}/settings.json", mode='r') as file:
        options = json.load(file)
        print(options)
    oddPages = []
    with open(f"{sub}/output.csv", 'r', newline='') as csvFile:
        # csvWriter = csv.writer(csvFile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for index, page in enumerate(doc):
            img = ImageSeperator.to_image(page)
            shift = 0
            C = DownC
            for i in range(0,3):
                cropped_image = cropper.crop(img, options,shift)
                modified_image = cropper.place_boxes(cropped_image, options)
                # if debug:
                #     modified_image.show()
                modified_image.save("current.jpg")
                try:
                    serialNum = optik.ExtractSerialNumber("current.jpg",debug,DownC)
                    # csvWriter.writerow([index, serialNum])
                    print(f"page {index} has a serial number of {serialNum}")
                    break
                except:
                    if C==DownC:
                        C=UpC
                        continue
                    if shift==Upshift:
                        shift= Downshift
                        continue
                    if shift==Upshift:
                        shift= Downshift
                        continue
                    elif shift==0:
                        shift=Upshift
                        continue
                    print(f"page {index} is odd..")
                    oddPages.append(index)
                    break
                if num < index:
                    break
        odds = ['odd']
        odds.extend(oddPages)
        csvWriter.writerow(odds)
        print(f"found {len(oddPages)} odd pages")

def TestPageAtIndex():
    sub = 'sub_EN/H'
    debug = 'y'
    index = 4#  5	6	8	9	10	11	12	13	15	16	17	18	19	20	21	23	24	25	26

    debug = True if debug == 'y' else False
    doc = fitz.open(f"{sub}/exams.pdf")
    with open(f"{sub}/settings.json", mode='r') as file:
        options = json.load(file)
        print(options)
    oddPages = []
    with open(f"{sub}/output.csv", 'r', newline='') as csvFile:
        # csvWriter = csv.writer(csvFile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        page = doc[index]
        img = ImageSeperator.to_image(page)

        # # Grayscale
        # img = img.convert('L')
        # # Threshold
        # img = img.point(lambda p: 255 if p > 220 else 0)
        # # To mono
        # img = img.convert('1')

        shift = 0
        C = DownC
        for i in range(0,4):
            cropped_image = cropper.crop(img, options,shift)
            modified_image = cropper.place_boxes(cropped_image, options)
            # if debug:
            #     modified_image.show()
            modified_image.save("current.jpg")
            try:
                serialNum = optik.ExtractSerialNumber("current.jpg",debug)
                # csvWriter.writerow([index, serialNum])
                print(f"page {index} has a serial number of {serialNum}")
                break
            except:
                if C == DownC:
                    C = UpC
                    continue
                if shift==20:
                    shift= -65
                    continue
                elif shift==0:
                    shift=20
                    continue
                print(f"page {index} is odd..")
                oddPages.append(index)
        odds = ['odd']
        odds.extend(oddPages)
        # csvWriter.writerow(odds)
        print(f"found {len(oddPages)} odd pages")


    #write a script to extract the odd pages from the exams file and put them in a seperate file named odds.pdf

if __name__ == '__main__':
    # Main()
    # singleTime(30)
    # TestPageAtIndex()
    ProcessPDFToDirectory('sub_EN/A',1,380)


