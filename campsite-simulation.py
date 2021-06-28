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


def print_msg(time, *args, **kwargs):
    #return
    print(f"{time:.1f}:", *args, **kwargs)



class Usage():
    """"""
    def __init__(self, limit):
        self.limit = None # maximum number of users, same for all days
        self.count = [] # number of users, day-wise
        self.new = [] # number of new users, day-wise
        self.reject = [] # number of users rejected due to maximum usage, day-wise


class Statistics():
    def __init__(self, limit_tent_meadow, limit_caravan_lots, limit_people):
        self.tent_meadow = Usage(limit_tent_meadow)
        self.caravan_lots = Usage(limit_caravan_lots)
        self.people = Usage(limit_people)


class Camperform(Enum):
    # just a tent, only allowed on tent meadow (needs 1 place)
    TENT = 0
    # a tent and a car, only allowed on tent meadow (needs 2 places)
    TENT_CAR = 1
    # a caravan, only allowed on caravan lots
    CARAVAN = 2


class Campsite(object):
    def __init__(self, env, sizes):
        # simulation environment
        self.env = env
        
        # meadow where campers with tent will stay
        self.tent_meadow = simpy.Container(self.env, init=0, capacity=sizes.size_meadow)
        # lots where campers with caravan will stay
        self.caravan_lots = simpy.Container(self.env, init=0, capacity=sizes.num_lots)

        # limited number of people due to corona regulations (unlimited is possible with capacity=simpy.core.Infinity)
        self.people = simpy.Container(self.env, init=0, capacity=sizes.limit_people)


def setup(env, settings):
    """Creates a campsite. Creates new arriving groups on every new day
    and let them try to check in to the campsite."""
    # create new empty campsite
    campsite = Campsite(env, settings.sizes)

    print_msg(env.now, "start simulation")

    # new groups arrive every day
    while True:
        day = env.now % 360

        # choose random number of new groups for this day, independent of day in year
        num_groups = random.normalvariate(settings.groups.day_mean, settings.groups.day_sd)
        # apply multiplicator specific to day in year, round to integer numbers, clip to minimum value 0
        num_groups = max(round(settings.groups.year[day] * num_groups), 0)

        # choose random form for every group
        forms = random.choices(settings.campers.form_val, cum_weights=settings.campers.form_wght, k=num_groups)

        # choose random duration of stay for every group
        durations = random.choices(settings.campers.duration_val, cum_weights=settings.campers.duration_wght, k=num_groups)

        # choose random number of people for every group
        num_people = random.choices(settings.campers.people_val, cum_weights=settings.campers.people_wght, k=num_groups)

        for i in range(num_groups):
            # create new arriving campers, they try to check in on camp site
            env.process(camper(env, str(day) + '-' + str(i), campsite, forms[i], num_people[i], durations[i]))

        # calculate statistics for this day
        # TODO

        # proceed to next day
        yield env.timeout(1)


