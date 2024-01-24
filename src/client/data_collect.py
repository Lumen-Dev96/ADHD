import socket
import threading
import time  # Needed for the timed broadcast
from datetime import datetime
import re
import pandas as pd
nickname=""
# List to keep track of client connections
clients = []
# Lock to ensure thread-safe operations on the clients list
clients_lock = threading.Lock()
Special_Command=""
# Server configuration
server_ip = '0.0.0.0'  # Listen on all network interfaces
server_port = 10000
Recieved_Data_in_Real_Time=[]
Buffer_of_IMU1=[]
Buffer_of_IMU2=[]
Running_IMU=None
Name_of_Handling_File=""
# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and start listening for incoming connections
server_socket.bind((server_ip, server_port))
server_socket.listen()

print('Server listening on port', server_port)

def broadcast(command):
    """ Send a command to all connected clients. """
    with clients_lock:  # Acquire lock to ensure list is not modified while iterating
        for client in clients:
            try:
                client.send(command.encode('utf-8'))  # Send the command to each client
            except socket.error as e:  # Handle potential socket errors
                print(f'Error sending to client: {e}')

def client_thread(client_socket, client_address):
    global Buffer_of_IMU2
    global Buffer_of_IMU1
    """ Handle communication with a connected client. """
    print(f'New connection from {client_address}') # used to check the connection is created or not
    # Add the new client to the clients list in a thread-safe manner
    with clients_lock:
        clients.append(client_socket)
    try:
        while True:  # Continuously receive data from the client
            imu_data = client_socket.recv(16400).decode('utf-8')
            if not imu_data :  # If no data is received, it means the client has disconnected
                break
            if "Get_Content_from" in Special_Command: #
                if Running_IMU =="IMU2":
                    if "It is the end of File" in imu_data:
                        Buffer_of_IMU2.append(imu_data)
                        print(imu_data)
                        Convert_Recieved_Data_to_Text_file(List_of_Collected_Data=Buffer_of_IMU2,File_Name=Name_of_Handling_File)
                        Buffer_of_IMU2=[]
                        print("End of Csv Conversion ")
                    else:
                        Buffer_of_IMU2.append(imu_data)
                        print(imu_data)
                if Running_IMU=="IMU1":
                    if "It is the end of File" in imu_data:
                        Buffer_of_IMU1.append(imu_data)
                        print(imu_data)
                        Convert_Recieved_Data_to_Text_file(List_of_Collected_Data=Buffer_of_IMU1,File_Name=Name_of_Handling_File)
                        Buffer_of_IMU1=[]
                        print("End of Csv Conversion ")
                    else:
                        Buffer_of_IMU1.append(imu_data)
                        print(imu_data)
            elif Special_Command == "Real_Time_Detection":#
                if "IMU2" in imu_data:
                    Buffer_of_IMU2.append(imu_data)
                elif "IMU1" in imu_data:
                    Buffer_of_IMU1.append(imu_data)
            else:
                print(imu_data)
            # Here you could call broadcast() if needed

    except socket.error as e:  # Handle any exceptions that occur within the thread
        print(f'Error with client {client_address}: {e}')
    finally:
        # When the client disconnects, remove it from the clients list and close the socket
        with clients_lock:
            clients.remove(client_socket)
        client_socket.close()
        print(f'Connection with {client_address} closed')

def broadcast_thread():
    global Special_Command
    global Name_of_Handling_File
    global Running_IMU
    global Buffer_of_IMU1
    global Buffer_of_IMU2
    """ Thread function for broadcasting commands at regular intervals. """
    while True:
        # Send a command to all clients
        message = '{}: {}'.format(nickname, input('Input the command for IMU:'))# input the command from the console
        if "Update_Local_Time_as" in message: # add the timestamp from the PC and
            message=nickname+":"+"Update_Local_Time_as"+ datetime.now().strftime("%Y-%m-%d-1-%H-%M-%S-%f")[:-3]
        elif "sd/mpuData/" in message:
            Name_of_Handling_File=message.split("/")[-1]
            Name_of_Handling_File=Name_of_Handling_File.replace(".txt",".csv")
            Running_IMU=Name_of_Handling_File.split("_")[0]
            Special_Command="Get_Content_from_"+Running_IMU
        elif "Real_time_Detection_and_Save_as" in message:
            Special_Command = "Real_Time_Detection"
        elif "stop" in message:
            if len(Buffer_of_IMU1)>0 and len(Buffer_of_IMU2)>0:
                print(len(Buffer_of_IMU1),len(Buffer_of_IMU2))
                Special_Command = ""
                Name_of_Handling_File = ""
                Running_IMU = None
        else:
            Special_Command = ""
            Name_of_Handling_File=""
            Running_IMU=None
        broadcast(message)
        #print("Special command",Special_Command,Running_IMU,Name_of_Handling_File)
        #time.sleep(5)  # Wait for 5 seconds before sending the next command


