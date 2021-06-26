import simpy
import random

class Campsite(object):
    def __init__(self, env):
        self.env = env
        
        # meadow where groups with tent will stay
        self.tent_meadow = simpy.Resource(self.env, capacity = )
        # lots where groups with caravan will stay, usable by tents if tent meadow is full
        self.caravan_lots = simpy.Resource(self.env, capacity = )

        # limited number of people due to corona regulations
        self.people = simpy.Container(self.env, init=0, capacity=)

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


def arrival(env, campsite):
    while True:
        # choose number of new groups for this day
        num_groups = 

        # create new arriving groups
        groups = [env.process(camper(env, campsite)) for i in range(num_groups))]
        # go to next day
        yield env.timeout(1)

def camper(env, campsite, rng):
    # choose type of camper
    camper_type = 

    place = None
    if type == tent:
        place = campsite.tent_meadow
    elif type == caravan:
        place = campsite.caravan_lots

    # if tent: 1. try to occupy tent meadow
    #          2. or else try to occupy caravan lot

    with place.request as req():

        # try to enter campsite
        # TODO: abort if campsite is full
        yield req | env.timeout(0)

        # choose duration of stay
        duration = 

        # choose number of persons
        # TODO abort if overall person limit is reached
        # check all people in
        yield campsite.people.get(number_people)

        # calculate price

        # pay

        # occupy place on campsite during the duration of stay
        yield event.timeout(duration)

        # check people out
        yield campsite.people.put(number_people)
        # leave campsite automatically via python context manager

def resource_user(env, resource):
    with resource.request() as req:  # Generate a request event
        yield req                    # Wait for access
        yield env.timeout(1)         # Do something

def print_stats(res):
    print(f'{res.count} of {res.capacity} slots are allocated.')
    print(f'  Users: {res.users}')
    print(f'  Queued events: {res.queue}')


if __name__ == '__main__':

    for i in num_experiments:
        env = simpy.Environment()
        # create new empty campsite
        campsite = Campsite(env)
        # let the simulation tune in?

        # create arrival process which creates new arriving groups every day
        arriv = env.process(arrival(env))

        env.run(until=360) # simulate one year (with 12 month with 30 days each)

        # add statistics to overall statistics

    # calculate mean and stdev over all experiments
