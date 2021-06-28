import random
from math import exp, sqrt, pi
from enum import Enum
import simpy
import matplotlib.pyplot as plt


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
    return
    print(f"{time:.1f}:", *args, **kwargs)


def plot_parameter(settings):
    plt.figure(figsize=(8,8))
    plt.suptitle('Parameter Simulation Campingplatz', weight='bold')

    plt.subplot(321, title='Verteilung neue Campergruppen pro Tag', xlabel='Anzahl Gruppen')
    day_x_min = max(0, settings.groups.day_mean - 4 * settings.groups.day_sd)
    day_x_max = settings.groups.day_mean + 4 * settings.groups.day_sd
    day_x = [(day_x_max - day_x_min) * x / 100 for x in range(100)]
    day_y = [normal_dist(x, settings.groups.year_mean, settings.groups.year_sd) for x in day_x]
    plt.plot(day_x, day_y)

    fig = plt.subplot(322, title='Multiplikator Nachfrage Jahresverlauf', xlabel='Monat')
    year_x = [12 * x / len(settings.groups.year) for x in range(len(settings.groups.year))]
    plt.plot(year_x, settings.groups.year)
    fig.set_xticks(list(range(1,13)))

    plt.subplot(323, title='Verteilung Campertypen')
    plt.bar(('Zelt', 'Zelt+PKW', 'Wohnwagen\n/-mobil'), settings.campers.form.values())

    plt.subplot(324, title='Preise Campertypen')
    prices_y = list(settings.prices.form.values())
    prices_y.append(settings.prices.person)
    plt.bar(('Zelt', 'Zelt+PKW', 'Wohnwagen\n/-mobil', 'Person'), prices_y)

    fig = plt.subplot(325, title='Verteilung Aufenthaltsdauer', xlabel='Anzahl Nächte')
    plt.bar(settings.campers.duration.keys(), settings.campers.duration.values())
    fig.set_xticks(list(settings.campers.duration.keys()))

    fig = plt.subplot(326, title='Verteilung Personen pro Gruppe', xlabel='Anzahl Personen')
    plt.bar(settings.campers.people.keys(), settings.campers.people.values())
    fig.set_xticks(list(settings.campers.people.keys()))

    plt.tight_layout()


def plot_usage(statistics):
    plt.figure(figsize=(10,9))
    plt.suptitle('Auslastung Campingplatz', weight='bold')

    fig = plt.subplot(321, title='Anzahl Gäste', xlabel='Monat')
    count_x = [12 * x / len(statistics.people.count) for x in range(len(statistics.people.count))]
    plt.plot(count_x, statistics.people.count, linestyle='', marker='.')
    if statistics.people.limit != simpy.core.Infinity:
        plt.axhline(statistics.people.limit, color='red', linestyle='--', label='Limit')
        plt.legend()
    fig.set_xticks(list(range(1,13)))

    fig = plt.subplot(322, title='neue Gäste', xlabel='Monat')
    new_x = [12 * x / len(statistics.people.new) for x in range(len(statistics.people.new))]
    plt.plot(new_x, statistics.people.new, linestyle='', marker='.', label='gesamt')
    reject_x = [12 * x / len(statistics.people.reject) for x in range(len(statistics.people.reject))]
    plt.plot(reject_x, statistics.people.reject, linestyle='', marker='.', label='abgelehnt')
    fig.set_xticks(list(range(1,13)))
    plt.legend()

    fig = plt.subplot(323, title='genutze Plätze Zeltwiese', xlabel='Monat')
    count_x = [12 * x / len(statistics.tent_meadow.count) for x in range(len(statistics.tent_meadow.count))]
    plt.plot(count_x, statistics.tent_meadow.count, linestyle='', marker='.')
    if statistics.tent_meadow.limit != simpy.core.Infinity:
        plt.axhline(statistics.tent_meadow.limit, color='red', linestyle='--', label='Limit')
        plt.legend()
    fig.set_xticks(list(range(1,13)))

    fig = plt.subplot(324, title='neue Gruppen Zeltwiese', xlabel='Monat')
    new_x = [12 * x / len(statistics.tent_meadow.new) for x in range(len(statistics.tent_meadow.new))]
    plt.plot(new_x, statistics.tent_meadow.new, linestyle='', marker='.', label='gesamt')
    reject_x = [12 * x / len(statistics.tent_meadow.reject) for x in range(len(statistics.tent_meadow.reject))]
    plt.plot(reject_x, statistics.tent_meadow.reject, linestyle='', marker='.', label='abgelehnt')
    fig.set_xticks(list(range(1,13)))
    plt.legend()

    fig = plt.subplot(325, title='genutze Parzellen Caravan', xlabel='Monat')
    count_x = [12 * x / len(statistics.caravan_lots.count) for x in range(len(statistics.caravan_lots.count))]
    plt.plot(count_x, statistics.caravan_lots.count, linestyle='', marker='.')
    if statistics.caravan_lots.limit != simpy.core.Infinity:
        plt.axhline(statistics.caravan_lots.limit, color='red', linestyle='--', label='Limit')
        plt.legend()
    fig.set_xticks(list(range(1,13)))

    fig = plt.subplot(326, title='neue Gruppen Caravan', xlabel='Monat')
    new_x = [12 * x / len(statistics.caravan_lots.new) for x in range(len(statistics.caravan_lots.new))]
    plt.plot(new_x, statistics.caravan_lots.new, linestyle='', marker='.', label='gesamt')
    reject_x = [12 * x / len(statistics.caravan_lots.reject) for x in range(len(statistics.caravan_lots.reject))]
    plt.plot(reject_x, statistics.caravan_lots.reject, linestyle='', marker='.', label='abgelehnt')
    fig.set_xticks(list(range(1,13)))

    plt.tight_layout()


