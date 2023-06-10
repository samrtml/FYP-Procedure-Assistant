#Imports
from analysis_library.packages import *
from analysis_library.context import *
from analysis_library.visual import *
from analysis_library.locational import *

def calculate_locational_score(ground_truth,prediction):

    #Determine TP,TN,FP,FN
    TP = 0
    TN = 0
    FP = 0
    FN = 0

    for i in range(len(ground_truth)):
        if ground_truth[i] == prediction[i] and ground_truth[i] != 'empty':
            TP += 1
        elif ground_truth[i] == 'empty' and prediction[i] == 'empty':
            TN += 1
        elif ground_truth[i] == 'empty' and prediction[i] != 'empty':
            FP += 1
        elif ground_truth[i] != 'empty' and prediction[i] == 'empty':
            FN += 1

    print("TP: "+str(TP) + " TN: "+str(TN) + " FP: "+str(FP) + " FN: "+str(FN))
    
    #Calculate Precision, Recall, F1
    precision = TP/(TP+FP)
    recall = TP/(TP+FN)
    F1 = 2*((precision*recall)/(precision+recall))

    return F1,precision,recall

#test_sequence_location = str(input("Please enter the location of the test sequence: "))
test_sequence_name  = str(input("Enter Test Folder Directory Name: "))
folder_dir_load = 'test_sequences/Chess - Locational/'+test_sequence_name

weights_file = "Chess_detector.pt"
#weights_file = str(input("Enter Weights File Name: "))
weights_dir =  'weights_collection/'+weights_file

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = torch.hub.load('WongKinYiu/yolov7', 'custom', f"{weights_dir}",force_reload=True, trust_repo=True).autoshape()

print("Locational Analysis")
results_list = []
sequence_length = len(os.listdir(folder_dir_load+"/input_images")) 
print("Sequence Length: "+str(sequence_length))


for i in range(1,sequence_length+1):
    print("Image: "+str(i))
    image = cv.imread(folder_dir_load+"/input_images/"+test_sequence_name+"_"+str(i)+".jpg")
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
    #Updating results list
    results_list.append(locational_detections)

#Writing results list to csv
file = open(folder_dir_load+'/generated_state_list.csv', "w")
writer = csv.writer(file)
for data_list in results_list:
    writer.writerow(data_list)
file.close()

#Reading in ground truth results list from csv
ground_truth_list = []

file = open(folder_dir_load+'/'+test_sequence_name+'.csv', 'r')
try:
    ground_truth_list = [list(map(int,rec)) for rec in csv.reader(file, delimiter=',')]
except:
    ground_truth_list = list(csv.reader(file, delimiter=","))
file.close()

#Generating Scores

print("Generating Precision, Recall, F1")
test_performance = []

print("Sequence Length: "+str(len(ground_truth_list)))

for i in range(len(ground_truth_list)):
    gt = ground_truth_list[i]
    pred = results_list[i]
    F1,precision,recall = calculate_locational_score(gt,pred)
    test_performance.append([F1,precision,recall])
    print("Performance for State "+str(i)+":")
    print("F1: "+str(F1)+" Precision: "+str(precision)+" Recall: "+str(recall))

file = open(folder_dir_load+'/test_performance.csv', "w")
writer = csv.writer(file)
for data_list in test_performance:
    writer.writerow(data_list)
file.close()

print("Average Sequence Performance: ")
print("F1: "+str(np.mean([i[0] for i in test_performance]))+" Precision: "+str(np.mean([i[1] for i in test_performance]))+" Recall: "+str(np.mean([i[2] for i in test_performance])))
