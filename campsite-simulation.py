print('loading libraries...')
import simpy
import random
from math import exp, sqrt, pi
from enum import Enum


def normal_dist(x , mean , sd, scale=None):
    # if scale is set: discard normalization and set maximum value to value of scale
    return exp(-0.5 * ((x - mean) / sd)**2) * (1 / (sd * sqrt(2 * pi)) if scale is None else scale)


def accumulate_dict(d):
    # takes a dict with weights as values and returns two lists: 
    # values and the corresponding cumulative weights each with same sorting
    values = []
    cum_weights = []
    for value, weight in d.items():
        values.append(value)
        cum_weights.append(( 0 if len(cum_weights) == 0 else cum_weights[-1] ) + weight)
    return values, cum_weights


class Camperform(Enum):
    # just a tent
    TENT = 0
    # a tent and a car
    TENT_CAR = 1
    # a caravan
    CARAVAN = 2


class Camper(object):
    def __init(self, form, size, duration):
        # form of this camper, one of Camperform
        self.form = form
        # number of people
        self.size = size
        # duration of stay on campsite
        self.duration = duration


class Campsite(object):
    def __init__(self, env, prices, costs, sizes):
        # simulation environment
        self.env = env
        
        # meadow where campers with tent will stay
        self.tent_meadow = simpy.Resource(self.env, capacity=sizes.size_meadow)
        # lots where campers with caravan will stay, usable by tents if tent meadow is full
        self.caravan_lots = simpy.Resource(self.env, capacity=sizes.num_lots)

        # limited number of people due to corona regulations
        self.people = simpy.Container(self.env, init=0, capacity=sizes.limit_people)

        # daily prices and costs
        self.prices = prices
        self.costs = costs

    def check_in(self, camper):
        pass


    def camp(self, camper):
        """The camping processes. It takes a ``camper`` process and lets it
        stay at the campsite for the given duration."""
        yield self.env.timeout(camper.duration)
        print("%s stayed %d days until %d." %
              (camper, camper.duration, env.now))



def setup(env, settings):
    """Creates a campsite. Creates new arriving groups on every new day
    and let them try to check in to the campsite."""
    # create new empty campsite
    campsite = Campsite(env, settings.prices, settings.costs, settings.sizes)

    # new groups arrive every day
    while True:
        day = env.now % 360

        # choose random number of new groups for this day, independent of day in year
        num_groups = random.normalvariate(settings.groups.day_mean, settings.groups.day_sd)
        # apply multiplicator specific to day in year, round to integer numbers, clip to minimum value 0
        num_groups = max(round(settings.groups.year[day] * num_groups), 0)

        for i in range(num_groups):
            # create new arriving campers, they try to check in on camp site
            env.process(new_camper(env, str(day) + '-' + str(i), campsite, settings.campers))

        # proceed to next day
        yield env.timeout(1)


def new_camper(env, name, campsite, dists):
    # choose form of camper
    form = random.choices(dists.form_val, cum_weights=dists.form_wght)[0]

    places = []
    if form is Camperform.TENT or form is Camperform.TENT_CAR:
        # tents belong firstly to the tent meadow
        places.append(campsite.tent_meadow)
        # usage of caravon lot is possible if tent meadow is full
        places.append(campsite.caravan_lots)
    elif form is Camperform.CARAVAN:
        # caravans belong always to the caravan lots
        places.append(campsite.caravan_lots)
    else:
        # TODO unknown form
        pass
        print('unknown place', form)

    for place in places:
        place_available = False

        #print('%s arrives at %.2f.' % (name, env.now))
        with place.request() as request:

            # try to enter campsite
            # TODO: abort if campsite is full
            entered = yield request | env.timeout(0)
            #print('%s enters at %.2f.' % (name, env.now))

            # check if aborted
            if request in entered:
                place_available = True

                # choose duration of stay
                duration = random.choices(dists.duration_val, cum_weights=dists.duration_wght)[0]

                # choose number of people
                num_people = random.choices(dists.people_val, cum_weights=dists.people_wght)[0]

                # TODO abort if overall people limit is reached
                # check all people in
                checked_in = yield campsite.people.put(num_people) | env.timeout(0)
                if checked_in: # TODO
                    pass
                else:
                    pass

                # calculate price

                # pay

                # occupy place on campsite during the duration of stay
                yield env.timeout(duration)

                # check people out
                yield campsite.people.get(num_people)
                
            else:
                # campsite is full
                # TODO add rejection to statistics
                pass

            # leave campsite automatically via python context manager

        if place_available:
            # place is available, no further looping over other places required
            break
        else:
            print("%s rejected at %f" % (name, env.now))