def plot_financial(statistics):
    plt.figure(figsize=(10,9))
    balance_total = round(sum(statistics.balance))
    balance_mean = round(balance_total / len(statistics.balance))
    title = f"Finanzen Campingplatz, Gesamtbilanz = {balance_total}, Schnitt Bilanz pro Tag = {balance_mean}"
    plt.suptitle(title, weight='bold')

    earnings_person_x = [12 * x / len(statistics.earnings_person) for x in range(len(statistics.earnings_person))]
    plt.plot(earnings_person_x, statistics.earnings_person, linestyle='', marker='.', label='Einnahmen Personen')
    earnings_base_x = [12 * x / len(statistics.earnings_base) for x in range(len(statistics.earnings_base))]
    plt.plot(earnings_base_x, statistics.earnings_base, linestyle='', marker='.', label='Einnahmen Grundpreis')
    costs_person_x = [12 * x / len(statistics.costs_person) for x in range(len(statistics.costs_person))]
    plt.plot(costs_person_x, statistics.costs_person, linestyle='', marker='.', label='Selbstkosten')
    costs_base_x = [12 * x / len(statistics.costs_base) for x in range(len(statistics.costs_base))]
    plt.plot(costs_base_x, statistics.costs_base, linestyle='', marker='.', label='Gemeinkosten')
    balance_x = [12 * x / len(statistics.balance) for x in range(len(statistics.balance))]
    fig = plt.plot(balance_x, statistics.balance, linestyle='', marker='.', label='Bilanz')
    #fig.set_xticks(list(range(1,13)))
    plt.legend()

    plt.tight_layout()


class Usage():
    """"""
    def __init__(self, limit):
        self.limit = limit # maximum number of users, same for all days
        self.count = [] # number of users, day-wise
        self.new = [] # number of new users, day-wise
        self.reject = [] # number of users rejected due to maximum usage, day-wise

    def add_empty_day(self):
        self.count.append(0)
        self.new.append(0)
        self.reject.append(0)


