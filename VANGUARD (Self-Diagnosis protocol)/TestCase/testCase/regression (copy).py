import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from plotting import BPS_Feedback_TestCase
BPS_Feedback = BPS_Feedback_TestCase().data
x, y = zip(*BPS_Feedback)
x_ = list(x)
train_x = np.array(list(x))
train_y = np.array(list(y))

current = os.getcwd()

p = PolynomialFeatures(degree=15).fit(train_x,traion_y)
print(p.get_feature_names(data.columns))

features = DataFrame(p.transform(data), columns=p.get_feature_names(data.columns))
print(features)

'''
regression data가 만들때마다 시간이 오래걸려서 txt 파일로 받아두려고 있는 코드 (regression.txt 파일이 있으면 돌릴 필요 없음)
f = open(f"{current}/regression.txt", 'w')
for i in range(len(polyfit)):
    data = f"{x_[i]},{polyfit[i][0]}\n"
    f.write(data)
f.close()
'''

