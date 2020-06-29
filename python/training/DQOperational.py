import serial
import socket
import numpy as np
import pickle
#qdan cikinca arduino tek basina donecek
SCALE = 5.25
q_table = None
sensibility = 2 / 3  # *** yeni
env_action_space_n = 3  # aksiyon sayımız: ileri-sol,ileri,ileri-sağ
env_obs_space_n = 3  # raycast (observation) sayısı
DISCRETE_OS_SIZE = [10, 10, 10]
env_observation_space_high = np.array([1000, 1000, 1000])  # raycast'lerin maksimum değerleri
env_observation_space_max = np.power(env_observation_space_high, sensibility)  # hassasiyet ayarı
env_observation_space_low = np.array([0] * env_obs_space_n)  # raycast'lerin minimum değerleri
env_observation_space_min = np.power(env_observation_space_low, sensibility)  # hassasiyet ayarı
discrete_os_win_size = (env_observation_space_max - env_observation_space_min) / DISCRETE_OS_SIZE
currState = None
prevState = None
current_data = None

def load_q_table(name='C:/Users/ASLI/Desktop/Self-driving car/Q LEARNING/Q LEARNING PYTHON/MODELS/QLMCOC3S3R1-lr0.01-eps0.0-dsc0.99-40M'):
    global q_table
    if name:
        picklefile = open(f'{name}.pickle', 'rb')
        q_table = pickle.load(picklefile)
        picklefile.close()
    else:
        assert "Name has not been defined!"


def get_discrete_state(_state):
    # if np.max(np.array(_state)) > max(env_observation_space_high):
    #     print("gelen raycast değeri:", np.max(_state))
    # gelen raycast değerlerini gelebilecek minimum değerden çıkarıp parça büyüklüğüne bölerek 10 parçadan hangisine uygun olduğuna bakıyoruz.
    # _discrete_state = (_state - env_observation_space_low) / discrete_os_win_size
    _discrete_state = np.power((_state - env_observation_space_low), sensibility) / discrete_os_win_size
    print("discrete state:", _discrete_state)
    return tuple(_discrete_state.astype(np.int))


def timeToDistance(times):
    global ok
    global distances
    for time in times:
        if time == 0 or time > 11000:
            print("time: ", time)
            distance = 190
        else:
            distance = time/29.1/2
        distances.append(min(distance, 190))
    print("distances:", distances)
    for distance in distances:
        if distance < 7:
            ok += 1
    return get_discrete_state(np.array(distances)*SCALE)


def get_first_state():
    global currState
    while not currState:
        while not model_car.inWaiting:
            pass
        message = (model_car.readline()).decode("utf-8")
        type_of_message = None
        try:
            type_of_message = type(eval(message)) is list
        except:
            print(f"message: {message} \t type: {type_of_message}")
        if type(eval(message)) is list:
            datas = eval(message)
            times = datas[:3]
            currState = timeToDistance(times)
        else:
            print("TypeError in get_states")


def get_states():
    global currState, prevState, negative,exit
    while not model_car.inWaiting:
        pass
    message = (model_car.readline()).decode("utf-8")
    type_of_message = None
    try:
        type_of_message = type(eval(message)) is list
    except:
        print(f"message: {message} \t type: {type_of_message}")
    if type(eval(message)) is list:
        datas = eval(message)
        times = datas[:3]
        for time in times:
            if time < 0 and not negative:
                model_car.write((str(np.argmax(time))).encode("utf-8"))
                negative = True
        if not negative:
            prevState = currState
            currState = timeToDistance(times)
        if datas[3] == 1:
            exit = True
    else:
        print("else", message)

load_q_table()
model_car = serial.Serial("COM9", baudrate=115200, timeout=1)
simulation_car = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creation of UDP server
simulation_car.bind(("127.0.0.1", 4242))  # localhost ve port
model_car.write("P".encode("utf-8"))
okay = True
exit=False
while okay:
    while not model_car.inWaiting():
        pass
    message = (model_car.readline()).decode("utf-8")
    if message == "GOYA is ready!":
        print("Arduino is ready!")
        model_car.write("Q".encode("utf-8"))
    okay = False
print("ITS OKAY")
data, address = simulation_car.recvfrom(1024)
data_eval = eval(data)
for data in data_eval:
    if type(data) == float:
        time = data/45
        model_car.write((str(time)).encode("utf-8"))
        while not model_car.inWaiting:
            pass
    elif data == "sag":
        model_car.write((str(-1)).encode("utf-8"))
        while not model_car.inWaiting:
            pass
    elif data == "sol":
        model_car.write((str(-2)).encode("utf-8"))
        while not model_car.inWaiting:
            pass
    elif data == "q":
        model_car.write((str(-4)).encode("utf-8"))
        get_first_state()
        model_car.write((str(0)).encode("utf-8"))
        while not exit:
            distances = []
            ok = 0
            negative = False
            get_states()
            if exit and not negative:
                model_car.write((str(4)).encode("utf-8"))
            elif not negative:
                if ok == 3:
                    action = np.argmax(distances)
                else:
                    action = np.argmax(q_table[currState])
                if list(q_table[currState]) == [0, 0, 0]:
                    action = np.argmax(currState)
                print(" action: ", action)
                model_car.write((str(action)).encode("utf-8"))
model_car.write((str(-3)).encode("utf-8"))












