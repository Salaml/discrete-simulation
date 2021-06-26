import simpy
import random

class Node(object):
    def __init__(self, env):
        self.channels = 

         self.env = env
         self.action = env.process(self.run())

     def run(self):
         while True:
             print('Start parking and charging at %d' % self.env.now)
             charge_duration = 5
             # We may get interrupted while charging the battery
             try:
                 yield self.env.process(self.charge(charge_duration))
             except simpy.Interrupt:
                 # When we received an interrupt, we stop charging and
                 # switch to the "driving" state
                 print('Was interrupted. Hope, the battery is full enough ')

             print('Start driving at %d' % self.env.now)
             trip_duration = 2
             yield self.env.timeout(trip_duration)

     def charge(self, duration):
         yield self.env.timeout(duration)


def node(name, env):
    while True:
        yield env.timeout(1)
        print('Node', name, 'sent message. t =', str(env.now))


def gateway(name, env):
    pass


if __name__ == '__main__':
    env = simpy.Environment()
    
    env.process(node('1', env))
    
    env.run(until=1200000)