class Statistics():
    def __init__(self, limit_tent_meadow, limit_caravan_lots, limit_people):
        self.tent_meadow = Usage(limit_tent_meadow)
        self.caravan_lots = Usage(limit_caravan_lots)
        self.people = Usage(limit_people)

        self.earnings_person = [] # earnings depending on number people, day-wise
        self.earnings_base = [] # earnings by base price depending on camper form, day-wise

        self.costs_person = [] # costs depending on number of people (water, ...), costs are negative values, day-wise
        self.costs_base = [] # daily fixed costs (wages, ...), costs are negative values, day-wise

        self.balance = [] # earnings + costs

    def add_empty_day(self):
        self.tent_meadow.add_empty_day()
        self.caravan_lots.add_empty_day()
        self.people.add_empty_day()

        self.earnings_person.append(0)
        self.earnings_base.append(0)

        self.costs_person.append(0)
        self.costs_base.append(0)

    def add_usage(self, form, count=0, new=0, reject=0):
        target = None
        if form is None:
            target = self.people
        elif form is Camperform.TENT:
            target = self.tent_meadow
        elif form is Camperform.TENT_CAR:
            target = self.tent_meadow
            # tent with car takes twice the space of a single tent
            count *= 2
            new *= 2
            reject *= 2
        elif form is Camperform.CARAVAN:
            target = self.caravan_lots

        target.count[-1] += count
        target.new[-1] += new
        target.reject[-1] += reject

    def add_financial(self, earnings_person=0, earnings_base=0, costs_person=0, costs_base=0):
        self.earnings_person[-1] += earnings_person
        self.earnings_base[-1] += earnings_base

        self.costs_person[-1] += costs_person
        self.costs_base[-1] += costs_base

    def calc_balance(self):
        self.balance = [sum(x) for x in zip(self.earnings_person, self.earnings_base, self.costs_person, self.costs_base)]

    @staticmethod
    def average_list(list_statistics, averaged):
        """averages all properties of list of Statistics objects into single Statistics object"""
        averaged.tent_meadow.count = [sum(x) / len(x) for x in zip(*[stat.tent_meadow.count for stat in list_statistics])]
        averaged.tent_meadow.new = [sum(x) / len(x) for x in zip(*[stat.tent_meadow.new for stat in list_statistics])]
        averaged.tent_meadow.reject = [sum(x) / len(x) for x in zip(*[stat.tent_meadow.reject for stat in list_statistics])]
        
        averaged.caravan_lots.count = [sum(x) / len(x) for x in zip(*[stat.caravan_lots.count for stat in list_statistics])]
        averaged.caravan_lots.new = [sum(x) / len(x) for x in zip(*[stat.caravan_lots.new for stat in list_statistics])]
        averaged.caravan_lots.reject = [sum(x) / len(x) for x in zip(*[stat.caravan_lots.reject for stat in list_statistics])]
        
        averaged.people.count = [sum(x) / len(x) for x in zip(*[stat.people.count for stat in list_statistics])]
        averaged.people.new = [sum(x) / len(x) for x in zip(*[stat.people.new for stat in list_statistics])]
        averaged.people.reject = [sum(x) / len(x) for x in zip(*[stat.people.reject for stat in list_statistics])]
        
        averaged.earnings_person = [sum(x) / len(x) for x in zip(*[stat.earnings_person for stat in list_statistics])]
        averaged.earnings_base = [sum(x) / len(x) for x in zip(*[stat.earnings_base for stat in list_statistics])]
        
        averaged.costs_person = [sum(x) / len(x) for x in zip(*[stat.costs_person for stat in list_statistics])]
        averaged.costs_base = [sum(x) / len(x) for x in zip(*[stat.costs_base for stat in list_statistics])]


class Camperform(Enum):
    # just a tent, only allowed on tent meadow (needs 1 place)
    TENT = 0
    # a tent and a car, only allowed on tent meadow (needs 2 places)
    TENT_CAR = 1
    # a caravan, only allowed on caravan lots
    CARAVAN = 2


class Campsite(object):
    def __init__(self, env, prices, costs, sizes):
        # simulation environment
        self.env = env
        
        # meadow where campers with tent will stay
        self.tent_meadow = simpy.Container(self.env, init=0, capacity=sizes.size_meadow)
        # lots where campers with caravan will stay
        self.caravan_lots = simpy.Container(self.env, init=0, capacity=sizes.num_lots)

        # limited number of people due to corona regulations (unlimited is possible with capacity=simpy.core.Infinity)
        self.people = simpy.Container(self.env, init=0, capacity=sizes.limit_people)

        # daily prices and costs
        self.prices = prices
        self.costs = costs


def setup(env, settings, statistics):
    """Creates a campsite. Creates new arriving groups on every new day
    and let them try to check in to the campsite."""
    # create new empty campsite
    campsite = Campsite(env, settings.prices, settings.costs, settings.sizes)

    print_msg(env.now, "start simulation")

    # new groups arrive every day
    while True:
        day = round(env.now % 360)

        # prepare statistics for this day
        statistics.add_empty_day()

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
            env.process(camper(env, str(day) + '-' + str(i), campsite, forms[i], num_people[i], durations[i], statistics))

        # wait until all campers have checked in / were rejected
        yield env.timeout(0.1)

        # gather statistics
        statistics.add_usage(None, count=campsite.people.level)
        statistics.add_usage(Camperform.TENT, count=campsite.tent_meadow.level)
        statistics.add_usage(Camperform.CARAVAN, count=campsite.caravan_lots.level)

        cost_people = campsite.costs.person * campsite.people.level
        costs_base = campsite.costs.base
        statistics.add_financial(costs_person=cost_people, costs_base=costs_base)

        # proceed to next day
        yield env.timeout(0.9)


