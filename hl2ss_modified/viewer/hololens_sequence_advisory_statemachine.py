# #Imports from analysis_library
from analysis_library.packages import *
from analysis_library.context import *
from analysis_library.visual import *
from analysis_library.locational import *

#Imorts for hl2ss  
from pynput import keyboard

import cv2
import hl2ss_imshow
import hl2ss
import threading
import hl2ss_rus

#HoloLens address
host = "146.169.253.244"

def unity_send_text(host,message):
    # HoloLens address
    host = host
    # Port
    port = hl2ss.IPCPort.UNITY_MESSAGE_QUEUE

    # Position in world space (x, y, z) in meters
    position = [0, -0.45, 1]

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
width     = 1920
height    = 1080
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


#Analysis Setup
current_state = 0


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
path = 'weights_collection/Bulldozer_detector.pt'
model = torch.hub.load('WongKinYiu/yolov7', 'custom', f"{path}",force_reload=True, trust_repo=True).autoshape()
timer = 0

command = "Hello & Welcome to Assembly Assistant!"
unity_send_text(host,command)

while True:
    data = client.get_next_packet()
    image_out = data.payload.image

    if image_out is None:
        continue
    else:
        if (timer == 100):
            timer = 0
            converted = cv.cvtColor(image_out, cv.COLOR_BGR2RGB)
            results = model(converted)
            results = results.pandas().xyxy[0]
            results = results[results.confidence >= 0.3]

            #Generating State 
            generated_results = generate_results_count(results)

            current_state, command = state_machine(current_state,generated_results,command)

            #Displaying Detection Stream
            display_save_bounding_boxes(results,image_out)
            image_out = cv.resize(image_out, (1280 , 720))
            draw_text(image_out, command)

            #Create Command
            unity_send_text(host,command)
            print(command)

            cv.imshow('Detections', image_out)
            cv.waitKey(50) 

            if (current_state == 12):
                unity_send_text(host,"Congratulations! You have completed the Bulldozer.")
                print("Congratulations! You have completed the Bulldozer.")
                break

            timer += 1
        else:
            cv.imshow('Bulldozer Detections', image_out)
            cv.waitKey(1) 
            timer += 1

client.close()

hl2ss.stop_subsystem_pv(host, port)