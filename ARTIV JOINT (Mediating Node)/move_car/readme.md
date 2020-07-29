# 간단한 매뉴얼

__<structure of move_car for Ioniq>__
[car_type = 0.0(Ioniq), mode, speed, accel, brake, steer, gear, angular(Ioniq), status(ERP42), estop(ERP42)]

사용법 : mode를 통한 차량 제어


## 설명

move_car는 0번째 값으로 차량의 종류를 선택하여 move_Ioniq 또는 move_ERP42 노드를 키고, 지속적으로 move_car topic을 받아와서 차량을 제어한다.

그에 따라, 개발자의 편의를 위해 dbw_ioniq노드를 sub하여 callback 변수로 저장해두고, 현재 속도 및 move_car topic도 callback으로 받아온다. 개발자의 편의에 따라 사용하면 된다.

또한, 현재 차량의 종류, 현재 모드, 현재 실제 속도를 /move_car_info topic을 통해 pub하므로, 편의에 맞게 사용하면 되겠다.

아래 링크에 자세한 매뉴얼이 있다. 꼭 정독해보자. 또 물어보거나 뭐 새로 만들어달라하면 죽일거다. ~~#이승기~~

[move_Ioniq 매뉴얼](https://docs.google.com/document/d/1AxAMeq6Xrgb8W50JrqpNWJELcRYVBZaxbXu9biplyvI/edit?usp=sharing)
