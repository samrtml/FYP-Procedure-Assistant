 #Imports from analysis_library
from analysis_library.packages import *
from analysis_library.context import *
from analysis_library.visual import *
from analysis_library.locational import *
from analysis_library.state_machine import *

#Imorts for hl2ss  
from pynput import keyboard

import cv2
import hl2ss_imshow
import hl2ss
import threading
import hl2ss_rus

#HoloLens address
host = "146.169.255.30"

def unity_send_text(host,message):
    # HoloLens address
    host = host
    # Port
    port = hl2ss.IPCPort.UNITY_MESSAGE_QUEUE

    # Position in world space (x, y, z) in meters
    position = [0, -0.45, 0.65]

    # Rotation in world space (x, y, z, w) as a quaternion
    rotation = [0, 0, 0, 1]

    # Text
    text = message

    # Font size
    font_size = 0.4

    # Text color
    rgba = [1, 1, 1, 1]

    #------------------------------------------------------------------------------

    ipc = hl2ss.ipc_umq(host, port)
    ipc.open()

    key = 0

    display_list = hl2ss_rus.command_buffer()
    display_list.begin_display_list() # Begin command sequence
    display_list.remove_all() # Remove all objects that were created remotely
    display_list.create_text() # Create text object, server will return its id
    display_list.set_target_mode(hl2ss_rus.TargetMode.UseLast) # Set server to use the last created object as target, this avoids waiting for the id of the text object
    display_list.set_text(key, font_size, rgba, text) # Set text
    display_list.set_world_transform(key, position, rotation, [1, 1, 1]) # Set the world transform of the text object
    display_list.set_active(key, hl2ss_rus.ActiveState.Active) # Make the text object visible
    display_list.set_target_mode(hl2ss_rus.TargetMode.UseID) # Restore target mode
    display_list.end_display_list() # End command sequence
    ipc.push(display_list) # Send commands to server
    results = ipc.pull(display_list) # Get results from server
    key = results[2] # Get the text object id, created by the 3rd command in the list

    print(f'Created text object with id {key}')

    ipc.close()


# Port
port = hl2ss.StreamPort.PERSONAL_VIDEO

# Operating mode
# 0: video
# 1: video + camera pose
# 2: query calibration (single transfer)
mode = hl2ss.StreamMode.MODE_0

# Camera parameters
width     = 1280
height    = 720
framerate = 30

# Video encoding profile
profile = hl2ss.VideoProfile.H265_MAIN

# Encoded stream average bits per second
# Must be > 0
bitrate = hl2ss.get_video_codec_bitrate(width, height, framerate, hl2ss.get_video_codec_default_factor(profile))

# Decoded format
# Options include:
# 'bgr24'
# 'rgb24'
# 'bgra'
# 'rgba'
# 'gray8'
decoded_format = 'bgr24'

#------------------------------------------------------------------------------

hl2ss.start_subsystem_pv(host, port)


enable = True

client = hl2ss.rx_decoded_pv(host, port, hl2ss.ChunkSize.PERSONAL_VIDEO, mode, width, height, framerate, profile, bitrate, decoded_format)
client.open()
print("Connection Successful")

#Analysis Setup
current_state = 0


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
path = 'weights_collection/Chess_detector.pt'
model = torch.hub.load('WongKinYiu/yolov7', 'custom', f"{path}",force_reload=True, trust_repo=True).autoshape()
timer = 0

#Read Instructions from CSV
file = open("trial_sequences/chess_sequence_simple/results_list.csv", "r")
#instruction_list = [list(map(str,rec)) for rec in csv.reader(file, delimiter=',')]
instruction_list = list(csv.reader(file, delimiter=","))
file.close()

#Read Instructions from CSV
file = open("trial_sequences/chess_sequence_simple/command_list.csv", "r")
command_list = [list(map(str,rec)) for rec in csv.reader(file, delimiter=',')]
file.close()

instruction_index = 0


command = "Hello & Welcome to Chess Assistant!"
unity_send_text(host,command)

while True:
    data = client.get_next_packet()
    image_out = data.payload.image

    if image_out is None:
        continue
    else:
        if (timer == 50):
            timer = 0

            #Converting Image and producing detection results
            converted = cv.cvtColor(image_out, cv.COLOR_BGR2RGB)
            results = produce_locational_detection(converted,model)

            #Extract Corners from results
            corners , error_message = extract_corners(results)

            if corners is None:
                #unity_send_text(host,"Please Ensure the entire chess board is visible")
                draw_text(image_out, error_message)
                cv.imshow('Chess Detections', image_out)
                cv.waitKey(50)

            else:
                board_coordinates = assign_corners(corners)

                #Transform to 'flat' space and capture transformation matrix
                transformed_image, transform_matrix = transform(image_out,board_coordinates)

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
                if instruction_index == len(instruction_list): # Not sure if works yet
                    print("Congratulations! You have completed the sequence!")
                    break

                desired_detection = instruction_list[instruction_index+1]
                command = (command_list[instruction_index])[0]

                print("Desired Detection")
                print(desired_detection)
                print("Locational Detections")
                print(locational_detections)

                #Create Command
                unity_send_text(host,command)

                #Display Regions
                transformed_image = display_regions(transformed_image,lines)
                display_save_bounding_boxes(results_transformed,transformed_image)
                #cv.rectangle(transformed_image,region_list[18][0],region_list[18][2],(0,0,255),3)
                draw_text(transformed_image, command)
                cv.imshow('Video Stream', transformed_image )
                cv.waitKey(50) #May need to be smaller at some point

                if locational_detections == desired_detection:
                    print("Congratulations! You have completed instruction: " + str(instruction_index+1))
                    instruction_index += 1


                timer += 1
        else:
            cv.imshow('Chess Detections', image_out)
            cv.waitKey(1) 
            timer += 1

client.close()

hl2ss.stop_subsystem_pv(host, port)