def Convert_Recieved_Data_to_Text_file(List_of_Collected_Data ,File_Name=None): # pass
    Time_Stamp=[]
    Accel_X_of_detector_1  = []
    Accel_Y_of_detector_1 = []
    Accel_Z_of_detector_1  = []
    Accel_X_of_detector_2 = []
    Accel_Y_of_detector_2  = []
    Accel_Z_of_detector_2  = []
    Number_of_Recieved_Data=0
    #print("Start of conversion to csv file ....")
    for data in range(len(List_of_Collected_Data)):
        #print(List_of_Collected_Data[data])
        # Use regex to find all data between 'start ' and ' end'
        matches = re.findall(r'start (.*?) end', List_of_Collected_Data[data], re.DOTALL)
        # Print all matches
        for match in matches:
            #print(match)
            Data_l=match.split(";")
            Time_Data=Data_l[0]
            Mpu_Data_1=Data_l[1]
            Mpu_Data_2 = Data_l[2]
            #print(match,Time_Data,Mpu_Data_1,Mpu_Data_2)
            TL=Time_Data.split(",") # the list which store the time stamp
            Year=str(int(TL[0].replace("(","")))
            Month = str(int(TL[1].replace(" ", "")))
            Day = str(int(TL[2].replace(" ", "")))
            Hour = str(int(TL[4].replace(" ", "")))
            Min = str(int(TL[5].replace(" ", "")))
            Second = str(int(TL[6].replace(" ", "")))
            Micro_Second = str(int(TL[7].replace(")", "").replace(" ","")))
            Mpu_Data_1=Mpu_Data_1.replace("{","")
            Mpu_Data_1 = Mpu_Data_1.replace("}", "")
            Mpu_Data_2 = Mpu_Data_2.replace("{", "")
            Mpu_Data_2 = Mpu_Data_2.replace("}", "")
            Mpu_d1=Mpu_Data_1.split(":")
            Mpu_d2=Mpu_Data_2.split(":")
            #print(TL, Mpu_d1,len(Mpu_d1), Mpu_d2,len(Mpu_d2))
            time_stamp=Year+":"+Month+":"+Day+":"+Hour+":"+Min+":"+Second+":"+Micro_Second
            accel_y_dector_1=float(Mpu_d1[1].split(",")[0])
            accel_y_dector_2 = float(Mpu_d2[1].split(",")[0])
            #print(accel_y_dector_1)
            accel_x_dector_1 = float(Mpu_d1[2].split(",")[0])
            accel_x_dector_2 = float(Mpu_d2[2].split(",")[0])
            accel_z_dector_1 = Mpu_d1[3].split(",")[0]
            accel_z_dector_2 = Mpu_d2[3].split(",")[0]
            #print(accel_z_dector_1)
            Accel_Y_of_detector_1.append(accel_y_dector_1)
            Accel_X_of_detector_1.append(accel_x_dector_1)
            Accel_Z_of_detector_1.append(accel_z_dector_1)
            Accel_Y_of_detector_2.append(accel_y_dector_2)
            Accel_Z_of_detector_2.append(accel_z_dector_2)
            Accel_X_of_detector_2.append(accel_x_dector_2)
            Time_Stamp.append(time_stamp)
            Number_of_Recieved_Data=Number_of_Recieved_Data+1
    #print("We have handle ...",Number_of_Recieved_Data," data")
    IMU_Detected_Data = pd.DataFrame()
    IMU_Detected_Data['Time_Stamp'] = Time_Stamp
    IMU_Detected_Data['Accel_X_of_Detector1'] = Accel_X_of_detector_1
    IMU_Detected_Data['Accel_Y_of_Detector1'] = Accel_Y_of_detector_1
    IMU_Detected_Data['Accel_Z_of_Detector1'] = Accel_Z_of_detector_1
    IMU_Detected_Data['Accel_X_of_Detector2'] = Accel_X_of_detector_2
    IMU_Detected_Data['Accel_Y_of_Detector2'] = Accel_Y_of_detector_2
    IMU_Detected_Data['Accel_Z_of_Detector2'] = Accel_Z_of_detector_2
    IMU_Detected_Data.to_csv(File_Name, index=False)
    return




# Main server loop

try:
    # Start the broadcasting thread
    nickname = input("Input the message for checking the Boardcasting Thread :") # Check the bocardcasting on or not
    write_thread = threading.Thread(target=broadcast_thread)
    write_thread.start()

    while True:
        # Accept new connections from clients
        client_sock, client_addr = server_socket.accept()
        # Start a new thread for each connected client
        threading.Thread(target=client_thread, args=(client_sock, client_addr)).start()

except KeyboardInterrupt:  # Allow the server to be stopped with Ctrl+C
    print('Server is shutting down')
finally:
    # Close the server socket and all client sockets before exiting
    server_socket.close()
    with clients_lock:
        for client in clients:
            client.close()
    print('Closed all client connections')

"""""
#The IMU's command
Command_List={
    "stop" : 'IMU will Stop all the measurement',
    "listdirectory": 'List all the file within the SD card',
     "invalid commnad":"Recieve some invalid command ",
     "Detect_And_Save_as":'Save all the detection to the given file',
     "Update_Local_Time_as":"Reset the time stamp of the IMU..",
     "Check_IMU_Time":"Check the clock reading of the IMU...",
     "Real_time_Detection_and_Save_as":"Save all the detection to the given file and send it in real time",
}
"""""