from analysis_library.packages import *
from analysis_library.context import *
from analysis_library.visual import *

def bulldozer_statemachine_analysis():
    #Analysis Functions Initalisation
    buffer_size = 20
    results_buffer = [[0,0,0,0,0,0,0,0]]*buffer_size 
    current_state = 0
    command = ""

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    path = 'weights_collection/Bulldozer_detector.pt'
    model = torch.hub.load('WongKinYiu/yolov7', 'custom', f"{path}",force_reload=True, trust_repo=True).autoshape()

    #Initiating Camera
    cam_port = int(input("Enter Camera Port: (0,1,2,...) "))
    cam = cv.VideoCapture(cam_port)
    cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    while True:
        
        check, image = cam.read()

        if check:

            #Converting Image and producing detectio results
            converted = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            results = model(converted)
            results = results.pandas().xyxy[0]
            results = results[results.confidence >= 0.05]

            #Generating State 
            generated_results = generate_results_count(results)
            results_buffer = update_results_buffer(results_buffer,generated_results)
            median_result = buffer_median(results_buffer)

            current_state, command = state_machine(current_state,median_result,command)

            #Displaying Detection Stream
            display_save_bounding_boxes(results,image)
            image = cv.resize(image, (1280 , 720))
            draw_text(image, command)
            cv.imshow('Bulldozer Detections', image)
            cv.waitKey(50) 

            if (current_state == 12):
                print("Congratulations! You have completed the sequence!")
                break
