import random
import numpy
import numpy as np
import math
from numpy import ndarray

from numpy import (array, dot, arccos)
from numpy.linalg import norm
import sys
my_path ='/Users/ranjitha/Desktop/2SEM/ENTS656'
sys.path.append(my_path)
import modules_656project as md


#basic paramaeters
road_l=6 #km
del_t=1 #sec
tot_sim_t= 1 # 1 or more hrs, total simulation time
tot_sim_sec = tot_sim_t*3600
p_call =1800

#each basestation may have the following propertities, some of which may be varied
hb= 50 #in m, this is the basestation anyenna height
# change to km loc_b = 20 # m west of the road at the midpoint of the road(3 km if the road is 6 km)
# 1 meter = 0.001 km
loc_b = 20

POW_TX=43 # dBm TX Power
LOSS = 2# db line/connector losses
AG_GAIN_TX = 15 #dbi, antenna gain
NUM_CH_A = 15 #per sector, no of traffice channels
NUM_CH_B = 15 
ALPHA_F=860 #MHz
BETA_F= 865 #MHz

#the mobile will have the following properties, some of which may be varied
hm = 1.5 #in m, height of mobile
HOM = 3# db handoff margin
RSL_T = -102 #dBm mobile Rx Threshold

#users uniformly distributed
NO_USERS =160
lam = float(2)/float(3600) #  2calls per hour(on average) 1800 seconds 2/3600
h = 3#minutes/call (=180 seconds/call)
V_SPEED= 15#m/s (=54 kph = 33.553977 mph)
# direction 50/50 chance of heading north or south
path = "/Users/ranjitha/Downloads/antenna_pattern.txt"
s = numpy.loadtxt(path, unpack=True)


global active_users
active_users={}
#active_users={517: [{'user_loc': 5500}, {'time': 50}, {'user_dir': 'south'}, {'user_distance': 1976.0684225631585}, {'sector': 'Beta'}, {'call_status': 'Call Established'}, {'call length': 5000}, {'rsl': -81.112321193743767}]}
global failed_users
failed_users={}
global user_details
user_details =[]
user_non_active=[]
dropped_call={}
blocked_call=[]
#archieve_users
global archieve_users
archieve_users=[]

#archieve_users =[]
#print "Dec archieve_users",archieve_users

user_Dir = ''

serving_sector=''
global u  

