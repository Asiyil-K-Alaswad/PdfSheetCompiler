from PIL import Image,ImageDraw



def crop(img,options,shiftY=0,shiftX=0,tilt=0):
    CROP_DIMENSION = options['cropDimensions']
    padding_amount = options['padding']

    crop_dimensions = (
        CROP_DIMENSION[0] - padding_amount + shiftX ,
        (CROP_DIMENSION[1] - padding_amount )+ shiftY,
        CROP_DIMENSION[2] + padding_amount + shiftX,
        (CROP_DIMENSION[3] + padding_amount) + shiftY
    )
    cropped_img = img.crop(crop_dimensions)
    tilted = cropped_img.rotate(tilt)
    return tilted

def place_boxes(img,options):
    draw = ImageDraw.Draw(img)

    box_padding = options['boxPadding']
    box_size = options['boxSize']
    boxes_positions = {
        'tl': [(box_padding,box_padding) , (box_padding+box_size,box_padding+box_size)],
        'tr': [(img.size[0]-(box_padding+box_size),box_padding),(img.size[0]-box_padding,box_padding+box_size)],
        'bl': [(box_padding,img.size[1]-(box_padding+box_size)), (box_padding+box_size , img.size[1]-box_padding)],
        'br': [(img.size[0]-(box_padding+box_size) , img.size[1]-(box_padding+box_size)) , (img.size[0]-(box_padding) , img.size[1]-(box_padding))]
    }
    draw.rectangle([(0, 0), (img.size[0], options['topPaintAmount'])], fill='#ffffff')
    draw.rectangle([(0, img.size[1]-options['bottomPaintAmount']), img.size], fill='#ffffff')
    draw.rectangle([(0, 0), (options['leftPaintAmount'], img.size[1])], fill='#ffffff')

    draw.rectangle(boxes_positions['tl'], fill='#000000', width=10)
    draw.rectangle(boxes_positions['tr'], fill='#000000', width=10)
    draw.rectangle(boxes_positions['bl'], fill='#000000', width=10)
    draw.rectangle(boxes_positions['br'], fill='#000000', width=10)

    return img

