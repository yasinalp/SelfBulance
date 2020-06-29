
import time
import datetime
import tensorflow as tf
from keras.callbacks import TensorBoard
import keras.backend as K
import numpy as np
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense, Input, Dropout
from keras.optimizers import Adam, SGD
import socket
import random
import collections
import inspect

#import matplotlib.pyplot as plt

last_episode = 0
last_step = 0  # 100_000_000
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creation of UDP server
server.bind(("127.0.0.1", 4242))  # localhost ve port
address_list = []  # godot client's address
state_list = []  # states of each car
action_list = []  # last action told to each car
replay_list = []
# D_OS_RES = 15  # DISCRETE_OS_RESOLUTION
env_action_space_n = 3  # actions' number (right, left, straight)
env_obs_space_n = 3  # ray cast number
reward = 0
done = 0  # controls if episode finished
episode = 0
EPISODES = 10_000  # 5000
SAVE_EVERY = EPISODES / 20
REPLAY_MEMORY_SIZE = 10_000  # How many last steps to keep for model training
MIN_REPLAY_MEMORY_SIZE = 32  # Minimum number of steps in a memory to start training
MINIBATCH_SIZE = 32  # How many steps (samples) to use for training
AGGREGATE_STATS_EVERY = 50
UPDATE_TARGET_EVERY = 10000  # 50
ep_scores = collections.deque(maxlen=100)
# [ep_scores.append(0) for i in range(500)]
render = True
runtimestamp = datetime.datetime.now().strftime('%m-%d-%Y-%H%M%S')
z = []