def user_makes_new_call(i,j):
    #x = numpy.random.random_integers(1,1800)
    #p_call = 1800
    global active_users
    x = numpy.random.random_sample()
    p_call = 1.0/1800.0
    #if p_call == x:
    if x<= p_call:
        
        user_details =[]
        #print "I am inside"
        ''' Initiate a call
                '''
        '''determine the users location along the road
                '''
        user_loc = np.random.uniform(low=0.0, high=6000.0, size=None)
        
        #user_loc = 5900
        user_details.append({"user_loc":user_loc})
        '''determine users direction (north or south)
                '''
        user_dir = numpy.random.randint(2)
        
        
        '''to determine distance between the mobile and base station
                              '''
        user_details.append({"time":j})
        if user_dir == 0:
            #North
            user_details.append({"user_dir":"north"})
            distance_user = 3000 - user_loc
            #print ",", distance_user
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            
            #print "dist_mob2base",dist_mob2base
        elif user_dir == 1:
            user_details.append({"user_dir":"south"})
            distance_user = user_loc - 3000
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            #print dist_mob2base
            user_details.append({"user_distance":dist_mob2base})
                   
            '''Find the RSL at the mobile from each sector
               md--->modules_656project.py '''
        rsl_sectorA,rsl_sectorB = md.rsl_eirp(dist_mob2base,user_loc)
        #print "rsl",rsl_sectorA,rsl_sectorB 
        '''RSLSERVER is greater than or equal to the RSL threshold
            '''
        rsl_mob = max(rsl_sectorA,rsl_sectorB)
        call_length = int(numpy.random.exponential(scale=180))

        if rsl_mob < RSL_T:
            
            '''call attempt failed due to signal strength less than threshold
                And move to the next user
                '''
            if rsl_sectorA > rsl_sectorB:
                sector = "alpha"
            else:
                sector = "beta"
            user_details.append({"sector": sector})
            user_details.append({"call_status":"Call Failed"})
            user_details.append({"Call Dropped":"Signal Strength"})
            active_users[i]=user_details
            return 0
        else:
            ''' maximum rsl among alpha and beta is taken as the serving sector
                '''
            if rsl_sectorA > rsl_sectorB:
                sector = "alpha"
                #user_details.append(sector)
                if md.NUM_CH_A !=0:
                    user_details.append({"sector":sector})
                    md.NUM_CH_A -=1
                    user_details.append({"call_status":"Call Established"})
                    user_details.append({"call length":call_length})
                    user_details.append({"rsl":rsl_sectorA})
                    active_users[i]=user_details
                else:
                    user_details =[]
                    user_details.append({"sector": sector})
                    user_details.append({"call_status":"Call Failed"})
                    user_details.append({"call_blocked":sector})
                    user_details.append({"capacity":"Insufficent_Capacity"})
                    failed_users[i]=user_details
                    '''other sector has sufficient signal strength to be
                        the serving sector and greater than threshold
                        '''
                    if rsl_sectorB > RSL_T:
                        sector = "beta"
                        if md.NUM_CH_B !=0:
                            user_details.append({"sector":sector})
                            md.NUM_CH_B = md.NUM_CH_B-1
                            user_details.append({"call_status":"Call Established"})
                            user_details.append({"call length":call_length})
                            user_details.append({"rsl":rsl_sectorB})
                            active_users[i]=user_details
                            
            else:
                sector = "beta"
                #user_details.append(sector)
                if md.NUM_CH_B !=0:
                    user_details.append({"sector":sector})
                    md.NUM_CH_B = md.NUM_CH_B-1
                    user_details.append({"call_status":"Call Established"})
                    user_details.append({"call length":call_length})
                    user_details.append({"rsl":rsl_sectorB})
                    active_users[i]=user_details
                else:
                    user_details =[]
                    user_details.append({"sector": sector})
                    user_details.append({"call_status":"Call_Failed"})
                    user_details.append({"call blocked":sector})
                    user_details.append({"capacity":"Insufficent Capacity"})
                    failed_users[i]=user_details
                    '''other sector has sufficient signal strength to be
                        the serving sector and greater than threshold
                        '''
                    
                    if rsl_sectorA > RSL_T:
                        sector = "alpha"
                        if md.NUM_CH_A !=0:
                            user_details.append({"sector":sector})
                            md.NUM_CH_A = md.NUM_CH_A-1
                            user_details.append({"call_status":"Call Established"})
                            user_details.append({"call length":call_length})
                            user_details.append({"rsl":rsl_sectorA})
                            active_users[i]=user_details
                    
    else:
        #print "call not made"
        return 0
    #print "New users",active_users

