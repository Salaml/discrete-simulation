import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RangeSlider, TextBox, Button


def normal_dist(x , mean , sd, scale=None):
    # if scale is set: discard normalization and set maximum value to value of scale
    return np.exp(-0.5 * ((x - mean) / sd)**2) * (1 / (sd * np.sqrt(2 * np.pi)) if scale is None else scale)

def norm_list(l):
    # normalize list of absolute frequencies to relative frequencies
    return [value / sum(l) for value in l]

def norm_dict(d):
    # normalize dict of absolute frequencies to relative frequencies
    return {key: value / sum(d.values()) for key, value in d.items()}


class MonteCarloSim(object):
    def __init__(self):
        # Parameter fuer Simulation
        # Normalverteilung neue Camper-Gruppen pro Tag
        self.dist_day_mean = 13
        self.dist_day_sd = 3
        # Multiplikator Nachfrage Jahresverlauf nach Monat
        self.dist_year_mean = 7.8 # Maximum gegen Ende Juli
        self.dist_year_sd = 1.1
        self.dist_year = [] # gets filled later with multiplicator for each day of year
        # Verteilung Anzahl Nächte pro Aufenthalt, maximal 14 Nächte
        self.dist_nights = [5, 5, 6, 7, 9, 8, 10, 6, 4, 3, 1, 1, 1, 2] # absolute Häufigkeit für 1 Nacht bis 14 Nächte
        # Verteilung Anzahl Personen pro Aufenthalt, maximal 4 Personen pro 'Reisegruppe'
        self.dist_people = [1, 5, 2, 4] # absolute Häufigkeit für 1 Person bis 4 Personen
        # Aufschluesselung nach Campertypen: Zelt, Zelt + PKW, Wohnwagen/-mobil
        self.share_types = {'tent': 1, 'car': 3, 'caravan': 6} # relativer Anteil der Typen
        self.price_types = {'tent': 5, 'car': 9, 'caravan': 15, 'person': 5} # Preise pro Nacht nach Typ

        self.costs_customer = -2 # tägliche Selbstkosten je übernachteter Person z.B. Wasser, Abfall
        self.costs_daily = -350 # tägliche Gemeinkosten z.B. Grundsteuer, Lohn

        self.N = 1000 # number of iterations for Monte-Carlo per intervall
        # granularity of time intervalls, smaller values are faster but less accurate
        self.days_per_year = 12 * 30 # divide year into 12 months with 30 days each
        # enable or disable specific dynamic input widgets, faster if disabled
        self.input_enable = {'seed': True, 'dist_day': True, 'dist_year': True, 'share_types': True, 'price_types': True, 'costs': True}
        self.seed = None
        self.rng = np.random.default_rng(self.seed)

        # Ergebnisse nach Tagen/Zeitintervallen
        self.result_groups = np.zeros(self.days_per_year) # Mittelwert Anzahl Gäste
        self.result_income = np.zeros(self.days_per_year) # Summe Einnahmen
        self.result_income_person = np.zeros(self.days_per_year) # Einnahmen durch Personen
        self.result_income_type = np.zeros(self.days_per_year) # Einnahmen durch Grundpreis je nach Typ
        self.result_costs_customers = np.zeros(self.days_per_year) # Selbstkosten abhängig von Personenzahl
        self.result_costs_daily = np.zeros(self.days_per_year) # Gemeinkosten
        self.result_balance = np.zeros(self.days_per_year) # Bilanz

        # normalize distributions
        self.dist_nights_norm = norm_list(self.dist_nights)
        self.dist_people_norm = norm_list(self.dist_people)
        self.share_types_norm = norm_dict(self.share_types)

        self.fig = plt.figure(constrained_layout=True, figsize=(16,9))
        self.fig.suptitle('Monte-Carlo-Simulation Campingplatz', weight='bold')
        self.fig_gs = self.fig.add_gridspec(4,4)

        b_calc = Button(plt.axes([0.08, 0.96, 0.1, 0.03]), 'Berechnung starten')
        b_calc.on_clicked(self.calculate)

        if self.input_enable['seed']:
            tb_seed = TextBox(plt.axes([0.14,0.92, 0.05, 0.03]), 'Seed Zufallszahlengenerator ', initial='' if self.seed is None else str(self.seed))
            tb_seed.on_submit(self.set_seed)

        if self.input_enable['dist_day']:
            tb_dist_day_mean = TextBox(plt.axes([0.14,0.88, 0.05, 0.03]), 'Mittelwert Tagesverteilung ', initial=str(self.dist_day_mean))
            tb_dist_day_mean.on_submit(self.set_dist_day_mean)
            tb_dist_day_sd = TextBox(plt.axes([0.14,0.85, 0.05, 0.03]), 'Std.-Abw. Tagesverteilung ', initial=str(self.dist_day_sd))
            tb_dist_day_sd.on_submit(self.set_dist_day_sd)

        if self.input_enable['dist_year']:
            tb_dist_year_mean = TextBox(plt.axes([0.14,0.81, 0.05, 0.03]), 'Mittelwert Multiplikator Jahr ', initial=str(self.dist_year_mean))
            tb_dist_year_mean.on_submit(self.set_dist_year_mean)
            tb_dist_year_sd = TextBox(plt.axes([0.14,0.78, 0.05, 0.03]), 'Std.-Abw. Multiplikator Jahr ', initial=str(self.dist_year_sd))
            tb_dist_year_sd.on_submit(self.set_dist_year_sd)

        if self.input_enable['share_types']:
            tb_share_tent = TextBox(plt.axes([0.14,0.74, 0.05, 0.03]), 'Anteil Zelt ', initial=str(self.share_types['tent']))
            tb_share_tent.on_submit(self.set_share_tent)
            tb_share_car = TextBox(plt.axes([0.14,0.71, 0.05, 0.03]), 'Anteil Zelt + PKW ', initial=str(self.share_types['car']))
            tb_share_car.on_submit(self.set_share_car)
            tb_share_caravan = TextBox(plt.axes([0.14,0.68, 0.05, 0.03]), 'Anteil Wohnwagen/-mobil ', initial=str(self.share_types['caravan']))
            tb_share_caravan.on_submit(self.set_share_caravan)

        if self.input_enable['price_types']:
            tb_price_tent = TextBox(plt.axes([0.14,0.64, 0.05, 0.03]), 'Preis Zelt ', initial=str(self.price_types['tent']))
            tb_price_tent.on_submit(self.set_price_tent)
            tb_price_car = TextBox(plt.axes([0.14,0.61, 0.05, 0.03]), 'Preis Zelt + PKW ', initial=str(self.price_types['car']))
            tb_price_car.on_submit(self.set_price_car)
            tb_price_caravan = TextBox(plt.axes([0.14,0.58, 0.05, 0.03]), 'Preis Wohnwagen/-mobil ', initial=str(self.price_types['caravan']))
            tb_price_caravan.on_submit(self.set_price_caravan)
            tb_price_person = TextBox(plt.axes([0.14,0.55, 0.05, 0.03]), 'Preis Person', initial=str(self.price_types['person']))
            tb_price_person.on_submit(self.set_price_person)

        if self.input_enable['costs']:
            tb_costs_customer = TextBox(plt.axes([0.14,0.51, 0.05, 0.03]), 'Selbstkosten pro Person/Nacht ', initial=str(self.costs_customer))
            tb_costs_customer.on_submit(self.set_costs_customer)
            tb_costs_daily = TextBox(plt.axes([0.14,0.48, 0.05, 0.03]), 'Gemeinkosten ', initial=str(self.costs_daily))
            tb_costs_daily.on_submit(self.set_costs_daily)

        self.dist_day_fig = self.fig.add_subplot(self.fig_gs[0,1], title='Verteilung neue Campergruppen pro Tag', xlabel='Anzahl Gruppen')
        self.dist_day_ax, = self.dist_day_fig.plot([0],[0]) # init with empty plot
        self.draw_dist_day()

        self.dist_year_fig = self.fig.add_subplot(self.fig_gs[1,1], title='Multiplikator Nachfrage Jahresverlauf', xlabel='Monat')
        self.dist_year_ax, = self.dist_year_fig.plot([0],[0]) # init with empty plot
        self.draw_dist_year()

        self.share_types_fig = self.fig.add_subplot(self.fig_gs[2,0], title='Verteilung Campertypen')
        share_types_label = ('Zelt', 'Zelt+PKW', 'Wohnwagen\n/-mobil')
        x = np.arange(len(share_types_label))
        self.share_types_ax = self.share_types_fig.bar(x, range(len(x))) # init with dummy values
        self.share_types_fig.set_xticks(x)
        self.share_types_fig.set_xticklabels(share_types_label)
        self.draw_share_types()

        self.price_types_fig = self.fig.add_subplot(self.fig_gs[2,1], title='Preise Campertypen')
        price_types_label = ('Zelt', 'Zelt+PKW', 'Wohnwagen\n/-mobil', 'Person')
        x = np.arange(len(price_types_label))
        self.price_types_ax = self.price_types_fig.bar(x, range(len(x))) # init with dummy values
        self.price_types_fig.set_xticks(x)
        self.price_types_fig.set_xticklabels(price_types_label)
        self.draw_price_types()

        self.dist_nights_fig = self.fig.add_subplot(self.fig_gs[3,0], title='Verteilung Aufenthaltsdauer', xlabel='Anzahl Nächte')
        self.dist_nights_ax = self.dist_nights_fig.bar(range(1, 1 + len(self.dist_nights_norm)), self.dist_nights_norm)
        self.dist_nights_fig.set_xticks(range(1, 1 + len(self.dist_nights_norm)))
        #self.draw_dist_nights()

        self.dist_people_fig = self.fig.add_subplot(self.fig_gs[3,1], title='Verteilung Personen pro Gruppe', xlabel='Anzahl Personen')
        self.dist_people_ax = self.dist_people_fig.bar(range(1, 1 + len(self.dist_people_norm)), self.dist_people_norm)
        self.dist_people_fig.set_xticks(range(1, 1 + len(self.dist_people_norm)))
        #self.draw_dist_people()

        # results
        self.result_groups_fig = self.fig.add_subplot(self.fig_gs[0,2:4], title='Ergebnis: Gruppen pro Tag', xlabel='Monat')
        self.result_groups_ax, = self.result_groups_fig.plot([0],[0]) # init with empty plot

        self.result_balance_fig = self.fig.add_subplot(self.fig_gs[1:3,2:4], title='Ergebnis: Bilanz pro Tag', xlabel='Monat')
        self.result_income_ax, = self.result_balance_fig.plot([0],[0], label='Gesamteinnahmen')
        self.result_income_person_ax, = self.result_balance_fig.plot([0],[0], label='Einnahmen Grundpreis')
        self.result_income_type_ax, = self.result_balance_fig.plot([0],[0], label='Einnahmen Personen')
        self.result_costs_customers_ax, = self.result_balance_fig.plot([0],[0], label='Selbstkosten')
        self.result_costs_daily_ax, = self.result_balance_fig.plot([0],[0], label='Gemeinkosten')
        self.result_balance_ax, = self.result_balance_fig.plot([0],[0], label='Bilanz')
        self.result_balance_fig.legend()

        self.table_balance_fig = self.fig.add_subplot(self.fig_gs[3,2], frameon=False)
        self.table_balance_fig.set_axis_off()
        balance_label = ('Mittelwert', 'Standardabweichung', 'Maximum', 'Summe')
        self.table_balance_ax = self.table_balance_fig.table(cellText=[' ']*4, rowLabels=balance_label, colLabels=('Bilanz',), cellLoc='left', loc='center')

        self.table_customers_fig = self.fig.add_subplot(self.fig_gs[3,3], frameon=False)
        self.table_customers_fig.set_axis_off()
        customers_label = ('Mittelwert', 'Standardabweichung', 'Maximum')
        self.table_customers_ax = self.table_customers_fig.table(cellText=[' ']*3, rowLabels=customers_label, colLabels=('Gruppen',), cellLoc='left', loc='center')

        plt.show()

    def draw_dist_year(self):
        x = np.linspace(0,12, self.days_per_year)
        y = normal_dist(x, self.dist_year_mean, self.dist_year_sd, 1)
        self.dist_year = y
        self.dist_year_ax.set_xdata(x)
        self.dist_year_ax.set_ydata(y)
        self.dist_year_fig.relim()
        self.dist_year_fig.autoscale_view()
        plt.draw()

    def set_dist_year_mean(self, mean):
        self.dist_year_mean = float(mean)
        self.draw_dist_year()

    def set_dist_year_sd(self, sd):
        self.dist_year_sd = float(sd)
        self.draw_dist_year()

    def draw_dist_day(self):
        x = np.linspace(max(0, self.dist_day_mean - 4 * self.dist_day_sd), self.dist_day_mean + 4 * self.dist_day_sd, 100)
        y = normal_dist(x, self.dist_day_mean, self.dist_day_sd)
        self.dist_day_ax.set_xdata(x)
        self.dist_day_ax.set_ydata(y)
        self.dist_day_fig.relim()
        self.dist_day_fig.autoscale_view()
        plt.draw()

    def set_dist_day_mean(self, mean):
        self.dist_day_mean = float(mean)
        self.draw_dist_day()

    def set_dist_day_sd(self, sd):
        self.dist_day_sd = float(sd)
        self.draw_dist_day()

    def draw_share_types(self):
        self.share_types_norm = norm_dict(self.share_types)
        y = [self.share_types_norm['tent'], self.share_types_norm['car'], self.share_types_norm['caravan']]
        for rect, height in zip(self.share_types_ax, y):
            rect.set_height(height)
        self.share_types_fig.relim()
        self.share_types_fig.autoscale_view()
        plt.draw()

    def set_share_tent(self, share_tent):
        self.share_types['tent'] = float(share_tent)
        self.draw_share_types()

    def set_share_car(self, share_car):
        self.share_types['car'] = float(share_car)
        self.draw_share_types()

    def set_share_caravan(self, share_caravan):
        self.share_types['caravan'] = float(share_caravan)
        self.draw_share_types()

    def draw_price_types(self):
        y = [self.price_types['tent'], self.price_types['car'], self.price_types['caravan'], self.price_types['person']]
        for rect, height in zip(self.price_types_ax, y):
            rect.set_height(height)
        self.price_types_fig.relim()
        self.price_types_fig.autoscale_view()
        plt.draw()

    def set_price_tent(self, price_tent):
        self.price_types['tent'] = float(price_tent)
        self.draw_price_types()

    def set_price_car(self, price_car):
        self.price_types['car'] = float(price_car)
        self.draw_price_types()

    def set_price_caravan(self, price_caravan):
        self.price_types['caravan'] = float(price_caravan)
        self.draw_price_types()

    def set_price_person(self, price_person):
        self.price_types['person'] = float(price_person)
        self.draw_price_types()

    def set_costs_customer(self, costs_customer):
        self.costs_customer = float(costs_customer)

    def set_costs_daily(self, costs_daily):
        self.costs_daily = float(costs_daily)

    def draw_result_groups(self):
        self.result_groups_ax.set_xdata(np.linspace(0,12, self.days_per_year))
        self.result_groups_ax.set_ydata(self.result_groups)
        self.result_groups_fig.relim()
        self.result_groups_fig.autoscale_view()
        plt.draw()

    def draw_result_balance(self):
        x = np.linspace(0,12, self.days_per_year)

        self.result_income_ax.set_xdata(x)
        self.result_income_ax.set_ydata(self.result_income)
        self.result_income_person_ax.set_xdata(x)
        self.result_income_person_ax.set_ydata(self.result_income_person)
        self.result_income_type_ax.set_xdata(x)
        self.result_income_type_ax.set_ydata(self.result_income_type)

        self.result_costs_customers_ax.set_xdata(x)
        self.result_costs_customers_ax.set_ydata(self.result_costs_customers)
        self.result_costs_daily_ax.set_xdata(x)
        self.result_costs_daily_ax.set_ydata(self.result_costs_daily)

        self.result_balance_ax.set_xdata(x)
        self.result_balance_ax.set_ydata(self.result_balance)

        self.result_balance_fig.relim()
        self.result_balance_fig.autoscale_view()
        plt.draw()

    def draw_table_balance(self):
        self.table_balance_ax[1, 0].set_text_props(text=str(round(np.mean(self.result_balance), 2)))
        self.table_balance_ax[2, 0].set_text_props(text=str(round(np.std(self.result_balance), 2)))
        self.table_balance_ax[3, 0].set_text_props(text=str(round(max(self.result_balance), 2)))
        self.table_balance_ax[4, 0].set_text_props(text=str(round(sum(self.result_balance), 2)))

        self.table_balance_fig.relim()
        self.table_balance_fig.autoscale_view()
        plt.draw()

    def draw_table_customers(self):
        self.table_customers_ax[1, 0].set_text_props(text=str(round(np.mean(self.result_groups), 2)))
        self.table_customers_ax[2, 0].set_text_props(text=str(round(np.std(self.result_groups), 2)))
        self.table_customers_ax[3, 0].set_text_props(text=str(round(max(self.result_groups), 2)))

        self.table_customers_fig.relim()
        self.table_customers_fig.autoscale_view()
        plt.draw()

    def set_seed(self, seed):
        # numpy requires int as seed, random seed if empty
        self.seed = (None if seed == '' else int(seed))

    def calculate(self, _):
        # use seed for reproducibility
        if self.seed is not None:
            self.rng = np.random.default_rng(self.seed)

        # weights and values for discrete propability distributions
        weights_types = [self.share_types_norm['tent'], self.share_types_norm['car'], self.share_types_norm['caravan']]
        values_types = [self.price_types['tent'], self.price_types['car'], self.price_types['caravan']]
        weights_nights = self.dist_nights_norm
        values_nights = range(1, 1+len(weights_nights))
        weights_people = self.dist_people_norm
        values_people = range(1, 1+len(weights_people))
        
        progress = 0

        # iterate over year
        for day in range(self.days_per_year):
            # random number of new groups independent of time of year, do self.N experiments
            list_num_groups = self.rng.normal(self.dist_day_mean, self.dist_day_sd, size=self.N)
            # apply multiplicator specific to time of year, round to integer numbers, clip to minimum value 0
            list_num_groups = np.maximum(np.around(self.dist_year[day] * list_num_groups), 0).astype(int)
            self.result_groups[day] = np.mean(list_num_groups)
            
            # iterate over self.N experiments
            income_person = []
            income_type = []
            costs_customers = []
            for num_groups in list_num_groups:
                if num_groups == 0:
                    income_person.append(0)
                    income_type.append(0)
                    costs_customers.append(0)
                else:
                    # num_groups groups arrived this day, determine price for type, nights & people for all groups
                    base_prices = self.rng.choice(values_types, p=weights_types, size=num_groups) # price for type
                    nights = self.rng.choice(values_nights, p=weights_nights, size=num_groups)
                    people = self.rng.choice(values_people, p=weights_people, size=num_groups)
                    # Einnahmen = Grundpreis Typ * Nächte + Preis Person * Personen * Nächte
                    income_person.append(sum(self.price_types['person'] * people * nights))
                    income_type.append(sum(base_prices * nights))
                    # Ausgaben = Kosten pro Person * Personen * Nächte
                    costs_customers.append(sum(self.costs_customer * people * nights))

            # store mean values of self.N experiments
            self.result_income_person[day] = np.mean(income_person)
            self.result_income_type[day] = np.mean(income_type)
            self.result_costs_customers[day] = np.mean(costs_customers)
            self.result_costs_daily[day] = self.costs_daily

            # show progress
            percent = round(100 * day / self.days_per_year)
            if percent - progress >= 10:
                progress = percent
                print(f"{progress}%")

        self.result_income = self.result_income_person + self.result_income_type
        self.result_balance = self.result_income + self.result_costs_customers + self.result_costs_daily

        self.draw_result_groups()
        self.draw_result_balance()
        self.draw_table_balance()
        self.draw_table_customers()

sim = MonteCarloSim()
