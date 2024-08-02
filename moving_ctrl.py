import serial
import threading
import time

uart = serial.Serial('/dev/ttyAMA0', baudrate=1000000, timeout=1)

current_command = None
command_lock = threading.Lock()

exit_event = threading.Event()

def execute_command():
    global current_command
    while not exit_event.is_set():
        with command_lock:
            if current_command:
                uart.write(current_command.encode())
                #print(f"Executing command: {current_command}")
        time.sleep(0.1)

def cmd_parser(cmd_input):
    if cmd_input == 'stop':
        return "{\"T\":0}"
    cmd_sliced = cmd_input.split()
    if cmd_sliced[0] == 'go':
        return "{\"T\":1,\"L\":" + cmd_sliced[1] + ",\"R\":" + cmd_sliced[2] + "}"

def input_command():
    global current_command
    while not  exit_event.is_set():
        command_input = input("Enter command: ")
        print(command_input)
        if command_input.lower() == 'quit':
            exit_event.set()
            break
        command = cmd_parser(command_input)
        print(command)
        with command_lock:
            print("Command sent: ", command_input, "=", command)
            current_command = command

if __name__ == "__main__":
    executor_thread = threading.Thread(target=execute_command)
    input_thread = threading.Thread(target=input_command)

    executor_thread.start()
    input_thread.start()

    executor_thread.join()
    input_thread.join()

    print("Program terminated.")
