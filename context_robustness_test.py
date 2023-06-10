#Imports
from analysis_library.packages import *
from analysis_library.context import *
from analysis_library.visual import *
from analysis_library.locational import *

def calculate_context_score(ground_truth,prediction):

    #Determine TP,TN,FP,FN
    TP = 0
    TN = 0
    FP = 0
    FN = 0

    for i in range(len(ground_truth)):
        if ground_truth[i] == prediction[i] and ground_truth[i] != 0:
            TP += 1
        elif ground_truth[i] == 0 and prediction[i] == 0:
            TN += 1
        elif ground_truth[i] == 0 and prediction[i] != 0:
            FP += 1
        elif ground_truth[i] != 0 and prediction[i] == 0:
            FN += 1
    
    #Calculate Precision, Recall, F1
    precision = TP/(TP+FP)
    recall = TP/(TP+FN)
    F1 = 2*((precision*recall)/(precision+recall))

    return F1,precision,recall



#test_sequence_location = str(input("Please enter the location of the test sequence: "))
test_sequence_name  = str(input("Enter Test Folder Directory Name: "))
folder_dir_load = 'test_sequences/Bulldozer - Context/'+test_sequence_name

weights_file = "Bulldozer_detector.pt"
#weights_file = str(input("Enter Weights File Name: "))
weights_dir =  'weights_collection/'+weights_file

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = torch.hub.load('WongKinYiu/yolov7', 'custom', f"{weights_dir}",force_reload=True, trust_repo=True).autoshape()

print("Context Analysis")
results_list = []
sequence_length = len(os.listdir(folder_dir_load+"/input_images")) 
print("Sequence Length: "+str(sequence_length))

for i in range(1,sequence_length+1):
    print("Image: "+str(i))
    image = cv.imread(folder_dir_load+"/input_images/"+test_sequence_name+"_"+str(i)+".jpg")
    print("Detecting")
    converted = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    results = model(converted)
    results = results.pandas().xyxy[0]
    results = results[results.confidence >= 0.1]
    print(results)
    
    #Generating State 
    generated_result = generate_results_count(results)
    #Updating results list
    results_list.append(generated_result)

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

for i in range(len(results_list)):
    gt = ground_truth_list[i]
    pred = results_list[i]
    F1,precision,recall = calculate_context_score(gt,pred)
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