model_name0 = "model0final1-nobias-8neurons"
model_name1 = "model1final1-nobias-8neurons"
model_name2 = "model2final1-nobias-8neurons"
load_name0 = ""  # "s3a3gi95arc61218126Adam-10M"
load_name1 = ""
load_name2 = ""
min_rewards = collections.deque(maxlen=1000)
max_rewards = collections.deque(maxlen=1000)
average_rewards = collections.deque(maxlen=1000)


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = 1
        self.replay_memory0 = collections.deque(maxlen=32)
        self.replay_memory1 = collections.deque(maxlen=32)
        self.replay_memory2 = collections.deque(maxlen=32)
        self.gamma = 0.99  # discount rate
        self.gamma_rise = 1.00001
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.0
        self.epsilon_decay = 0.00001
        self.learning_rate = 0.001
        self.model1 = self._build_model1()
        if load_name1:
            self.model1 = load_model(f"models/dq/{load_name1}.h5py")
            print(f"model {load_name1} loaded!")
        # Target network
        self.target_model1 = self._build_model1()
        self.target_model1.set_weights(self.model1.get_weights())
        self.target_update_counter1 = 0

        self.model_name1 = 'model1'
        self.model_variables1 = f"{self.model_name1}-lr{self.learning_rate}-eps{self.epsilon}-dsc{self.epsilon_decay}"
        self.model2 = self._build_model2()
        if load_name2:
            self.model2 = load_model(f"models/dq/{load_name2}.h5py")
            print(f"model {load_name2} loaded!")
        # Target network
        self.target_model2 = self._build_model2()
        self.target_model2.set_weights(self.model2.get_weights())
        self.target_update_counter2 = 0

        self.model_name2 = 'model2'
        self.model_variables2 = f"{self.model_name2}-lr{self.learning_rate}-eps{self.epsilon}-dsc{self.epsilon_decay}"
        self.model0 = self._build_model0()
        if load_name0:
            self.model0 = load_model(f"models/dq/{load_name0}.h5py")
            print(f"model {load_name0} loaded!")
        # Target network
        self.target_model0 = self._build_model0()
        self.target_model0.set_weights(self.model0.get_weights())
        self.target_update_counter0 = 0
        self.model_name0 = 'model3'
        self.model_variables0 = f"{self.model_name0}-lr{self.learning_rate}-eps{self.epsilon}-dsc{self.epsilon_decay}"


    def _build_model1(self):
        # Neural Net for Deep-Q learning Model
        model1 = Sequential()
        model1.add(Dense(8, use_bias=False, input_dim=self.state_size, activation='linear'))
        model1.add(Dense(self.action_size, activation='linear'))
        model1.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model1

    def _build_model2(self):
        # Neural Net for Deep-Q learning Model
        model2 = Sequential()
        model2.add(Dense(8, use_bias=False,  input_dim=self.state_size, activation='linear'))
        model2.add(Dense(self.action_size, activation='linear'))
        model2.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model2

    def _build_model0(self):
        # Neural Net for Deep-Q learning Model
        model0 = Sequential()
        model0.add(Dense(8, use_bias=False, input_dim=self.state_size, activation='linear'))
        model0.add(Dense(self.action_size, activation='linear'))
        model0.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model0

    def remember(self, state, action, reward, next_state, done):
        if action == 0:
            self.replay_memory0.append((state, action, reward, next_state, done))
        elif action == 1:
            self.replay_memory1.append((state, action, reward, next_state, done))
        elif action == 2:
            self.replay_memory2.append((state, action, reward, next_state, done))

    def get_qs(self, state):
        if np.random.rand() <= self.epsilon:
            act = random.randrange(self.action_size)
            # print("act: ", act)
            return act
        act_values0 = self.model0.predict(state)
        act_values1 = self.model1.predict(state)
        act_values2 = self.model2.predict(state)
        lines = inspect.getsource(self.model2.predict)
        #print(lines)
        act_values = []
        act_values.append(act_values0[0])
        act_values.append(act_values1[0])
        act_values.append(act_values2[0])
        # print(f"state: {state} acts: {act_values}")
        return np.argmax(np.array(act_values))  # returns action

    def train1(self, terminal_state):
        global z
        if len(self.replay_memory1) < MIN_REPLAY_MEMORY_SIZE:
            print("haydaa1!!")
            print(len(self.replay_memory1))
            return
            # Get a minibatch of random samples from memory replay table
        minibatch = random.sample(self.replay_memory1, MINIBATCH_SIZE)

        # Get current states from minibatch, then query NN model for Q values
        current_states = np.array([transition[0][0] for transition in minibatch])
        current_qs_list = self.model1.predict(current_states)
        new_current_states = np.array([transition[3][0] for transition in minibatch])
        # print("new_current states: ", new_current_states)
        # print("n_c_s_shape: ", new_current_states.shape)
        future_qs_list = self.target_model1.predict(new_current_states)
            # print(f"next qs: ", future_qs_list)

        X = []
        y = []
        z = []  # action değerlerini tutabilmek için

            # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + self.gamma * max_future_q

            else:

                new_q = reward #+ self.gamma * np.max(current_qs_list[index])

                # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[0] = new_q

            # And append to our training data
            X.append(current_state)
            y.append(current_qs)
            z.append(action)

        # Fit on all samples as one batch, log only on terminal state
        self.model1.fit(np.array(X).reshape((-1, self.state_size)), np.array(y), batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False )

        # Update target network counter every episode
        if terminal_state:
            self.target_update_counter1 += 1

            # If counter reaches set value, update target network with weights of main network
        if self.target_update_counter1 > UPDATE_TARGET_EVERY:
                # print("Target Updated")
            self.target_model1.set_weights(self.model1.get_weights())
            self.target_update_counter1 = 0

    def train2(self, terminal_state):
        global z
        if len(self.replay_memory2) < MIN_REPLAY_MEMORY_SIZE:
            print("haydaa2!!")
            print(len(self.replay_memory2))
            return
            # Get a minibatch of random samples from memory replay table
        minibatch = random.sample(self.replay_memory2, MINIBATCH_SIZE)

            # Get current states from minibatch, then query NN model for Q values
        current_states = np.array([transition[0][0] for transition in minibatch])
        current_qs_list = self.model2.predict(current_states)
        new_current_states = np.array([transition[3][0] for transition in minibatch])
        # print("new_current states: ", new_current_states)
        # print("n_c_s_shape: ", new_current_states.shape)
        future_qs_list = self.target_model2.predict(new_current_states)
            # print(f"next qs: ", future_qs_list)

        X = []
        y = []
        z = []  # action değerlerini tutabilmek için

            # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + self.gamma * max_future_q

            else:

                new_q = reward #+ self.gamma * np.max(current_qs_list[index])

                # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[0] = new_q

            # And append to our training data
            X.append(current_state)
            y.append(current_qs)
            z.append(action)

        # Fit on all samples as one batch, log only on terminal state
        self.model2.fit(np.array(X).reshape((-1, self.state_size)), np.array(y), batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False )

        # Update target network counter every episode
        if terminal_state:
            self.target_update_counter2 += 1

            # If counter reaches set value, update target network with weights of main network
        if self.target_update_counter2 > UPDATE_TARGET_EVERY:
                # print("Target Updated")
            self.target_model2.set_weights(self.model2.get_weights())
            self.target_update_counter2 = 0

    def train0(self, terminal_state):
        global z
        if len(self.replay_memory0) < MIN_REPLAY_MEMORY_SIZE:
            print("haydaa0!!")
            print(len(self.replay_memory0))
            return
            # Get a minibatch of random samples from memory replay table
        minibatch = random.sample(self.replay_memory0, MINIBATCH_SIZE)

            # Get current states from minibatch, then query NN model for Q values
        current_states = np.array([transition[0][0] for transition in minibatch])
        current_qs_list = self.model0.predict(current_states)
        new_current_states = np.array([transition[3][0] for transition in minibatch])
        # print("new_current states: ", new_current_states)
        # print("n_c_s_shape: ", new_current_states.shape)
        future_qs_list = self.target_model0.predict(new_current_states)
            # print(f"next qs: ", future_qs_list)

        X = []
        y = []
        z = []  # action değerlerini tutabilmek için

            # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + self.gamma * max_future_q

            else:

                new_q = reward #+ self.gamma * np.max(current_qs_list[index])

                # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[0] = new_q

            # And append to our training data
            X.append(current_state)
            y.append(current_qs)
            z.append(action)

        # Fit on all samples as one batch, log only on terminal state
        self.model0.fit(np.array(X).reshape((-1, self.state_size)), np.array(y), batch_size=MINIBATCH_SIZE, verbose=0, shuffle=False )

        # Update target network counter every episode
        if terminal_state:
            self.target_update_counter0 += 1

            # If counter reaches set value, update target network with weights of main network
        if self.target_update_counter0 > UPDATE_TARGET_EVERY:
                # print("Target Updated")
            self.target_model0.set_weights(self.model0.get_weights())
            self.target_update_counter0 = 0


