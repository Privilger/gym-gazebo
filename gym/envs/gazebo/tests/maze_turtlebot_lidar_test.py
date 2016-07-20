#!/usr/bin/env python
import gym
import time
import numpy
import random
#import pandas

class QLearn:
    def __init__(self, actions, epsilon, alpha, gamma):
        self.q = {}
        self.epsilon = epsilon  # exploration constant
        self.alpha = alpha      # discount constant
        self.gamma = gamma      # discount factor
        self.actions = actions

    def getQ(self, state, action):
        return self.q.get((state, action), 0.0)

    def learnQ(self, state, action, reward, value):
        '''
        Q-learning:
            Q(s, a) += alpha * (reward(s,a) + max(Q(s') - Q(s,a))            
        '''
        oldv = self.q.get((state, action), None)
        if oldv is None:
            self.q[(state, action)] = reward
        else:
            self.q[(state, action)] = oldv + self.alpha * (value - oldv)

    def chooseAction(self, state, return_q=False):
        q = [self.getQ(state, a) for a in self.actions]
        maxQ = max(q)

        if random.random() < self.epsilon:
            minQ = min(q); mag = max(abs(minQ), abs(maxQ))
            # add random values to all the actions, recalculate maxQ
            q = [q[i] + random.random() * mag - .5 * mag for i in range(len(self.actions))] 
            maxQ = max(q)

        count = q.count(maxQ)
        # In case there're several state-action max values 
        # we select a random one among them
        if count > 1:
            best = [i for i in range(len(self.actions)) if q[i] == maxQ]
            i = random.choice(best)
        else:
            i = q.index(maxQ)

        action = self.actions[i]        
        if return_q: # if they want it, give it!
            return action, q
        return action

    def learn(self, state1, action1, reward, state2):
        maxqnew = max([self.getQ(state2, a) for a in self.actions])
        self.learnQ(state1, action1, reward, reward + self.gamma*maxqnew)

def render():
    render_skip = 100 #Skip first X episodes.
    render_interval = 5 #Show render Every Y episodes.
    render_episodes = 2 #Show Z episodes every rendering.

    if (x%render_interval == 0) and (x != 0) and (x > render_skip):
        env.render()
    elif ((x-render_episodes)%(render_interval) == 0) and (x != 0) and (x > render_skip):
        env.render(close=True)



if __name__ == '__main__':

    env = gym.make('GazeboMazeTurtlebotLidar-v0')

    last_time_steps = numpy.ndarray(0)

    qlearn = QLearn(actions=range(env.action_space.n),
                    alpha=0.7, gamma=0.8, epsilon=0.1)

    for x in range(3000):
        done = False

        accululated_reward = 0 #Should going forward give more reward then L/R ?

        observation = env.reset()

        render() #defined above, not env.render()

        state = ''.join(map(str, observation))

        for i in range(200):

            # Pick an action based on the current state
            action = qlearn.chooseAction(state)

            # Execute the action and get feedback
            observation, reward, done, info = env.step(action)

            nextState = ''.join(map(str, observation))

            #Must change
            if not(done):
                qlearn.learn(state, action, reward, nextState)
                state = nextState

            else:
                # Q-learn stuff
                reward = -200
                qlearn.learn(state, action, reward, nextState)
                last_time_steps = numpy.append(last_time_steps, [int(i + 1)])
                break 

            accululated_reward += reward
            print "EP:"+str(x+1)+" - IT:"+str(i+1)+" AR:"+str(accululated_reward)


    l = last_time_steps.tolist()
    l.sort()

    print("Overall score: {:0.2f}".format(last_time_steps.mean()))
    print("Best 100 score: {:0.2f}".format(reduce(lambda x, y: x + y, l[-100:]) / len(l[-100:])))

    env.close()