def user_has_call():
    user_dir =''
    serving_sector =''
    new_user_loc=0
    global active_users
    #archieve_users
    global archieve_users
    
    
    #print "listing", list(active_users)
    for each_users in active_users:
        #print "each_users",each_users
        is_handoff=2
        if len(active_users[each_users]) == 0:
            break
            print " "
        else:
            for details2 in active_users[each_users]:
                for k,v in details2.items():
                    #print k,v
                    if k == 'user_dir':
                        #print "user_dir",v
                        user_dir = v
            for details3 in active_users[each_users]:
                for key,value in details3.items():
                    if key == 'sector':
                        serving_sector = value
                        #print "serving_sector",serving_sector
            for details4 in active_users[each_users]:
                for key,value in details4.items():
                    if key == 'user_loc':
                        #print "user moving"
                        #print key,value
                        #print "user_Dir",user_dir
                        if user_dir == 'north' and value >0 :
                            #print "details[key]=value-V_SPEED",value-V_SPEED
                            details4[key]=value-V_SPEED
                        elif user_dir == 'south' and value <6000 :
                            #print "details[key]=value-V_SPEED",value+V_SPEED
                            details4[key]=value+V_SPEED
                        if value <0 or value >6000:
                            #print ("ho ho")
                            active_users[each_users].append({"Call_exit_status":"Successful call"})
                            archieve_users.append(active_users[each_users])
                            active_users[each_users] = []
                            if serving_sector == 'alpha':
                                md.NUM_CH_A +=1
                            else:
                                #print "NUM_CH_B",NUM_CH_B
                                md.NUM_CH_B +=1
            for details5 in active_users[each_users]:
                for key,value in details5.items():
                    if key == 'call length':
                        if value > 0:
                            details5[key]=value-1
                        elif value == 0:
                            active_users[each_users].append({"Call_exit_status":"Successful call"})
                            archieve_users.append(active_users[each_users])
                            active_users[each_users] = []
                            if serving_sector == 'alpha':
                                md.NUM_CH_A +=1
                            else:
                                #print "NUM_CH_B",NUM_CH_B
                                md.NUM_CH_B +=1
            #if len(active_users[each_users])==0:
                #print "contiue"
                #continue
            #else:
            #print ("RSL REcal")
            for details1 in active_users[each_users]:
                for key,value in details1.items():
                    if key == 'user_loc':
                        new_user_loc = value
                    #print "new_user_loc",new_user_loc
            if new_user_loc > 3000:
                dist2mobbase_new = new_user_loc - 3000
            else:
                dist2mobbase_new = 3000-new_user_loc
            dist_mob2base_send = math.sqrt((loc_b**2 + dist2mobbase_new**2))
                #print "details",details
            rsl_sectorA,rsl_sectorB = md.rsl_eirp(dist_mob2base_send,new_user_loc)
                #rsl_sectorA,rsl_sectorB = -100,-90
            #print "dist_mob2base_send,new_user_loc",dist_mob2base_send,new_user_loc
            #print "rsl_sectorA,rsl_sectorB ",rsl_sectorA,rsl_sectorB 
            '''RSLSERVER is greater than or equal to the RSL threshold
                                '''
            if serving_sector == "alpha":
                rsl_mob = rsl_sectorA
            else:
                rsl_mob = rsl_sectorB
            for details8 in active_users[each_users]:
                for key,value in details8.items():
                    if key == 'rsl':
                        details8[key]=rsl_mob
            
                            
            if rsl_mob < RSL_T:
                #print "True"
                
                '''call attempt failed due to signal strength less than threshold
                                And move to the next user
                '''
                if rsl_sectorA > rsl_sectorB:
                    sector = "alpha"
                else:
                    sector = "beta"
                active_users[each_users].append({"sector": sector})
                active_users[each_users].append({"call_status":"Call Failed"})
                active_users[each_users].append({"Call Dropped":"Signal Strength"})
                #print "archieve_users",type(archieve_users),active_users[each_users]
                archieve_users.append(active_users[each_users])
                active_users[each_users] = []
                #print "active_users",active_users
                #print "archieve_users",archieve_users
                if serving_sector == 'alpha':
                    md.NUM_CH_A +=1
                else:
                    md.NUM_CH_B +=1
    
            else:
                if is_handoff >1:
                    #print "handoff open"
                    #print "serving_sector",serving_sector
                    if serving_sector == 'alpha':
                        #print "serving_sector",serving_sector
                        if rsl_sectorB >= rsl_sectorA + HOM:
                            #print "handoff happenning"
                            active_users[each_users].append({"hand_off": serving_sector})
                            if md.NUM_CH_B >0:
                                for details6 in active_users[each_users]:
                                    for key,value in details6.items():
                                        if key == 'sector':
                                            details6[key]="beta"
                                                #continue
                                        if key == 'rsl':
                                            details6[key] = rsl_sectorB
                                                
                                active_users[each_users].append({"hand_off_status": "Successful"})
                                is_handoff +=1
                                md.NUM_CH_A -=1
                                md.NUM_CH_B +=1
                            else:
                                active_users[each_users].append({"hand_off_status": "Failure"})
                                is_handoff +=1
                    else:
                        if rsl_sectorA >= rsl_sectorB + HOM:
                            #print "handoff happenning"
                            active_users[each_users].append({"hand_off": serving_sector})
                            if md.NUM_CH_A >0:
                                for details7 in active_users[each_users]:
                                    for key,value in details7.items():
                                        if key == 'sector':
                                            details7[key]="alpha"
                                        if key == 'rsl':
                                            details7[key] = rsl_sectorA
                                active_users[each_users].append({"hand_off_status": "Successful"})
                                is_handoff +=1
                                md.NUM_CH_A +=1
                                md.NUM_CH_B -=1
                            else:
                                active_users[each_users].append({"hand_off_status": "Failure"})
                                is_handoff +=1
            #print each_users                                  
        
''' For hw2cell.docxach user that does not have a call up
    '''

''' Probablity of a call = λ*ΔT ; probability of a call is taken from 1 to 1800
    which will be 1 in 1800 and checked with a random number say 1800 
    '''

#time
print "Welcome to Python application which will simulate the downlink behavior of a 3-sectored basestation"

'''Initial simulation of 1 hour
    '''
