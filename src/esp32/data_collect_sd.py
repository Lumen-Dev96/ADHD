import utime
from kalman import KALMAN
import network
import time
import machine
from mpu6050 import MPU6050
import _thread
import sd_card
import os

import gc
try :
    import usocket as socket
except:
    import socket
from machine import RTC

print("Finish the import library..")
Command_List={
    "stop" : 'IMU will Stop all the measurement',
    "listdirectory": 'List all the file within the SD card',
     "invalid commnad":"Recieve some invalid command ",
     "Detect_And_Save_as":'Save all the detection to the given file',
     "Update_Local_Time_as":"Reset the time stamp of the IMU..",
     "Check_IMU_Time":"Check the clock reading of the IMU...",
     "Real_time_Detection_and_Save_as":"Save all the detection to the given file and send it in real time",
}
# define global variable for thread control
Measurment=False
Real_Time_Detection=False
mpu_is_ok=False
Outfile_Name=""
File_List=[]
Data_Buffer=[]
lock = _thread.allocate_lock() # the lock for
Finish_writing=False
#PC_Time_Stamp=None
#UTC_OFFSET=8*60*60
Message=""
rtc=RTC()
def all_mpu_init():
    global mpu_is_ok
    if mpu1.init() and mpu2.init():
        mpu_is_ok = True
        print('MPU is init success')
    else:
        mpu_is_ok = False
        print('MPU is init failed')
    
# Handling Command from remote control
def Command_listener(client,sd):
    uart = machine.UART(1, baudrate=115200)
    global running_threads
    global Measurment
    global SD_Avaliable
    global File_List
    global Outfile_Name
    global rtc
    output_buffer=[] #
    global Real_Time_Detection
    os.mount(sd, '/sd')
    #print("Open sd card directory..")
    dir_list = os.listdir('/sd')
    for txtfile  in os.listdir('/sd/mpuData') :
            #print(txtfile)
            if txtfile.endswith(".txt") :
                print(txtfile)
                File='sd/mpuData/'+txtfile
                File_List.append(File)
                #print(File)
    #broadcast("The current time is "+str(time_lib.get_format_date()))
    client.send("The current time of IMU 1 is "+str(rtc.datetime()))
    while True:
        Command= client.recv(1024).decode()  # receive data from the remote controller
        Command=Command.split(":")
        if len(Command)>=2:
            
            Command=Command[1]
            
            Command=Command.replace(" ", "")
        else:
            Command="invalid commnad"
        #print("Recieved "+Command)
        #print(list(Command_List.keys()),Command)
        if Command=="Check_IMU_Time":
            client.send("IMU1 time is "+str(rtc.datetime()))
        if "Detect_And_Save_as" in Command:
            File_Name=Command.split("as")[1]
            #print("File Name will be ",File_Name)
            if File_Name!="":
                Outfile_Name=File_Name.replace(" ", "")
                Outfile_Name="IMU1_"+Outfile_Name
                Measurment=True
                start_time= utime.time()
                client.send("IMU 1 will save the following file as : "+File_Name)
            else:
                client.send("Please provide the file name like: Detect_And_Save_as file_Name"+Outfile_Name)
        if "Real_time_Detection_and_Save_as" in Command:
            File_Name=Command.split("as")[1]
            Real_Time_Detection=True
            print("Detect in real time and save as ",File_Name)
            if File_Name!="":
                Outfile_Name=File_Name.replace(" ", "") #  get the file Name from the command 
                Outfile_Name="IMU1_"+Outfile_Name # Adding the prefix to prevent confusion 
                #print("Output file Name is ",Outfile_Name)
                start_time= utime.time()
            else:
                client.send("Please provide the file name like: Real_time_Detection_and_Save_as file_Name")
        
        if "Update_Local_Time_as" in Command:
            Current_Time=Command.split("as")[1]
            if Current_Time!="":
                print("Current time from pc is ",Current_Time)
                date_list=Current_Time.split("-")
                date = (int(date_list[0]), int(date_list[1]), int(date_list[2]),int(date_list[3]), int(date_list[4]), int(date_list[5]),int(date_list[6]),int(date_list[7]+"000"))
                rtc.datetime(date)
                client.send("IMU1 time is "+str(rtc.datetime()))
                #print(rtc.datetime())
                
            
        if Command=="stop":
            Measurment=False
            Real_Time_Detection=False
            client.send("Measurment status in IMU1 is "+str(Measurment)+" , "+str(Real_Time_Detection))
            end_time= utime.time()
            print("We spend ",end_time-start_time," to detect")
        if Command=="listdirectory":
            client.send('List all the file within the SD card')
            File_Block=""
            for f in File_List:
                client.send("IMU1 has "+f)
                print(f)
            
        if Command in File_List:
            Retriving_File = open(Command,'rb')
            #print("Excuting send file command ",Retriving_File)
            #start_time= utime.time()
            while True:
                chunk=Retriving_File.read(16384)  # Adjust chunk size if needed
                #print(chunk,type(chunk))
                if not chunk:
                        #End_Time=utime.time()
                        #print("Take ...",End_Time-start_time)
                        break
                else:
                    #print("Sending data...")
                    #broadcast(result+'\r\n')
                    # Write the chunk to UART for transmission to the PC
                    client.send(chunk)
                    # Delay to allow UART buffer to clear, may be adjusted based on testing
                    time.sleep_ms(50)

