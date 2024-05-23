from PIL import Image
import fitz  # PyMuPDF

def pdf_to_images(pdf_path, output_dir):
  #easier to read, but modifies image quality
  doc = fitz.open(pdf_path)
  for page_num in range(len(doc)):
    page = doc[page_num]
    img = page.get_images()
    pix = page.get_pixmap(matrix = fitz.Matrix(3,3))
    image = Image.frombytes("RGB", (pix.width,pix.height), pix.samples)
    image.save(f"{output_dir}/{page_num+1}.jpg")

def pdf_to_images2(pdf_path, output_dir):
  #yield true images, but longer
  doc = fitz.open(pdf_path) # open a document
  for page_index in range(len(doc)): # iterate over pdf pages
      page = doc[page_index] # get the page
      image_list = page.get_images()

      # print the number of images found on the page
      if image_list:
          print(f"Found {len(image_list)} images on page {page_index}")
      else:
          print("No images found on page", page_index)

      xref = image_list[0][0] # get the XREF of the image
      pix = fitz.Pixmap(doc, xref) # create a Pixmap
      if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
          pix = fitz.Pixmap(fitz.csRGB, pix)
      pix.save(f"{output_dir}/{page_index}.jpg") # save the image as png
      pix = None

def to_image(page):
    img = page.get_images()
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return image

if __name__ == '__main__':
  pdf = input('please enter the directory of the pdf file: ')
  out = input('Please enter the output directory: ')
  try:
    pdf_to_images(pdf, out)
    print('task completed')
  except:
    print('An error occurred while processing your request')
