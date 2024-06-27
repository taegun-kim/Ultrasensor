import serial
import RPi.GPIO as GPIO
import time
import os
import threading

# 핀 번호
TRIG_PIN = 16   
ECHO_PIN = 20   
PIR_PIN = 19    
LED_PIN = 13

# 블루투스 시리얼 통신
BlSerial = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1.0)

# 핀 초기화
def Setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.setup(PIR_PIN, GPIO.IN)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, False)

## 수업시간에 활용한 거리 계산 코드 활용 (오픈소스)
def get_Distance():
    GPIO.output(TRIG_PIN, False)

    #Trigger 파동 활성화
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    # 거리 측정
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    
    if distance <= 2 or distance >= 400: # 이상값 나올시 -1로 반환
        distance = -1
        
    try:
        BlSerial.write(str(distance).encode()) # 블루투스 송신
    except serial.SerialException as e:
        print(f"Failed to write to serial device: {e}")  

def get_pir():
    # 장애물 감지 센싱 결과 받음
    detect = GPIO.input(PIR_PIN)
        
    if detect:
        GPIO.output(LED_PIN, False) # 비감지시 LED OFF
    else:
        GPIO.output(LED_PIN, True) # 비감지시 LED ON
                        
def activateCamera():
    print("Activating camera...")
    os.system("sudo motion -b") # os에서 백그라운드로 motion 소프트웨어 실행

def bluetoothServer():
    
    try:
        Setup() # 초기화 함수
        
        # 백그라운드에서 Motion 소프트웨어 실행 (스레드)
        camera_thread = threading.Thread(target=activateCamera)
        camera_thread.daemon = True
        camera_thread.start()

        # 거리 및 감지 센싱
        while True:
            get_Distance()
            get_pir()
            time.sleep(1)


    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        GPIO.cleanup()
        BlSerial.close()

if __name__ == "__main__":
    bluetoothServer()