def Detecting_Data_in_Real_Time(mpu1,mpu2,client):
    global File_List
    global Outfile_Name
    global rtc
    global Real_Time_Detection
    Number_of_data=0
    Created_File=False
    data_file=None
    Data_Buffer= bytearray() # Byte array for faster excution and less memory occuption 
    flash_config = {'threshold': 20, 'shakeTime': 300, 'isOpenGyro': True, 'autoStop': False, 'autoStopCnt': 30000,'mapX1': 'X', 'mapX1Direct': 1, 'mapY1': 'Y', 'mapY1Direct': 1, 'mapZ1': 'Z', 'mapZ1Direct': 1,'mapX2': 'X', 'mapX2Direct': 1, 'mapY2': 'Y', 'mapY2Direct': 1, 'mapZ2': 'Z', 'mapZ2Direct': 1}
    #print("Real Time Thread is created")
    while True:
        if Created_File ==False and Real_Time_Detection==True:
            if Outfile_Name!="":
                data_file = open('/sd/mpuData/' + Outfile_Name + '.txt', 'a')
                Created_File=True
                #print("File created")
        while Real_Time_Detection==True and Created_File==True:
            mpu_data1 = mpu1.get_data(flash_config['isOpenGyro'])
            mpu_data2 = mpu2.get_data(flash_config['isOpenGyro'])
            Data = 'IMU1 start {0};{1};{2} end\r\n'.format(rtc.datetime(), mpu_data1, mpu_data2).encode('utf-8') # Use IMU1 to distinglish the where does the data comes from  
            Data_Buffer.extend(Data)
            Number_of_data = Number_of_data+1
            if len(Data_Buffer) >= 8192:  # Adjust this size as needed
                data_file.write(Data_Buffer)
                data_file.flush()
                client.send(Data_Buffer) # sending the data to the PC in real time 
                Data_Buffer = bytearray()  # Reset the buffer
                #print("we have detected ",Number_of_data)
                gc.collect()# release the RAM explictily to prevent memory allociation error 
        if Real_Time_Detection==False and Created_File==True: # detection end and the saving folder had been created 
            data_file.write(Data_Buffer)
            data_file.flush()
            File_List.append('sd/mpuData/' + Outfile_Name+'.txt' )# Update file list 
            Outfile_Name=""
            Created_File=False
            Data_Buffer= bytearray() # Assign a new bytearray for the next task 
            gc.collect()# release the RAM explictily to prevent memory allociation error 
            data_file.write("It is the end of File") # Indicate it is the end of the record 
            data_file.close() # Close the file to prevent the file error 
                    
                
