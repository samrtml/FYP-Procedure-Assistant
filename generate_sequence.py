
#Imports
from analysis_library.packages import *
from analysis_library.context import *
from analysis_library.visual import *
from analysis_library.locational import *

def main():
    print("Welcome to the sequence generator!")
    
    live_select = input("Would you like to generate a sequence from a live video stream? (y/n): ")

    if live_select == "y":
        print("Please ensure that the camera is connected and the correct port is selected.")
        live_capture()
        predefined_generate()

    elif live_select == "n":
        print("Select a predefined sequence to generate")
        predefined_generate()

    else:
        print("Invalid input. Please try again.")
        main()


def live_capture():

    #Create Sequence Folder
    sequence_name = input("Enter the name of the sequence: ")
    os.mkdir('generated_sequences/'+sequence_name)
    os.mkdir('generated_sequences/'+sequence_name+'/input_images')

    #Create Command List in Sequence Folder
    command_list_file = open('generated_sequences/'+sequence_name+'/command_list.csv', 'w+')
    csv_writer = csv.writer(command_list_file)

    #Initiating Camera
    cam_port = int(input("Enter the camera port: (Integer 0,1,2,...) "))
    cam = cv.VideoCapture(cam_port)
    cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    #Initiating Image Count
    image_count = 0

    if input("Are you ready to the first state (Enter anything to procede)"):

            #Eliminating strange 5 frame buffer issue
            for i in range(5):
                check, image = cam.read()

            if check:
                #Saving Image to Sequence Folder
                image_count = image_count + 1
                cv.imwrite('generated_sequences/'+sequence_name+'/input_images/'+sequence_name+str(image_count)+'.jpg', image)

    while True:

        if input("Are you ready to capture the current state (Enter anything to procede)"):

            #Eliminating strange 5 frame buffer issue
            for i in range(5):
                check, image = cam.read()

            if check:
                #Saving Image to Sequence Folder
                image_count = image_count + 1
                cv.imwrite('generated_sequences/'+sequence_name+'/input_images/'+sequence_name+str(image_count)+'.jpg', image)


            #Write Command to Command List CSV
            command = input("Enter instruction/command which took place from the previous to the current state: ")
            csv_writer.writerow([command])

                
                
            if (input("Have you finished the sequence (y to exit)") == "y"):
                break
    
    #Close Command List
    command_list_file.close()

def predefined_generate():

    #User Inputs
    image_folder = str(input("Enter Image Folder Directory Name: "))
    folder_dir_load = 'generated_sequences/'+image_folder+'/input_images'
    folder_dir_save = 'generated_sequences/'+image_folder+'/detection_output'
    sequence_length = len(os.listdir(folder_dir_load)) 
    print("Sequence Length: "+str(sequence_length))

    weights_file = str(input("Enter Weights File Name: "))
    weights_dir =  'weights_collection/'+weights_file

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = torch.hub.load('WongKinYiu/yolov7', 'custom', f"{weights_dir}",force_reload=True, trust_repo=True).autoshape()

    locational_select = input("Does your procedure require locational analysis? (y/n): ")

    if locational_select == "y":
        #locational_analysis(image_folder)
        print("Locational Analysis")
        results_list = []
        os.mkdir(folder_dir_save)

        for i in range(1,sequence_length+1):
            print("Image: "+str(i))
            image = cv.imread(folder_dir_load+"/"+image_folder+str(i)+".jpg")

            print("Detecting")
            #Converting Image and producing detection results
            converted = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            results = produce_locational_detection(converted,model)

            #Extract Corners from results
            corners , error_message = extract_corners(results)
            if corners is None:
                print("Error please inspect corners are visible on image: "+str(i))

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
            for j in range(len(detected_boxes)):
                detection_box = detected_boxes[j]
                tl = (int(detection_box[0]),int(detection_box[3]))
                tr = (int(detection_box[2]),int(detection_box[3]))
                bl = (int(detection_box[0]),int(detection_box[1]))
                br = (int(detection_box[2]),int(detection_box[1]))
                name = detection_box[4]
                detection_nice_format.append([tl,tr,br,bl,name])

            #Determine IoU
            locational_detections = generate_regional_detection_list(region_list,detection_nice_format)
            print(locational_detections)

            #Display Regions
            transformed_image = display_regions(transformed_image,lines)
            display_save_bounding_boxes(results_transformed,transformed_image)

            cv.imwrite(folder_dir_save+"/"+image_folder+str(i)+".jpg",transformed_image)

            #Updating results list
            results_list.append(locational_detections)

        #Writing results list to csv
        file = open('generated_sequences/'+image_folder+'/sequence_state_list.csv', "w")
        writer = csv.writer(file)

        for data_list in results_list:
            writer.writerow(data_list)

        file.close()

    
    elif locational_select == "n":
        print("Context Analysis")
        results_list = []
        os.mkdir(folder_dir_save)

        for i in range(1,sequence_length+1):
            print("Image: "+str(i))
            image = cv.imread(folder_dir_load+"/"+image_folder+str(i)+".jpg")

            print("Detecting")
            converted = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            results = model(converted)
            results = results.pandas().xyxy[0]
            results = results[results.confidence >= 0.1]

            print(results)
            
            display_save_bounding_boxes(results,image)
            image = cv.resize(image, (1280 , 720))
            
            cv.imwrite(folder_dir_save+"/"+image_folder+str(i)+".jpg",image)

            #Generating State 
            generated_result = generate_results_count(results)

            #Updating results list
            results_list.append(generated_result)

        #Writing results list to csv
        file = open('generated_sequences/'+image_folder+'/sequence_state_list.csv', "w")
        writer = csv.writer(file)

        for data_list in results_list:
            writer.writerow(data_list)

        file.close()

    else:
        print("Invalid input. Please try again.")
        predefined_generate()

main()