def camper(env, name, campsite, form, num_people, duration):
    """Models 1 camper group defined by form, number of people and duration of stay.
    Group tries to check in on given campsite. Prerequisites needed for successful check in:
        -maximum number of people on campsite (corona regulations) not reached
        -a free place on campsite depending on form of camper"""

    # check all people in, abort instantly via timeout(0) if campsite people limit (corona regulations) is reached
    check_in = campsite.people.put(num_people)
    checked_in = yield check_in | env.timeout(0)
    if check_in not in checked_in:
        print_msg(env.now, name, f"reject {num_people} people, limit reached ({campsite.people.level}/{campsite.people.capacity})")
        # TODO add to statistics
    else:
        # check in successful (in terms of people limit), try to get place on campsite
        request_place = None
        if form is Camperform.TENT:
            # tents need 1 place on the tent meadow
            request_place = campsite.tent_meadow.put(1)
        elif  form is Camperform.TENT_CAR:
            # tents with car need 2 places on the tent meadow
            request_place = campsite.tent_meadow.put(2)
        elif form is Camperform.CARAVAN:
            # caravans belong to the caravan lots and need 1 lot
            request_place = campsite.caravan_lots.put(1)

        # try to get place on campsite fitting to form of camper
        # abort instantly if no place available via timeout(0)
        place_available = yield request_place | env.timeout(0)
        if request_place not in place_available:
            # campsite is full
            # TODO add rejection to statistics
            print_msg(env.now, name, f"reject {form}, no place available")
        else:
            print_msg(env.now, name, f"check in {form}, {num_people} people, {duration} nights")

            # calculate price
            # pay
            # add to statistics

            # occupy place on campsite during the duration of stay
            # check out before 11:30, check in after 14:00 => remove 2.5 hours (0.1 days) time difference from duration
            yield env.timeout(duration - 0.1)

            # leave place on campsite after stay
            if form is Camperform.TENT:
                yield campsite.tent_meadow.get(1)
            elif  form is Camperform.TENT_CAR:
                yield campsite.tent_meadow.get(2)
            elif form is Camperform.CARAVAN:
                yield campsite.caravan_lots.get(1)

            print_msg(env.now, name, f"check out")

        # check people out
        yield campsite.people.get(num_people)



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


class DistCampers(object):
    # distribution of camping forms, absolute frequencies
    form = {Camperform.TENT: 1, Camperform.TENT_CAR: 3, Camperform.CARAVAN: 6}

    # distribution of duration of stay in nights, absolute frequencies
    duration = {1: 5, 2: 5, 3: 6, 4: 7, 5: 9, 6: 8, 7: 10, 8: 6, 9: 4, 10: 3, 11: 1, 12: 1, 13: 1, 14: 2}

    # distribution of number of people per group, absolute frequencies
    people = {1: 1, 2: 5, 3: 2, 4: 4}


class Prices(object):
    # daily price per person
    person = 5
    # daily base price for a group depending on form of camper
    form = {Camperform.TENT: 5, Camperform.TENT_CAR: 9, Camperform.CARAVAN: 15}


class Costs(object):
    # daily costs per person (e. g. electricity, water)
    person = -2
    # daily fixed costs (e. g. land tax, wages)
    daily = -200


class Sizes(object):
    # number of places of tent meadow
    size_meadow = 4#30
    # number of lots for caravans
    num_lots = 21#50

    # limited number of people for whole campsite due to corona regulations
    limit_people = 10#simpy.core.Infinity # infinity = no limit


class Settings(object):
    # integrate all settings into 1 class, edit settings in specific classes
    groups = DistGroups
    campers = DistCampers
    prices = Prices
    costs = Costs
    sizes = Sizes

    # general simulation settings
    # make simulation reproducible if not None
    seed = 42
    # number of repetitions of simulation, results are averaged over all experiments
    num_experiments = 25


if __name__ == '__main__':

    # calculate multiplicator for each day of year (360 days = 12 month * 30 days per month)
    Settings.groups.year = [normal_dist(day / 30, Settings.groups.year_mean, Settings.groups.year_sd, 1) for day in range(12 * 30)]

    # calculate cumulative weights from absolute frequencies
    Settings.campers.form_val, Settings.campers.form_wght = accumulate_dict(Settings.campers.form)
    Settings.campers.duration_val, Settings.campers.duration_wght = accumulate_dict(Settings.campers.duration)
    Settings.campers.people_val, Settings.campers.people_wght = accumulate_dict(Settings.campers.people)

    random.seed(Settings.seed)

    statistics = []

    for _ in range(Settings.num_experiments):
        statistic = Statistics(Settings.sizes.size_meadow, Settings.sizes.num_lots, Settings.sizes.limit_people)

        env = simpy.Environment()
        startup = env.process(setup(env, Settings))

        env.run(until=30) # simulate one year with 360 days (12 month * 30 days per month)

        # add statistics to overall statistics
        statistics.append(statistic)

    # calculate mean and stdev of results over all experiments
