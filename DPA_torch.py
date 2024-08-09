import random
import gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import DPA_Env
import main as CTB
import baidu_chatglm2
import commandrun

#创建智能体
class QLearningAgent:
    def __init__(self, env):
        self.env = env
        self.state_size = env.observation_Space.n   #状态空间大小
        self.action_size = env.action_space.n       #动作空间大小
        self.learning_rate = 0.01                   #学习率
        self.epsilon = 1.0                          #探索率
        self.epsilon_min = 0.01                     #最小探索率
        self.epsilon_decay = 0.995                  #探索率衰减因子
        self.gamma = 0.95                           #折扣因子
        self.model = self._build_model()            #构建神经网络模型
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate) #优化器
        self.memory = []                            #经验回放
    #建立模型
    def _build_model(self):
        model = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self.state_size, 24),
            nn.ReLU(),
            nn.Linear(24, self.action_size),
            nn.Linear(self.action_size, self.action_size)
        )
        return model
    #存储记忆
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    #定义动作
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return self.env.action_space.sample()
        state = torch.from_numpy(state).float().unsqueeze(0)
        act_values = self.model(state)
        return torch.argmax(act_values).item()
    #经验回放
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * torch.max(self.model(next_state))
            state = torch.from_numpy(state).float().unsqueeze(0)
            target_f = self.model(state)
            target_f[0][action] = target
            self.optimizer.zero_grad()
            loss = nn.MSELoss()(target_f, target_f.clone().detach())
            loss.backward()
            self.optimizer.step()
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    #载入模型
    def load(self, name):
        self.model.load_state_dict(torch.load(name))
    #保存模型
    def save(self, name):
        torch.save(self.model.state_dict(), name)

if __name__ == "__main__":
    env = DPA_Env.Network_explorer()    #使用自定义的环境
    agent = QLearningAgent(env)      #创建代理
    batch_size = 1
    episodes = 5    #定义训练次数
    result_c = "error"
    timeout = 10
    for e in range(1, episodes):
        state = env.reset()
        state = np.reshape(state, [1, env.observation_Space.n])
        if CTB.judge_env() == "empty":
            ip = CTB.get_ip()
            while result_c == "error":
                result_c = baidu_chatglm2.chat_with_baidu_command(ip)
            result_c = commandrun.run_command_with_timeout(result_c, timeout)
            tmp = result_c
            while result_c == "error" or result_c == tmp:
                result_c = baidu_chatglm2.chat_with_baidu_nmap(result_c)
        for _ in range(10):
            action = agent.act(state) #代理选择动作
            next_state, reward, done = env.step(action) #执行动作返回参数
            next_state = np.reshape([2, env.observation_Space.n], next_state)
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            if done:
                print("episode: {}/{}, score: {}".format(e, episodes, reward))
                break
        agent.replay(batch_size)
