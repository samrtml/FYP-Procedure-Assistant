from analysis_library.packages import *

def extract_corners(results):
    
    if ((results['name'].eq('corner')).any()):
        if (results['name'].eq('corner').sum() == 4):

            corners_results = results[results['name'] == 'corner']
            corners_results.insert(0,'center_x',(corners_results['xmin']+corners_results['xmax'])/2)
            corners_results.insert(0,'center_y',(corners_results['ymin']+corners_results['ymax'])/2)
    
            #Get centre x and y of corners
            corners = corners_results[['center_x','center_y']]
            corners = corners.to_numpy()
            error_message = ""
            return corners , error_message
        
        else:
            error_message = 'Error - Incorrect number of corners detected - Please adjust the target'
            return None , error_message
            
    else:
        error_message = 'Error - No corners detected - Please adjust the target'
        return None , error_message
        
def assign_corners(corners):

    #Corner Assignment
    #[top_left, top_right, bottom_right, bottom_left] 

    board = np.zeros((4, 2), dtype = "float32") #initialise board array with 4 corners and 2 values (x,y)
    
    #Determining top left and bottom right corners
    sum = corners.sum(axis = 1) #sum of x and y for each corner
    board[0] = corners[np.argmin(sum)] #top_left
    board[2] = corners[np.argmax(sum)] #bottom_right

    #Determining top right and bottom left corners
    difference = np.diff(corners, axis = 1) #difference of x and y for each corner
    board[1] = corners[np.argmin(difference)] #top_right
    board[3] = corners[np.argmax(difference)] #bottom_left

    return board

def transform(image, board_coordinates):
      
    image = np.asarray(image)
    (top_left, top_right, bottom_right, bottom_left)  = board_coordinates

    #Calculating the width and height of the new image
    #Width
    bottom_width = np.sqrt(((bottom_right[1] - bottom_left[1]) ** 2)+((bottom_right[0] - bottom_left[0]) ** 2))
    top_width = np.sqrt(((top_right[1] - top_left[1]) ** 2)+ ((top_right[0] - top_left[0]) ** 2))
    max_width = max(int(bottom_width), int(top_width))
    #Height
    right_width = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) + ((top_right[1] - bottom_right[1]) ** 2))
    left_width = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) + ((top_left[1] - bottom_left[1]) ** 2))
    max_height = max(int(right_width), int(left_width))

    #Obtains transformation
    #New target image points [top_left, top_right, bottom_right, bottom_left] 
    target_coordinates = np.array([[0, 0],[max_width - 1, 0],[max_width - 1, max_height - 1],[0, max_height - 1]], dtype = "float32")
    transform_matrix = cv.getPerspectiveTransform(board_coordinates, target_coordinates)
    
    #Warping image
    warped = cv.warpPerspective(image, transform_matrix, (max_width, max_height))
    transformed_image = Image.fromarray(warped, "RGB")

    return transformed_image , transform_matrix

def create_regions(divsion_info,transformed_image):

    #Example regions defintion for 8x8 chess board
    #horizontal_regions = [0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125]
    #vertical_regions = [0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125] 
    horizontal_regions , vertical_regions = divsion_info 
    width,height = transformed_image.size

    #Creating horizontal lines
    horizontal_lines = []
    previous_h = 0
    horizontal_lines.append(previous_h)

    for i in range(0,len(horizontal_regions)):
        horizontal_lines.append(previous_h + int(height * horizontal_regions[i]))
        previous_h = previous_h + int(height * horizontal_regions[i])
    
    #Creating vertical lines
    vertical_lines = []
    previous_v = 0
    vertical_lines.append(previous_v)

    for i in range(0,len(vertical_regions)):
        vertical_lines.append( previous_v + int(width * vertical_regions[i]))
        previous_v = previous_v + int(width * vertical_regions[i])


    lines = [horizontal_lines, vertical_lines]
    return lines

def display_regions(image,lines):

    width, height = image.size

    #Displaying regions on image
    horizontal_lines = lines[0]
    vertical_lines = lines[1]

    image = cv.UMat(np.array(image, dtype=np.uint8))

    for i in range(len(horizontal_lines)):
        cv.line(image, (0, horizontal_lines[i]), (width, horizontal_lines[i]), (0, 0 , 255), 1)
    
    for i in range(len(vertical_lines)):
        cv.line(image, (vertical_lines[i], 0), (vertical_lines[i], height), (0, 0 , 255), 1)

    return image

def create_region_list(lines):

    horizontal_lines = lines[0]
    vertical_lines = lines[1]

    #region_list = [tl,tr,bl,br]
    region_list = []


    for i in range(len(horizontal_lines)-1):
        for j in range(len(vertical_lines)-1):
            bl = (float(vertical_lines[j]),  float(horizontal_lines[i]))
            br = (float(vertical_lines[j+1]),float(horizontal_lines[i]))
            tl = (float(vertical_lines[j]),  float(horizontal_lines[i+1]))
            tr = (float(vertical_lines[j+1]),float(horizontal_lines[i+1]))
            region_list.append([tl,tr,br,bl])
    
    return region_list

def determine_iou(region_box, detection_box):
    region_box = Polygon(region_box)
    detection_box = Polygon(detection_box)

    iou = region_box.intersection(detection_box).area / region_box.union(detection_box).area

    return iou

def generate_regional_detection_list(region_list, detected_boxes):
    regional_detection_list = region_list.copy()
    current_region_iou = region_list.copy()

    for i in range(len(region_list)):
        regional_detection_list[i] = "empty"
        current_region_iou[i] = 0

    for i in range(len(region_list)):
        region_box = region_list[i]
        for j in range(len(detected_boxes)):
            detection_box = detected_boxes[j]
            iou = determine_iou(region_box,detection_box[:4])
            if iou > 0.3:
                if iou > current_region_iou[i]:
                    regional_detection_list[i] = (detection_box[4].replace("'", ''))
                    current_region_iou[i] = iou
            
    return regional_detection_list

def produce_locational_detection(image,model):
    results = model(image)
    results = results.pandas().xyxy[0]
    results = results[results.confidence >= 0.6]
    return results

