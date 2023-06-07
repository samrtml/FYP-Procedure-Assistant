from analysis_library.packages import *

def display_save_bounding_boxes(results,image):

     for index, row in results.iterrows():
          xmin,ymin,xmax,ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
          label, confidence = str(row['name']) , str('{:.2%}'.format(row['confidence']))
          cv.rectangle(image, (xmin,ymin), (xmax,ymax), (0,255,0), 1)
          cv.putText(image, label + ' , ' + confidence, (xmin, ymin-10), cv.FONT_HERSHEY_SIMPLEX, 0.3, (36,255,12), 1)

def draw_text(img, text,
          font=cv.FONT_HERSHEY_SIMPLEX,
          pos=(10, 10),
          font_scale=1,
          font_thickness=1,
          text_color=(255, 255, 255),
          text_color_bg=(0, 0, 0)
          ):

    x, y = pos
    text_size, _ = cv.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv.rectangle(img, pos, (x + text_w + 10, y + text_h +10), text_color_bg, -1)
    cv.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)

    return text_size