step_total = 0  # tells how much time the q values change
agent = DQNAgent(env_obs_space_n, env_action_space_n)  # initialization of agent
while True:  # game plays here
    data, address = server.recvfrom(1024)
    data_eval = eval(data)
    type_of_data = type(data_eval)
    if address not in address_list:
        print(f"address {address} is not in the list, will be added")
        address_list.append(address)
        state_list.append(None)
        action_list.append(None)
    address_index = address_list.index(address)
    if type_of_data is list:
        if data_eval[0] == 0:  # observation configs
            server.sendto(bytes("99", "utf-8"), address)  # send action to Godot
        else:
            if len(data_eval) > 4:
                print("data_eval: ", data_eval)
            header, next_state, reward, done = data_eval
            if next_state:
                if action_list[address_index] is not None and state_list[address_index] is not None:
                    next_state = np.reshape(next_state, [1, agent.state_size])  # quantization of ray cast value
                    # print(f"done : {done} bool: {bool(done)}")
                    if not done:
                        agent.remember(state_list[address_index], action_list[address_index], reward, next_state, done)
                        state_list[address_index] = next_state
                        action = agent.get_qs(np.reshape(next_state, [1, agent.state_size]))
                        # print(f"action is {action}")
                        action_list[address_index] = action
                        server.sendto(bytes(f"{action + 1}", "utf-8"), address)  # send action to godot
                        if not step_total % MIN_REPLAY_MEMORY_SIZE and step_total > MIN_REPLAY_MEMORY_SIZE:
                            if action_list[address_index] == 0:
                                agent.train0(done)
                            elif action_list[address_index] == 1:
                                agent.train1(done)
                            elif action_list[address_index] == 2:
                                agent.train2(done)

                    else:
                        # print(f"done : {done}")
                        # time.sleep(0.5)
                        # if an episode ends, there must not be any relation between starting point and collision point
                        # state_list[address_index] = None
                        # action_list[address_index] = None
                        agent.remember(state_list[address_index], action_list[address_index], reward, next_state, done)
                        if action_list[address_index] == 0:
                            agent.train0(done)
                        elif action_list[address_index] == 1:
                            agent.train1(done)
                        elif action_list[address_index] == 2:
                            agent.train2(done)
                        episode += 1
                        #agent.tensorboard.step = episode
                        #ep_scores.append(header)
                        state_list[address_index] = None
                        action_list[address_index] = None
                        #average_score = (sum(ep_scores) / len(ep_scores))
                        #min_score = min(ep_scores)
                        #max_score = max(ep_scores)
                        #agent.tensorboard.update_stats(reward_avg=average_score, reward_min=min_score, reward_max=max_score, epsilon=agent.epsilon, gamma=agent.gamma)
                        # average_rewards.append(sum(ep_scores) / len(ep_scores))
                        # min_rewards.append(min(ep_scores))
                        # max_rewards.append(max(ep_scores))
                        # print(f"{len(max_rewards)}max_rewards: \n{max_rewards}")
                        # if render:
                        #     # ax.plot(range(len(min_rewards)), min_rewards, '-r')
                        #     # ax.plot(range(len(average_rewards)), average_rewards, '-b')
                        #     # ax.plot(range(len(max_rewards)), max_rewards, '-g')
                        #     ax.scatter(episode, min_rewards[-1], c='r')
                        #     ax.scatter(episode, average_rewards[-1], c='b')
                        #     ax.scatter(episode, max_rewards[-1], c='g')
                        #     plt.show()
                        #     plt.pause(0.001)
                        # print("episode2: ", episode)
                        server.sendto(bytes("0", "utf-8"), address)  # send action to godot
                        # if step_total>REPLAY_EVERY:
                        #     agent.replay(REPLAY_EVERY//3)
                    step_total += 1
                    # if reward > 0:  # reward will be negative if episode does not end. for debugging
                elif action_list[address_index] is None and state_list[address_index] is not None:
                    action = agent.get_qs(np.reshape(next_state, [1, agent.state_size]))
                    action_list[address_index] = action
                    server.sendto(bytes(f"{action + 1}", "utf-8"), address)  # send action to godot
                elif action_list[address_index] is None and state_list[address_index] is None:
                    state_list[address_index] = np.reshape(next_state, [1, agent.state_size])
                    server.sendto(bytes("96", "utf-8"), address)  # send action to godot
            else:  # state is empty
                server.sendto(bytes("98", "utf-8"), address)  # send action to godot
    elif type_of_data is str:
        server.sendto(bytes("97", "utf-8"), address)  # send action to godot
    # Decay epsilon
    if agent.epsilon > agent.epsilon_min:
        agent.epsilon -= agent.epsilon_decay
        agent.epsilon = max(agent.epsilon_min, agent.epsilon)
        # print("episode: ", episode)
        # if not step_total % MIN_REPLAY_MEMORY_SIZE:
        # print("step total", step_total)
        print("epsilon: ", agent.epsilon)
    if not step_total % 1_000_000 and step_total > 1:
        # print(f"max_rewards: \n{max_rewards}")
        # print(f"step total: \n{state_list}")
        print("step total", step_total)
        agent.model0.save(f"models/dq/{model_name0}-{int(step_total/1000000)}M.h5py")
        agent.model1.save(f"models/dq/{model_name1}-{int(step_total / 1000000)}M.h5py")
        agent.model2.save(f"models/dq/{model_name2}-{int(step_total / 1000000)}M.h5py")
    # print("*", end="-")

