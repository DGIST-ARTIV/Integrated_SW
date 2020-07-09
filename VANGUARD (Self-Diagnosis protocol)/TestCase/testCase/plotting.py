import matplotlib.pyplot as plt
import os

""" 브레이크와 액셀의 txt파일 모두 한 줄에 시간, ACT_Feed, Feed 순으로 3가지 데이터를 담고 있다. """

def get_subdir(path): # 해당 디렉토리에서 sub 디렉토리만을 찾아서 리스트로 반환하는 함수
    content_list = os.listdir(path)
    subdir_list = []
    for content in content_list:
            fullname = os.path.join(path, content)                
            if os.path.isdir(fullname):
                    subdir_list.append(fullname)
    return subdir_list

def get_file(path,file_format="all"): # 해당 디렉토리에서 특정 포맷의 파일만 찾아서 리스트로 반환하는 함수    
    file_list = os.listdir(path)
    if file_format != "all":
        format_file_list = [file for file in file_list if file.endswith(file_format)]

    else:
        format_file_list = file_list

    for i in range(len(format_file_list)):
        format_file_list[i] = os.path.join(path, format_file_list[i])           
    return format_file_list

def all_files(file_format="all"): #사용할 모든 파일 이름을 리스트로 반환하는 함수 
    current = os.getcwd()
    sub_list = get_subdir(current)
    all_files = []
    for subdir in sub_list:
        all_files += get_file(subdir,file_format)
    return all_files  
def data_separation(file_list): # txt 파일의 data를 key가 시간이고 value가 각각 ACT_Feed와 Feed인 2개의 dictionary로 분리하는 함수
    dict1 = dict()
    dict2 = dict()
    for i in range(len(file_list)):
        f = open(f"{file_list[i]}", 'r')
        lines = f.readlines()        
        for line in lines:
            temp = line.split(',')
            dict1[float(temp[0])] = float(temp[1])
            dict2[float(temp[0])] = float(temp[2])
        f.close()
    dict1 = sorted(dict1.items())
    dict2 = sorted(dict2.items())
    return dict1, dict2

def plotting(dic,color,name): # topic 별로 분리되어있는 dictionary를 받아와서 원하는 형태로 plotting 해주는 함수
    x, y = zip(*dic)
    plt.figure()
    plt.scatter(x,y,color=color)
    plt.title(name + " TestCase",fontsize=25)
    plt.xlabel("Test Time",fontsize=25)
    plt.ylabel(name,fontsize=25)
    plt.show()

def get_BPS_Feedback():
    f_list = all_files()
    brake_file_list = []    
    for f in f_list:
        if 'brake' in f:
            brake_file_list.append(f)

    BPS_ACT_Feedback, BPS_Feedback = data_separation(brake_file_list)
    return BPS_Feedback

class BPS_Feedback_TestCase():

    def __init__(self):
        self.data = get_BPS_Feedback()

if __name__ == "__main__":
    f_list = all_files()
    
    accel_file_list = []
    brake_file_list = []    
    for f in f_list:
        if 'accel' in f:
            accel_file_list.append(f)
        elif 'brake' in f:
            brake_file_list.append(f)   

    APS_ACT_Feedback, APS_Feedback = data_separation(accel_file_list)
    BPS_ACT_Feedback, BPS_Feedback = data_separation(brake_file_list)
    
    print("<Plotting TestCase of VANGUARD>")
    print("1: APS_ACT_Feedback ")
    print("2: BPS_ACT_Feedback ")
    print("3: APS_Feedback ")
    print("4: BPS_Feedback ")
    user_choice = input("Enter the number you want: ")
    if user_choice == "1":
        plotting(APS_ACT_Feedback, 'chartreuse', 'APS_ACT_Feedback')
    elif user_choice == "2":
        plotting(BPS_ACT_Feedback, 'deeppink', 'BPS_ACT_Feedback')
    elif user_choice == "3":
        plotting(APS_Feedback, 'blue', 'APS_Feedback')
    elif user_choice == "4":
        plotting(BPS_Feedback, 'darkorange', 'BPS_Feedback')



