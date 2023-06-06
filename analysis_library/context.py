from analysis_library.packages import *

def update_results_buffer(results_buffer ,instance_results):
    results_buffer.insert(0,instance_results)
    results_buffer.pop()
    return results_buffer 

def buffer_median(results_buffer):
    buffer_size = len(results_buffer)
    loose_wheel_count = []
    fitted_wheel_count = []
    wheel_slot_count = []
    loose_blade_count = [] 
    fitted_blade_count = []
    loose_cabin_count = []
    cabin_slot_count = []
    screw_count = []

    for i in results_buffer:
      loose_wheel_count.append(i[0])
      fitted_wheel_count.append(i[1])
      wheel_slot_count.append(i[2])
      loose_blade_count.append(i[3])
      fitted_blade_count.append(i[4])
      loose_cabin_count.append(i[5])
      cabin_slot_count.append(i[6])
      screw_count.append(i[7])

    loose_wheel_count.sort()
    fitted_wheel_count.sort()
    wheel_slot_count.sort()
    loose_blade_count.sort()
    fitted_blade_count.sort()
    loose_cabin_count.sort()
    cabin_slot_count.sort()
    screw_count.sort()

    median_counts = [loose_wheel_count[buffer_size//2], fitted_wheel_count[buffer_size//2], 
                     wheel_slot_count[buffer_size//2],loose_blade_count[buffer_size//2],
                     fitted_blade_count[buffer_size//2],loose_cabin_count[buffer_size//2],
                     cabin_slot_count[buffer_size//2],screw_count[buffer_size//2]]

    return median_counts

def generate_results_count(result):
   
   if (result['name'].eq('loose_wheel')).any():
        loose_wheel_count = result['name'].value_counts()['loose_wheel']
   else:
        loose_wheel_count = 0

   if (result['name'].eq('loose_cabin')).any():
        loose_cabin_count = result['name'].value_counts()['loose_cabin']
   else:
        loose_cabin_count = 0

   if (result['name'].eq('loose_blade')).any():
        loose_blade_count = result['name'].value_counts()['loose_blade']
   else:
        loose_blade_count = 0
  
   if (result['name'].eq('fitted_blade')).any():
        fitted_blade_count = result['name'].value_counts()['fitted_blade']
   else:
        fitted_blade_count = 0
   
   if  (result['name'].eq('fitted_wheel')).any():
       fitted_wheel_count = result['name'].value_counts()['fitted_wheel']
   else:
        fitted_wheel_count = 0
   
   if  (result['name'].eq('wheel_slot')).any():
       wheel_slot_count = result['name'].value_counts()['wheel_slot']
   else:
       wheel_slot_count = 0

   if  (result['name'].eq('cabin_slot')).any():
       cabin_slot_count = result['name'].value_counts()['cabin_slot']
   else:
       cabin_slot_count = 0

   if  (result['name'].eq('screw')).any():
       screw_count = result['name'].value_counts()['screw']
   else:
       screw_count = 0

   counts = [loose_wheel_count,fitted_wheel_count,wheel_slot_count,loose_blade_count,fitted_blade_count,loose_cabin_count,cabin_slot_count,screw_count]
   
   return counts
          
def state_machine(current_state,detections,previous_command):

    command = previous_command

    loose_wheel_count  = detections[0]
    fitted_wheel_count = detections[1]
    wheel_slot_count   = detections[2]
    loose_blade_count  = detections[3]
    fitted_blade_count = detections[4]
    loose_cabin_count  = detections[5]
    cabin_slot_count   = detections[6]
    screw_count        = detections[7]

    #              States                   # 
    # "State Detection" current_state = 0

    # "Collect Loose Wheel" current_state = 1
    # "Collect Screw (Wheel)" current_state = 2 
    # "Fit Wheel" current_state = 3 

    # "Collect Loose Cabin" current_state = 4
    # "Collect Screw (Cabin)" current_state = 5 
    # "Fit Cabin" current_state = 6

    # "Collect Loose Blade" current_state = 7
    # "Collect Screw (Blade)" current_state = 8 
    # "Fit Blade" current_state = 9

    if ((current_state == 0) and (detections == [0,0,0,0,0,0,0,0])):
        current_state = 0
        command = "No bulldozer detected"
        return current_state , command
    
    if (current_state == 0): 
        if (wheel_slot_count > 0 ):
            current_state = 1
            command = "Collect a loose wheel"
            return current_state , command
        if (cabin_slot_count == 1):
            current_state = 4
            command = "Collect the loose cabin"
            return current_state , command
        if ( (fitted_blade_count == 1) and (fitted_wheel_count == 2)): #Needs to be made more robust
            current_state = 12
            command = "Congratulations you've successfully assembled Bulldozer"
            return current_state , command
        if ( (loose_blade_count == 0) and (fitted_blade_count == 0) ):
            current_state = 7 
            command = "Collect the loose blade"
            return current_state , command

        return current_state , command

    #Collection of parts
    if (current_state == 1 and fitted_wheel_count == 0): 
        if (loose_wheel_count > 0): 
            current_state = 2
            command = "Collect a screw for the wheel"
            return current_state , command
        
        return current_state , command
    
    if (current_state == 1 and fitted_wheel_count == 1): 
        if (loose_wheel_count > 0): 
            current_state = 21
            command = "Collect a screw for the second wheel"
            return current_state , command
        
        return current_state , command
    
    if (current_state == 4): 
        if (loose_cabin_count > 0): 
            current_state = 5
            command = "Collect a screw for the cabin"
            return current_state , command
        
        return current_state , command
    
    if (current_state == 7): 
        if (loose_blade_count > 0): 
            current_state = 8
            command = "Collect a screw for the blade"
            return current_state , command
        
        return current_state , command
    
    #Collection of screws
    if (current_state == 2): 
        if (screw_count> 0): 
            current_state = 3
            command = "Fit the wheel"
            return current_state , command
        
        return current_state , command
    
    if (current_state == 5): 
        if (screw_count > 0): 
            current_state = 6
            command = "Fit the cabin"
            return current_state , command
        
        return current_state , command
    
    if (current_state == 8): 
        if (screw_count > 0): 
            current_state = 9
            command = "Fit the blade"
            return current_state , command
        
        return current_state , command
    
    if (current_state == 21): 
        if (screw_count > 0): 
            current_state = 22
            command = "Fit the second wheel"
            return current_state , command
        
        return current_state , command
    

    
    #Ensure part fit
    if (current_state == 3): 
        if (fitted_wheel_count == 1): #This does not validate that a second wheel has been fitted yet 
            current_state = 0
            command = "Well done the wheel is fitted"
            return current_state , command
        
        return current_state , command
    
    if (current_state == 6): 
        if (loose_cabin_count == 0 and cabin_slot_count == 0): 
            current_state = 0
            command = "Well done the cabin is fitted"
            return current_state , command
        
        return current_state , command
    
    if (current_state == 9): 
        if (fitted_blade_count == 1): 
            current_state = 0
            command = "Well done the blade is fitted"
            return current_state , command
        
        return current_state , command
    
    if (current_state == 22): 
        if (fitted_wheel_count == 2): 
            current_state = 0
            command = "Well done the second wheel is fitted"
            return current_state , command
        
        return current_state , command

    
    command = "Please adjust the bulldozer"
    return current_state , command
