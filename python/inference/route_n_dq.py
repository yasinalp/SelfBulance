import serial
import socket

car_speed = 45  # cm/s

model_car = serial.Serial("COM28", baudrate=9600, timeout=1)
simulation_car = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creation of UDP server
simulation_car.bind(("127.0.0.1", 4242))  # localhost ve port

okay = True
while okay:
    while not model_car.inWaiting():
        pass
    message = (model_car.readline())
    print(f"message in bytes: {message}")
    for char in message:
        print(f"char: {char}")
    print(f"encoded message: {message.decode('ascii')}")
    if message[:-2] == "0":
        print("Model car is ready!")
    model_car.write("Q".encode("ascii"))
    okay = False

data, address = simulation_car.recvfrom(1024)
data_eval = eval(data)
print(f"data: {data}")
print(f"data eval: {data_eval}")
type_of_data = type(data_eval)
for _data in data_eval:
    if type(_data) == float or type(_data) == int:
        time = int(_data * 1000 / car_speed)  # in milliseconds
        print(f"time: {time}")
        model_car.write((str(time)+'\r').encode("ascii"))
        while not model_car.inWaiting:
            pass
        response = (model_car.readline()).decode("ascii")
        print(f"response: {response}")
    elif _data == "sol":
        model_car.write((str(-1)+'\r').encode("ascii"))
        while not model_car.inWaiting:
            pass
        response = (model_car.readline()).decode("ascii")
        print(f"response: {response}")
    elif _data == "sag":
        model_car.write((str(-2)+'\r').encode("ascii"))
        while not model_car.inWaiting:
            pass
        response = (model_car.readline()).decode("ascii")
        print(f"response: {response}")

model_car.write((str(-3)).encode("ascii"))
