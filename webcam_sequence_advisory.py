
#Imports
from analysis_library.packages import *
from analysis_library.context import *
from analysis_library.visual import *
from analysis_library.locational import *

def state_list_advice():

    #User Input
    sequence_name = input("Enter the name of the sequence you wish to follow (sequence should be defined in generated_sequences folder): ")
    
    #Read State List
    file = open('generated_sequences/'+sequence_name+'/sequence_state_list.csv', 'r')
    try:
        instruction_list = [list(map(int,rec)) for rec in csv.reader(file, delimiter=',')]
    except:
        instruction_list = list(csv.reader(file, delimiter=","))
    file.close()

    #Read Command List
    file = open('generated_sequences/'+sequence_name+'/command_list.csv', 'r')
    command_list = [list(map(str,rec)) for rec in csv.reader(file, delimiter=',')]
    file.close()

    #Initiate Model 
    weights_file = str(input("Enter Weights File Name: "))
    weights_dir =  'weights_collection/'+weights_file
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = torch.hub.load('WongKinYiu/yolov7', 'custom', f"{weights_dir}",force_reload=True, trust_repo=True).autoshape()

    #Initiating Camera
    cam_port = int(input("Enter the camera port: (Integer 0,1,2,...) "))
    cam = cv.VideoCapture(cam_port)
    cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    locational_select = input("Would you like to use locational advice? (y/n): ")

    if locational_select == "y":
        locational_advice(cam,model,instruction_list,command_list)
    elif locational_select == "n":
        context_advice(cam,model,instruction_list,command_list)
    else: 
        print("Invalid input. Please try again.")
        state_list_advice()


def context_advice(cam,model,instruction_list,command_list):

    buffer_size = 20
    results_buffer = [[0,0,0,0,0,0,0,0]]*buffer_size 
    instruction_index = 0

    while True:

        check, image = cam.read()

        if check:

            #Converting Image and producing detectio results
            converted = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            results = model(converted)
            results = results.pandas().xyxy[0]
            results = results[results.confidence >= 0.1]

            #Navigate Instructions List
            if instruction_index == len(instruction_list): 
                print("Congratulations! You have completed the sequence!")
                break

            desired_detection = instruction_list[instruction_index+1]
            command = (command_list[instruction_index])[0]

            #Generating State 
            generated_results = generate_results_count(results)
            results_buffer = update_results_buffer(results_buffer,generated_results)
            current_detection = buffer_most_frequent(results_buffer)

            #Displaying Detection Stream
            display_save_bounding_boxes(results,image)
            image = cv.resize(image, (1280 , 720))
            draw_text(image, command)
            cv.imshow('Context Advice', image)
            cv.waitKey(50) #May need to be smaller at some point

            if current_detection == desired_detection:
                print("Congratulations! You have completed instruction: " + str(instruction_index+1))
                instruction_index += 1


def locational_advice(cam,model,instruction_list,command_list):
    print("Locational Advice")
    instruction_index = 0
    
    while True:

        #Capture Image
        check, image = cam.read()

        #Check Image is valid 
        if check:

            #Converting Image and producing detection results
            converted = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            results = produce_locational_detection(converted,model)

            #Extract Corners from results
            corners , error_message = extract_corners(results)

            if corners is None:
                draw_text(image, error_message)
                cv.imshow('Locational Detections', image)
                cv.waitKey(50)

            else:
                board_coordinates = assign_corners(corners)

                #Transform to 'flat' space and capture transformation matrix
                transformed_image, transform_matrix = transform(image,board_coordinates)

                #Produce Detection Results on transformed image
                results_transformed = produce_locational_detection(transformed_image,model)

                #Define Regions
                horizontal_regions = [0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125]
                vertical_regions   = [0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125] 
                divsion_info = [horizontal_regions,vertical_regions]
                    
                #Create Regions
                lines = create_regions(divsion_info,transformed_image)
                region_list = create_region_list(lines)

                #Isolate Results
                dropped_results = results_transformed.copy()
                dropped_results.drop(['confidence','class'], axis=1, inplace=True)
                detected_boxes =  dropped_results.values.tolist()

                #Transform Results
                detection_nice_format = []
                for i in range(len(detected_boxes)):
                    detection_box = detected_boxes[i]
                    tl = (int(detection_box[0]),int(detection_box[3]))
                    tr = (int(detection_box[2]),int(detection_box[3]))
                    bl = (int(detection_box[0]),int(detection_box[1]))
                    br = (int(detection_box[2]),int(detection_box[1]))
                    name = detection_box[4]
                    detection_nice_format.append([tl,tr,br,bl,name])

                #Determine IoU
                locational_detections = generate_regional_detection_list(region_list,detection_nice_format)

                #Navigate Instructions List
                if instruction_index == len(instruction_list): 
                    print("Congratulations! You have completed the sequence!")
                    break

                desired_detection = instruction_list[instruction_index+1]
                command = (command_list[instruction_index])[0]

                print("Desired Detection")
                print(desired_detection)
                print("Locational Detections")
                print(locational_detections)

                #Display Regions
                transformed_image = display_regions(transformed_image,lines)
                display_save_bounding_boxes(results_transformed,transformed_image)
                draw_text(transformed_image, command)
                cv.imshow('Locational Detections', transformed_image )
                cv.waitKey(50)

                if locational_detections == desired_detection:
                    print("Congratulations! You have completed instruction: " + str(instruction_index+1))
                    instruction_index += 1


def main():
    print("Welcome to the sequence advisory!")
    
    advice_select = input("Would you like to advice from a state-machine or state-list? (sm/sl): ")

    if advice_select == "sm":
        print("State Machine Advice is only provided for the toy bulldozer case.")
        bulldozer_statemachine_analysis()

    elif advice_select == "sl":
        state_list_advice()

    else:
        print("Invalid input. Please try again.")
        main()



main()