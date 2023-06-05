
#Imports
from analysis_library.imports import *


def main():
    print("Welcome to the sequence generator!")
    
    live_select = input("Would you like to generate a sequence from a live video stream? (y/n): ")

    if live_select == "y":
        live_capture()
        #predefined_generate()

    elif live_select == "n":
        print("la")
        #predefined_generate()

    else:
        print("Invalid input. Please try again.")
        main()


def live_capture():

    #Create Sequence Folder
    sequence_name = input("Enter the name of the sequence: ")
    os.mkdir('generated_sequences/'+sequence_name)

    #Create Command List in Sequence Folder
    command_list_file = open('generated_sequences/'+sequence_name+'/command_list.csv', 'w+')
    csv_writer = csv.writer(command_list_file)

    #Initiating Camera
    cam_port = 0
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
                cv.imwrite('generated_sequences/'+sequence_name+'/'+sequence_name+str(image_count)+'.jpg', image)

    while True:

        if input("Are you ready to capture the current state (Enter anything to procede)"):

            #Eliminating strange 5 frame buffer issue
            for i in range(5):
                check, image = cam.read()

            if check:
                #Saving Image to Sequence Folder
                image_count = image_count + 1
                cv.imwrite('generated_sequences/'+sequence_name+'/'+sequence_name+str(image_count)+'.jpg', image)


            #Write Command to Command List CSV
            command = input("Enter instruction/command which took place from the previous to the current state: ")
            csv_writer.writerow([command])

                
                
            if (input("Have you finished the sequence (y to exit)") == "y"):
                break
    
    #Close Command List
    command_list_file.close()


main()




# def predefined_generate():

#     image_folder = input("Enter the path to the folder containing the image sequence: ")

#     locational_select = input("Does your procedure require locational analysis? (y/n): ")

#     if locational_select == "y":
#         locational_analysis(image_folder)
    
#     elif locational_select == "n":
#         non_locational_analysis(image_folder)

#     else:
#         print("Invalid input. Please try again.")
#         predefined_generate()

# def locational_analysis(image_folder):
#     #TODO: Implement locational analysis

# def non_locational_analysis(image_folder):


