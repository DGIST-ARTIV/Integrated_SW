import os
from plotting import BPS_Feedback_TestCase

BPS_Feedback = BPS_Feedback_TestCase().data

def get_regression():
    current = os.getcwd()
    dict1 = dict()
    f = open(f"{current}/regression.txt", 'r')
    lines = f.readlines()
    for line in lines:
        temp = line.split(',')
        dict1[float(temp[0])] = float(temp[1])
    f.close()
    #dict1 = sorted(dict1.items())
    return dict1

class Regression():

    def __init__(self):
        self.data = get_regression()

def BPS_Feedback_dict():
    x, y = zip(*BPS_Feedback)
    x = list(x)
    y = list(y)
    dic = dict()
    for i in range(len(x)):
        dic[x[i]] = y[i]
    return dic

def maximum():
    regression_dic = get_regression()
    BPS_Feedback_dic = BPS_Feedback_dict()

if __name__ == "__main__":
    print(len(get_regression()))
    print(len(BPS_Feedback))