def camper(env, name, campsite, form, num_people, duration, statistics):
    """Models 1 camper group defined by form, number of people and duration of stay.
    Group tries to check in on given campsite. Prerequisites needed for successful check in:
        -maximum number of people on campsite (corona regulations) not reached
        -a free place on campsite depending on form of camper"""

    # check all people in, abort instantly via timeout(0) if campsite people limit (corona regulations) is reached
    check_in = campsite.people.put(num_people)
    checked_in = yield check_in | env.timeout(0)
    if check_in not in checked_in:
        # check in not successful, group goes to another campsite -> cancel pending request
        check_in.cancel()
        print_msg(env.now, name, f"reject {num_people} people, limit reached ({campsite.people.level}/{campsite.people.capacity})")
        # add to statistics
        statistics.add_usage(None, reject=num_people)
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
            # campsite is full, group goes to another campsite -> cancel pending request
            request_place.cancel()
            print_msg(env.now, name, f"reject {form}, no place available")
            # add rejection to statistics
            statistics.add_usage(form, reject=num_people)
        else:
            print_msg(env.now, name, f"check in {form}, {num_people} people, {duration} nights")

            # calculate price to pay
            price_people = campsite.prices.person * num_people * duration
            price_base = campsite.prices.form[form] * duration

            # add to statistics
            statistics.add_financial(earnings_person=price_people, earnings_base=price_base)
            statistics.add_usage(form, new=1) # for tent meadow / caravan lots
            statistics.add_usage(None, new=num_people) # for people limit

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

            print_msg(env.now, name, "check out")

        # check people out
        yield campsite.people.get(num_people)


################################################################################
################################### Settings ###################################
################################################################################

class DistGroups(object):
    # parameters for normal distribution of number of new camper groups per day
    day_mean = 12
    day_sd = 4

    # multiplicator for demand in course of the year
    # normal distribution with maximum at mean scaled to 1
    # (0 = begin of january, 11 = begin of december)
    year_mean = 7.0 # maximum at end of july / begin of august
    year_sd = 2.0


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
    base = -350


class Sizes(object):
    # number of places of tent meadow
    size_meadow = 50
    # number of lots for caravans
    num_lots = 30

    # limited number of people for whole campsite due to corona regulations
    limit_people = 150 # no limit with simpy.core.Infinity


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

################################################################################
################################################################################
################################################################################

if __name__ == '__main__':

    # calculate multiplicator for each day of year (360 days = 12 month * 30 days per month)
    Settings.groups.year = [normal_dist(day / 30, Settings.groups.year_mean, Settings.groups.year_sd, 1) for day in range(12 * 30)]

    # calculate cumulative weights from absolute frequencies
    Settings.campers.form_val, Settings.campers.form_wght = accumulate_dict(Settings.campers.form)
    Settings.campers.duration_val, Settings.campers.duration_wght = accumulate_dict(Settings.campers.duration)
    Settings.campers.people_val, Settings.campers.people_wght = accumulate_dict(Settings.campers.people)

    random.seed(Settings.seed)

    statistics = [] # list of statistics with one entry per experiment

    for _ in range(Settings.num_experiments):
        statistic = Statistics(Settings.sizes.size_meadow, Settings.sizes.num_lots, Settings.sizes.limit_people)

        env = simpy.Environment()
        startup = env.process(setup(env, Settings, statistic))

        env.run(until=360) # simulate one year with 360 days (12 month * 30 days per month)

        # add statistics to overall statistics
        statistics.append(statistic)

    # calculate mean of results over all experiments
    statistic_mean = Statistics(Settings.sizes.size_meadow, Settings.sizes.num_lots, Settings.sizes.limit_people)
    Statistics.average_list(statistics, statistic_mean)

    # calculate financial balance
    statistic_mean.calc_balance()

    # show everything in pretty format
    plot_parameter(Settings)
    plot_usage(statistic_mean)
    plot_financial(statistic_mean)
    plt.show()
