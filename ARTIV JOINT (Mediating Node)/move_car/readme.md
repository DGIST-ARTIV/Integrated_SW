# 간단한 매뉴얼

__<structure of move_car for Ioniq>__
[car_type = 0.0(Ioniq), mode, speed, accel, brake, steer, gear, angular(Ioniq), status(ERP42), estop(ERP42)]

__<structure of move_car for ERP42>__
[car_type = 1.0(ERP42), mode, speed, accel, brake, steer, gear, angular(Ioniq), status(ERP42), estop(ERP42)]

사용법 : mode를 통한 차량 제어

## ros2 launch file link

[move_Ioniq](./move_Ioniq)

[move_ERP42](https://github.com/DGIST-ARTIV/Integrated_SW/releases/tag/move_ERP42-1.0.2)

## 설명

0번째 값 : 0.0 or 1.0 >> 차량의 종류를 선택

1번째 값 : mode 선택

2번째 값 : cruise control일 때, 속도 선택 (km/h)

3번째 ~ 9번째 값 : cmd 노드를 통해 직접 넣을 수 있었던 여타 값들

##

### $ 주의 사항 $

msg를 Float32MultiArray를 사용하므로, 사용하지 않는 값이더라도 0.0과 같은 쓰레기값을 채우고, 마지막 인덱스까지 다 쓰레깃값으로 채울 것!

예시 : Ioniq을 속도 20km/h로 cruise control하고 핸들은 운전자가 제어하는 상황

__MCmsg.data = [0.0,1.0,20.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]__

자세한 사항은 아래 매뉴얼을 참고!

[move_Ioniq 매뉴얼](https://docs.google.com/document/d/1AxAMeq6Xrgb8W50JrqpNWJELcRYVBZaxbXu9biplyvI/edit?usp=sharing)

[move_ERP42 매뉴얼](https://artiv.gitbook.io/artiv-move-car/)
