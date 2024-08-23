import serial
import threading
import time
import curses

uart = serial.Serial('/dev/ttyAMA0', baudrate=1000000, timeout=1)

current_command = None
command_lock = threading.Lock()
exit_event = threading.Event()

fixed_speed = 250  # 모든 방향에 대해 고정된 최대 속도
key_states = {'w': False, 'a': False, 's': False, 'd': False}

def generate_command():
    L = 0
    R = 0

    # 단일 키에 따른 명령어 설정
    if key_states['w']:
        L, R = fixed_speed, fixed_speed
    elif key_states['s']:
        L, R = -fixed_speed, -fixed_speed
    elif key_states['a']:
        L, R = -fixed_speed, fixed_speed
    elif key_states['d']:
        L, R = fixed_speed, -fixed_speed

    return f'{{"T\":1,\"L\":{L},\"R\":{R}}}'

def execute_command():
    global current_command
    last_command = None
    while not exit_event.is_set():
        with command_lock:
            if current_command != last_command:
                uart.write(current_command.encode())
                last_command = current_command
        time.sleep(0.02)  # 명령 전송 주기를 0.02초로 설정

def input_command(stdscr):
    global current_command
    stdscr.nodelay(True)
    
    while not exit_event.is_set():
        key = stdscr.getch()
        if key != -1:
            if key == ord('w'):
                key_states['w'] = True
                key_states['a'] = False
                key_states['s'] = False
                key_states['d'] = False
            elif key == ord('a'):
                key_states['w'] = False
                key_states['a'] = True
                key_states['s'] = False
                key_states['d'] = False
            elif key == ord('s'):
                key_states['w'] = False
                key_states['a'] = False
                key_states['s'] = True
                key_states['d'] = False
            elif key == ord('d'):
                key_states['w'] = False
                key_states['a'] = False
                key_states['s'] = False
                key_states['d'] = True
        else:
            if key == -1:
                key_states['w'] = False
                key_states['a'] = False
                key_states['s'] = False
                key_states['d'] = False

        with command_lock:
            if any(key_states.values()):
                current_command = generate_command()
            else:
                current_command = "{\"T\":0}"  # stop 명령어
        time.sleep(0.02)  # 입력 처리 주기를 0.02초로 설정

if __name__ == "__main__":
    executor_thread = threading.Thread(target=execute_command)

    executor_thread.start()

    curses.wrapper(input_command)

    exit_event.set()
    executor_thread.join()

    print("Program terminated.")