#def user_has_call(j):

    
#    return 0

#for i in range (tot_sim_sec):
def main():
    no_calls_can_make = 0
    active=0
    md.shadow_pre_cal()
    NO_USERS = 160
    
    archieve_users_list=[]
    #archieve_users=list()
    for i in range (3600):
        '''160 users always on the road
        time        '''
        if(len(active_users)!=0):
                user_has_call()
        for j in range (NO_USERS):
            
            user_makes_new_call(j,i)


main()

f = open( 'file1.txt', 'w' )
f.write(repr(archieve_users))
f.close()
f = open( 'file2.txt', 'w' )
f.write(repr(active_users))
f.close()
f = open( 'file3.txt', 'w' )
f.write(repr(failed_users))
f.close()


def num_of_call(sector_name):
    global active_users
    #archieve_users
    global archieve_users
    number_calls_active=0
    number_calls_archieve=0
    tot_calls=0
    hand_off=0
    success_call=0
    hand_off_F = 0
    hand_off_S_A = 0
    hand_off_S_Ar = 0
    drop_capacity = 0
    drop_strength =0
    sector_found=''
    sector_found1=''
    if sector_name == "alpha":
        no_ch_use = 15 - md.NUM_CH_A
    else:
        no_ch_use = 15 - md.NUM_CH_B
    for each_users in active_users:
        for details2 in active_users[each_users]:
            for key,value in details2.items():
                if key == 'sector' and value == sector_name:
                    number_calls_active +=1
                    sector_found = value
                if key =='hand_off_status' and value == 'Successful'and sector_found == sector_name :
                    hand_off_S_A = hand_off_S_A+1
                if key =='hand_off_status' and value == 'Failure'and sector_found == sector_name :
                    hand_off_F = hand_off_F+1
                if key =='capacity' and value == 'Insufficent_Capacity'and sector_found == sector_name :
                    drop_capacity +=1
                    #Call Dropped":"Signal Strength
                if key =='Call Dropped"' and value == 'Signal Strength' and sector_found == sector_name :
                    drop_strength +=1
    
    for each_users in failed_users:
        #print "each_users",failed_users[each_users]
        for details1 in failed_users[each_users]:
            for key,value in details1.items():
                #print key,value
                if key == 'sector':
                    sector_found1 = value
                    #print "found",sector_found1
                    #number_calls_active +=1
                    #sector_found1 = value
                #print sector_found1
        for details9 in failed_users[each_users]:
            for key,value in details9.items():
                #print key,value
                if key =='capacity' and sector_found1 == sector_name :
                    #print "inc iiiiiiiiii",sector_found1
                    drop_capacity +=1
                    
                    #Cal Dropped":"Signal Strength
                if key =='Call Dropped"' and value == 'Signal Strength' and sector_found1 == sector_name :
                    drop_strength +=1               
                
    #print number_calls_active
    for each_users in range(0,len(archieve_users)):
        for details3 in archieve_users[each_users]:
            for key,value in details3.items():
                if  key == 'sector' and value == sector_name:
                    sector_found = value
                    number_calls_archieve +=1
                if sector_found ==sector_name and  key == 'Call_exit_status' and value == 'Successful call':
                    success_call +=1
                if key =='hand_off_status' and value == 'Successful'and sector_found == sector_name :
                    hand_off_S_Ar = hand_off_S_Ar+1
                if key =='hand_off_status' and value == 'Failure'and sector_found == sector_name :
                    hand_off_F = hand_off_F+1
                if key =='capacity' and value == 'Insufficent_Capacity'and sector_found == sector_name :
                    drop_capacity +=1
                    #Call Dropped":"Signal Strength
                #print key,value    
                if key =='Call Dropped' and value == 'Signal Strength' and sector_found == sector_name :
                    #print key,value
                    drop_strength +=1
                
                    
                
    #print number_calls_archieve
    tot_calls = number_calls_active + number_calls_archieve
    print ("The number of channels currently ",no_ch_use)
    print ("The number of call attempts ",tot_calls)
    print ("The number of successful calls",success_call)
    print ("The number of successful handoffs ", hand_off_S_A+hand_off_S_Ar)
    print ("The number of handoff failures into and out of each sector",hand_off_F)
    print ("The number of call drops  due to capacity",drop_capacity )
    print ("The number of call drops due to low signal strength ",drop_strength )

    

num_of_call("beta")
num_of_call("alpha")

 
                
            
                
        


        