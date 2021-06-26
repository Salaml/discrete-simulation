print('loading libraries...')
import simpy
import random
from enum import enum
import itertools

def normal_dist(x , mean , sd, scale=None):
    # if scale is set: discard normalization and set maximum value to value of scale
    return np.exp(-0.5 * ((x - mean) / sd)**2) * (1 / (sd * np.sqrt(2 * np.pi)) if scale is None else scale)

def norm_list(l):
    # normalize list of absolute frequencies to relative frequencies
    return [value / sum(l) for value in l]

def norm_dict(d):
    # normalize dict of absolute frequencies to relative frequencies
    return {key: value / sum(d.values()) for key, value in d.items()}


class Camperform(Enum):
    # just a tent
    TENT = 1
    # a tent and a car
    TENT_CAR = 2
    # a caravan
    CARAVAN = 3

class Camper(object):
    def __init(self, form, size, duration):
        # form of this camper, one of Camperform
        self.form = form
        # number of people
        self.size = size
        # duration of stay on campsite
        self.duration = duration


class Campsite(object):
    def __init__(self, env, size_meadow, num_lots, limit_people,
            prices_form, price_person):
        # simulation environment
        self.env = env
        
        # meadow where campers with tent will stay
        self.tent_meadow = simpy.Resource(self.env, capacity=size_meadow)
        # lots where campers with caravan will stay, usable by tents if tent meadow is full
        self.caravan_lots = simpy.Resource(self.env, capacity=num_lots)

        # limited number of people due to corona regulations
        self.people = simpy.Container(self.env, init=0, capacity=limit_people)

        # daily base price depending on form of camper
        self.prices_form = prices_form
        # daily price per person
        self.price_person = price_person

    def check_in(self, camper):


    def camp(self, camper):
        """The camping processes. It takes a ``camper`` process and lets it
        stay at the campsite for the given duration."""
        yield self.env.timeout(camper.duration)
        print("%s stayed %d days until %d." %
              (camper, camper.duration, env.now))



def setup(env, settings):
    """Creates a campsite. Creates new arriving campers on every new day
    and let them try to check in to the campsite."""
    # settings
    # TODO
    size_meadow = 20
    num_lots = 50
    limit_people = simpy.core.Infinity

    # create new empty campsite
    campsite = Campsite(env, size_meadow, num_lots, limit_people, 
            prices_form, price_person)

    # new campers arrive every day
    for day in itertools.count():
        # choose number of new campers for this day
        num_campers = 

        for i in range(num_campers):
            # create new arriving campers, they try to check in on camp site
            env.process(camper(env, str(day) + '-' + str(i), campsite))

        # wait for next day
        yield env.timeout(1)

def camper(env, name, campsite, rng=None):
    # choose form of camper
    form = 

    place = None
    if form is Camperform.TENT or form is Camperform.TENT_CAR:
        place = campsite.tent_meadow
    elif form is Camperform.CARAVAN:
        place = campsite.caravan_lots
    else:
        # TODO unknown form

    # if tent: 1. try to occupy tent meadow
    #          2. or else try to occupy caravan lot

    print('%s arrives at %.2f.' % (name, env.now))
    with place.request as request():

        # try to enter campsite
        # TODO: abort if campsite is full
        entered = yield request | env.timeout(0)
        print('%s enters at %.2f.' % (name, env.now))

        # check if aborted
        if request in entered:

            # choose duration of stay
            duration = 

            # choose number of persons
            # TODO abort if overall person limit is reached
            # check all people in
            checked_in = yield campsite.people.put(number_people) | env.timeout(0)
            if in checked_in:
                pass
            else:
                pass

            # calculate price

            # pay

            # occupy place on campsite during the duration of stay
            yield event.timeout(duration)

            # check people out
            yield campsite.people.get(number_people)
            
        else:
            # campsite is full
            # TODO add rejection to statistics

        # leave campsite automatically via python context manager


def resource_user(env, resource):
    with resource.request() as req:  # Generate a request event
        yield req                    # Wait for access
        yield env.timeout(1)         # Do something

def print_stats(res):
    print(f'{res.count} of {res.capacity} slots are allocated.')
    print(f'  Users: {res.users}')
    print(f'  Queued events: {res.queue}')


class Settings(object):
    # parameters for normal distribution of number of new camper groups per day
    dist_day_mean = 12
    dist_day_sd = 4

    # multiplicator for demand in course of the year
    # normal distribution with maximum at mean scaled to 1
    # (0 = begin of january, 11 = begin of december)
    dist_year_mean = 7.0 # maximum at end of july / begin of august
    dist_year_sd = 2.5

    # distribution of camping forms, absolute frequencies
    dist_form = {Camperform.TENT: 1, Camperform.TENT_CAR: 3, Camperform.CARAVAN: 6}

    # distribution of duration of stay in nights, 14 nights at max, absolute frequencies
    dist_duration = [5, 5, 6, 7, 9, 8, 10, 6, 4, 3, 1, 1, 1, 2]
    # distribution of number of people per group, 4 people at max, absolute frequencies
    dist_person = [1, 5, 2, 4]

    # daily price per person
    price_person = 5
    # daily base price for a group depending on form of camper
    prices_form = {Camperform.TENT: 5, Camperform.TENT_CAR: 9, Camperform.CARAVAN: 15}

    # daily costs per person (e. g. waste, water)
    costs_person = -2
    # daily fixed costs (e. g. land tax, wages)
    costs_daily = -350



    dist_year = [] # gets filled later with multiplicator for each day of year


if __name__ == '__main__':

    for i in num_experiments:
        env = simpy.Environment()
        # let the simulation tune in?

        # create arrival process which creates new arriving campers every day
        arriv = env.process(arrival(env))

        env.run(until=360) # simulate one year (with 12 month with 30 days each)

        # add statistics to overall statistics

    # calculate mean and stdev over all experiments