def resource_user(env, resource):
    with resource.request() as req:  # Generate a request event
        yield req                    # Wait for access
        yield env.timeout(1)         # Do something


def print_stats(res):
    print(f'{res.count} of {res.capacity} slots are allocated.')
    print(f'  Users: {res.users}')
    print(f'  Queued events: {res.queue}')


class DistGroups(object):
    # parameters for normal distribution of number of new camper groups per day
    day_mean = 12
    day_sd = 4

    # multiplicator for demand in course of the year
    # normal distribution with maximum at mean scaled to 1
    # (0 = begin of january, 11 = begin of december)
    year_mean = 7.0 # maximum at end of july / begin of august
    year_sd = 2.5

    # do not edit, gets filled later with multiplicator for each day of year
    year = []


class DistCampers(object):
    # distribution of camping forms, absolute frequencies
    form = {Camperform.TENT: 1, Camperform.TENT_CAR: 3, Camperform.CARAVAN: 6}

    # distribution of duration of stay in nights, absolute frequencies
    duration = {1: 5, 2: 5, 3: 6, 4: 7, 5: 9, 6: 8, 7:10, 8: 6, 9: 4, 10: 3, 11: 1, 12: 1, 13: 1, 14: 2}

    # distribution of number of people per group, absolute frequencies
    people = {1: 1, 2: 5, 3: 2, 4: 4}

    # do not edit, get filled later with values from dicts
    form_val = []
    duration_val = []
    people_val = []
    # do not edit, get filled later with cumulative weights from dicts
    form_wght = []
    duration_wght = []
    people_wght = []


class Prices(object):
    # daily price per person
    person = 5
    # daily base price for a group depending on form of camper
    form = {Camperform.TENT: 5, Camperform.TENT_CAR: 9, Camperform.CARAVAN: 15}


class Costs(object):
    # daily costs per person (e. g. electricity, water)
    person = -2
    # daily fixed costs (e. g. land tax, wages)
    daily = -350


class Sizes(object):
    # number of places of tent meadow, tent = 1 place, tent + car = 2 places
    size_meadow = 20
    # number of lots for caravans
    num_lots = 50

    # limited number of people for whole campsite due to corona regulations
    limit_people = simpy.core.Infinity # infinity = no limit


class Settings(object):
    # integrate all settings into 1 class, edit settings in specific classes
    groups = DistGroups
    campers = DistCampers
    prices = Prices
    costs = Costs
    sizes = Sizes


if __name__ == '__main__':

    # make simulation reproducible if not None
    random.seed(42)

    num_experiments = 1

    # calculate multiplicator for each day of year (360 days = 12 month * 30 days per month)
    Settings.groups.year = [normal_dist(day / 30, Settings.groups.year_mean, Settings.groups.year_sd, 1) for day in range(12 * 30)]

    # calculate cumulative weights from absolute frequencies
    Settings.campers.form_val, Settings.campers.form_wght = accumulate_dict(Settings.campers.form)
    Settings.campers.duration_val, Settings.campers.duration_wght = accumulate_dict(Settings.campers.duration)
    Settings.campers.people_val, Settings.campers.people_wght = accumulate_dict(Settings.campers.people)

    for i in range(num_experiments):
        env = simpy.Environment()
        startup = env.process(setup(env, Settings))

        env.run(until=360) # simulate one year with 360 days (12 month * 30 days per month)

        # add statistics to overall statistics

    # calculate mean and stdev of results over all experiments