def Detecting_data_from_MPU(mpu1,mpu2):
    print("Dteecting thread")
    global mpu_is_ok
    global File_List
    global Outfile_Name
    global Measurment
    Created_File=False
    data_file=None
    Data_Buffer= bytearray() # Byte array for faster excution and less memory occuption 
    flash_config = {'threshold': 20, 'shakeTime': 300, 'isOpenGyro': False, 'autoStop': False, 'autoStopCnt': 30000,
                    'mapX1': 'X', 'mapX1Direct': 1, 'mapY1': 'Y', 'mapY1Direct': 1, 'mapZ1': 'Z', 'mapZ1Direct': 1,
                    'mapX2': 'X', 'mapX2Direct': 1, 'mapY2': 'Y', 'mapY2Direct': 1, 'mapZ2': 'Z', 'mapZ2Direct': 1
                    }
    while True:
        if Created_File ==False and Measurment==True: # Create the file first 
               if Outfile_Name!="":
                    if "IMU1_" in Outfile_Name: # Ensure the file Name contains the prefix to distinglish sourse latter on 
                        data_file = open('/sd/mpuData/' + Outfile_Name + '.txt', 'a')
                        Created_File=True
                    else:
                        Outfile_Name="IMU1_"+Outfile_Name
                        data_file = open('/sd/mpuData/' + Outfile_Name + '.txt', 'a')
                        Created_File=True
        while Measurment==True and Created_File==True: # Ensure we have already created the file first 
                    mpu_data1 = mpu1.get_data(flash_config['isOpenGyro'])
                    mpu_data2 = mpu2.get_data(flash_config['isOpenGyro'])
                    Data="start "+str(rtc.datetime())+";"+str(mpu_data1)+";"+str(mpu_data2)+" end"+'\r\n'
                    Data_Buffer.extend(Data)
                    if len(Data_Buffer) >= 8192:  # Adjust this size as needed
                        data_file.write(Data_Buffer)
                        data_file.flush() # Write the data to the file 
                        Data_Buffer = bytearray()  # Reset the buffer
                        #print("we have detected ",Number_of_data)
                        gc.collect()# release the RAM explictily to prevent memory allociation error 
        if Measurment==False and Created_File==True: # detection end and the saving folder had been created 
            data_file.write(Data_Buffer)
            data_file.flush()
            File_List.append('sd/mpuData/' + Outfile_Name+'.txt')# Update file list 
            Outfile_Name=""
            Created_File=False
            Data_Buffer= bytearray() # Assign a new bytearray for the next task 
            gc.collect()# release the RAM explictily to prevent memory allociation error 
            data_file.write("It is the end of File") # Indicate it is the end of the record 
            data_file.close() # Close the file to prevent the file error 
        
if __name__ == '__main__':
    #init the sd card
    sd = machine.SDCard(slot=1, width=4, freq=40_000_000)
    #reates a software-based implementation of the I2C
    iic = machine.SoftI2C(scl=machine.Pin(17), sda=machine.Pin(16), freq=400000)
    # scl :clock line ;sda:data line ;freq: communication frequency 
    mpu1 = MPU6050(iic, 104)
    mpu2 = MPU6050(iic, 105)
    # iic: The I2C object used to communicate with the MPU6050 sensor.
    # addr: The I2C address of the MPU6050 sensor. 
    # ax1_filter = KALMAN()
    # ay1_filter = KALMAN()
    # az1_filter = KALMAN()
    # gx1_filter = KALMAN()
    # gy1_filter = KALMAN()
    # gz1_filter = KALMAN()
    # ax2_filter = KALMAN()
    # ay2_filter = KALMAN()
    # az2_filter = KALMAN()
    # gx2_filter = KALMAN()
    # gy2_filter = KALMAN()
    # gz2_filter = KALMAN()
    led = machine.Pin(19, machine.Pin.OUT, value=0)
    adc = machine.ADC(machine.Pin(34))
    connect_key = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)
    start_key = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    all_mpu_init()# init the mpu and check is it successful to init
    sdcard_is_ok = sd_card.check(sd)
    print("Finish the prepaation work")
    # Finish all the prepaation work
    # Use WIFI to connect to PC
    # Replace 'your-ssid' and 'your-password' with your WiFi information
    WIFI_id = 'IoT'
    WIFI_Password = 'eduhk+IoT+2018'
    # Replace 'server-ip' with the IP address of the PC server
    server_ip = '172.19.251.201' # My PC ip 
    server_port = 10000  # The port the server is listening on
    # Connect to Wi-Fi
    # Activate the network interface
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Connect to the network if not already connected
    while not wlan.isconnected():
        wlan.active(True)
        wlan.connect(WIFI_id, WIFI_Password)
        # Wait for connection with a timeout
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
        # Check if connected
    if wlan.isconnected():
        print("Connected to WiFi")
    else:
        print("Failed to connect to WiFi")
        
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Create the client socket sucessfully")
    Testified=True
    while Testified:
        try:
            client_socket.connect((server_ip, server_port))
            #print('Connected to server')
            client_socket.send("Hello...I am ESP32 with IMU1 and IMU2")
            #print("message sended .. ")
            Testified=False
        except OSError as e:
            print('Socket connection failed: ', e)
            time.sleep(1)
    # Create a thread for writing,saving and detect in real time  
    _thread.start_new_thread(Detecting_data_from_MPU, (mpu1,mpu2))
    _thread.start_new_thread(Detecting_Data_in_Real_Time, (mpu1,mpu2,client_socket))
    # Command handler of IMU
    Command_listener(client_socket,sd)