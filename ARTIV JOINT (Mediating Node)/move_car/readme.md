# 간단한 매뉴얼

__<structure of move_car for Ioniq>__
[car_type = 0.0(Ioniq), mode, speed, accel, brake, steer, gear, angular(Ioniq), status(ERP42), estop(ERP42)]

사용법 : mode를 통한 차량 제어

mode 0.0 : E-Stop (사용예시 : [0.0, 0.0, None, 2000.0])
브레이크 값 넣는 만큼 계속 밟음

mode 1.0 : Cruise Control (사용예시 : [0.0, 1.0, 30.0])
원하는 속도를 입력하면 해당 속도로 curise control 진행

mode 2.0 : Cruise Control with Steering (사용예시 : [0.0, 2.0, 30.0, None, None, 200.0, None, 200.0])
원하는 속도를 입력하면 해당 속도로 cruise control을 진행하고 steering도 가능

mode 3.0 : Develper Mode (사용예시 : [0.0, 3.0, None, accel값, brake값, steer값, gear값, angular값])
move_car는 기존의 dbw_cmd 노드를 대체하되, 기능적인 부분을 편하게 만들어주는 노드로써, 일단 기존에 사용가능했던 raw값 publisher도 내장되어 있음

## 설명

move_car는 0번째 값으로 차량의 종류를 선택하여 move_Ioniq 또는 move_ERP42 노드를 키고, 지속적으로 move_car topic을 받아와서 차량을 제어한다.

그에 따라, 개발자의 편의를 위해 dbw_ioniq노드를 sub하여 callback 변수로 저장해두고, 현재 속도 및 move_car topic도 callback으로 받아온다. 개발자의 편의에 따라 사용하면 된다.

또한, 현재 차량의 종류, 현재 모드, 현재 실제 속도를 /move_car_info topic을 통해 pub하므로, 편의에 맞게 사용하면 되겠다.
