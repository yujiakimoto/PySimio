import numpy as np
import pygame
import datetime
from time import sleep
from arrival import generate_arrival
import re


class Event:
    def __init__(self, time, bus, bus_stop, event_type):
        self.time = time            # time at which the event occurs
        self.bus = bus              # bus object
        self.bus_stop = bus_stop    # the event location of the bus object
        self.type = event_type      # either 'departure' or 'arrival'

    def print_event(self):
        """ when the simulation is DEBUG mode, print the event on console """
        print("{} : {} event at {} at t = {}\n".format(self.bus.name, self.type, self.bus_stop.name, self.time))


class Map:
    def __init__(self, routes, buses, bus_stops, name='Ithaca'):
        self.name = name                    # name of this map
        self.routes = routes                # list of Route objects that the map provides
        self.buses = buses                  # list of Bus objects in this map
        self.bus_stops = bus_stops          # list of BusStop objects
        self.event_queue = []               # an event queue to manage discrete simulation
        self.prev_time = 0                  # keep track of previous event time
        self.surface = None

    def simulate(self, max_time, debug=False, animate=False, **settings):
        """Run simulation of this map
        Args:
            max_time (float): number of minutes for which to run the simulation
            debug (boolean): whether or not to run the simulation in debug mode
            animate(boolean): whether or not to render an animation of the simulation
            **settings: keyword-arguments specifying settings of the animation
        """
        time = 0
        # initialize the event queue
        for i, bus in enumerate(self.buses):
            if bus.route == self.routes[1]:         # buses on Route 2 must start at depot, then change
                bus.change_route(self.routes[0])
            # TODO: implement better staggered departures
            self.event_queue.append(Event(27*i/7, bus, self.bus_stops['TDOG Depot'], 'departure'))

        # draw bus stop (if animate) and generate new data
        for bus_stop in self.bus_stops.values():
            bus_stop.generate_data(max_time)
            if animate:
                self.surface = settings['surface']
                bus_stop.add_animation(settings['surface'], settings['coordinates'][bus_stop.name])

        # main loop
        while time < max_time:
            if debug:                                                       # wait for user input to proceed
                input()

            if animate:
                self.update_clock(settings['surface'], time)
                for bus_stop in self.bus_stops.values():
                    bus_stop.update(time)                                   # fine-grained animation (much slower)

            sorted_queue = sorted(self.event_queue, key=lambda x: x.time)   # sort the event queue
            self.event_queue = sorted_queue[1:]                             # shift the queue by 1
            next_event = sorted_queue[0]                                    # get the next earliest event
            time = next_event.time                                          # current event time
            delta_time = time - self.prev_time                              # time - time_lst to calculate the integral

            if debug:                                                       # print the event
                next_event.print_event()

            # update the utility
            for b in self.buses:
                b.avg_occupancy += delta_time * b.occupancy                       # average occupancy of each bus
                b.avg_standing += delta_time * max(b.occupancy - b.num_seats, 0)  # average people standing for each bus

            for bs in self.bus_stops.keys():
                bs = self.bus_stops[bs]
                bs.avg_num_waiting += delta_time * bs.num_waiting                 # average people waiting at each stop

            for bs in self.bus_stops.keys():                                      # average people waiting at each hour
                bs = self.bus_stops[bs]
                hour = int(time/60)
                if hour not in bs.avg_num_waiting_t.keys():
                    bs.avg_num_waiting_t[hour] = 0
                    bs.num_waiting_hr = 0
                bs.avg_num_waiting_t[hour] += delta_time * bs.num_waiting_hr


            # TODO: make this more elegant
            if time > max_time:
                break

            # process arrival event
            if next_event.type == "arrival":
                new_route = None
                if next_event.bus.route2 and next_event.bus.distance == 2.5:
                    new_route = self.routes[1]
                if next_event.bus_stop.name == "TDOG Depot":
                    # TODO: define the optimal policy to re-route buses
                    new_route = next_event.bus.route

                dpt_event = next_event.bus.arrive(next_event.bus_stop, next_event.time, new_route, debug=debug)
                self.event_queue.append(dpt_event)

            # process departure event
            else:
                # TODO: calculate the delay time for the bus
                delay = 0
                arv_event = next_event.bus.depart(next_event.bus_stop, next_event.time, time + delay)
                self.event_queue.append(arv_event) # add arrival event to the queue

            self.prev_time = time # update the last event time

        # update the utility
        for b in self.buses:
            b.avg_occupancy /= max_time
            b.avg_standing /= max_time

        for bs in self.bus_stops.keys():
            bs = self.bus_stops[bs]
            bs.avg_num_waiting /= max_time
            waiting_t = bs.avg_num_waiting_t
            waiting_t = np.array([value for (key, value) in sorted(bs.avg_num_waiting_t.items())])
            bs.avg_num_waiting_t = waiting_t/60


        print('Simulation complete')
        # self.reset()

    def update_clock(self, surface, elapsed):
        """Updated clock in bottom right corner of animation"""
        clear = pygame.image.load('images/blank.png')
        clear_rect = clear.get_rect()
        clear_rect.bottomright = (1080, 720)
        surface.blit(clear, clear_rect)

        font_med = pygame.font.SysFont("Helvetica", 15)
        start = datetime.datetime(2017, 12, 1, 6, 0)
        current = (start + datetime.timedelta(minutes=elapsed)).time()
        clock = font_med.render('Time: ' + str(current)[:5], 1, (255, 255, 255))
        surface.blit(clock, (990, 690))

    def collect_stats(self):
        """ Called after the simulation to collect the stats"""
        stats = {}
        total_traveled = 0
        for bus in self.buses:
            stats[bus.name + " distance"] = bus.distance            # traveling distance for each bus
            total_traveled += bus.distance                          # traveling distance for all buses
            stats[bus.name + " avg occupancy"] = bus.avg_occupancy  # average occupancy for each buses
            stats[bus.name + " avg standing"] = bus.avg_standing    # average number of people standing for each bus

        for bs in self.bus_stops.keys():
            bs = self.bus_stops[bs]
            stats[bs.name + " avg people waiting"] = bs.avg_num_waiting  # avg. number of people waiting at each stop
            stats[bs.name + " hourly people waiting"] = re.split("\[ |\]", str(bs.avg_num_waiting_t))[1]
            total_waiting = 0
            total_people = 0
            for dest in bs.waiting_time.keys():
                avg_waiting = bs.waiting_time[dest]/bs.num_getoff[dest]
                stats[bs.name + "-" + dest + " waiting time"] = avg_waiting
                total_waiting += bs.waiting_time[dest]
                total_people += bs.num_getoff[dest]

            if total_people != 0:
                stats[bs.name + " waiting time total"] = total_waiting/total_people

        stats['total distance'] = total_traveled  # total distance traveled
        return stats

    def reset(self):
        """ reset simulation """
        # TODO : make this cleaner
        self.prev_time = 0
        # reset the stats for each bus
        for bus in self.buses:
            bus.reset()
        # reset the stats for each bus stop
        for bus_stop in self.bus_stops.values():
            bus_stop.reset()
            if bus_stop.animate:
                bus_stop.update(0)
                self.update_clock(self.surface, 0)


class Bus:
    """ Models a bus travelling around Ithaca.

    Attributes:
        route (Route): A Route object denoting which route this bus takes.
        next_stop_num (int): The stop number of the next stop this bus will stop at.
        next_stop (BusStop): A BusStop object denoting the next stop this bus will stop at.

        passengers (list): A list of Person objects representing the passengers on this bus.
        occupancy (int): The number of people currently on this bus.
        num_seats(int): The number of seats on this bus.
        standing_cap(int): The number of people that can be standing on this bus.
        max_cap(int): The maximum total capacity of this bus.

        distance (float): Total distance travelled by this bus

    """
    def __init__(self, name, route):

        assert(isinstance(route, Route)), "route must be a Route object"

        self.name = name
        self.route = route
        self.route2 = route.num == 2                       # indicates whether bus is supposed to be on route 2

        self.next_stop_num = 1                             # bus starts at first stop, i.e. index 0
        self.next_stop = self.route.stops[1]

        self.passengers = []                               # bus starts with nobody on it
        self.occupancy = 0
        self.num_seats = 25                                # default number of seats is 25
        self.standing_cap = 10                             # default standing capacity is 10
        self.max_cap = self.num_seats + self.standing_cap  # default total capacity is 25+10=35

        self.distance = 0                                  # distance travelled by this bus
        # TODO: other relevant performance metrics?
        self.avg_occupancy = 0
        self.avg_standing = 0

        self.animate = False
        self.surface = None
        self.icon = None
        self.icon_rect = None,

    def goes_to(self, stop):
        """Returns True if this bus goes to the specified stop and False otherwise"""

        assert(isinstance(stop, BusStop)), "stop must be a BusStop"
        return stop in self.route.stops

    def change_route(self, route):
        """Change the route that this bus travels on"""
        # TODO: implement better logic to find appropriate next stop
        self.route = route
        self.next_stop_num = 1
        self.next_stop = self.route.stops[1]

    def board(self, stop, time):
        """Models the process of people boarding this bus at a certain stop"""
        # people waiting at bus stop will get on if bus goes to desired destination and there is space on the bus
        stop.update(time)
        boarding_time = time
        for person in stop.people_waiting:
            if self.goes_to(person.destination) and self.occupancy < self.max_cap:
                self.passengers.append(person)
                self.occupancy += 1

                stop.people_waiting.remove(person)
                stop.num_waiting -= 1
                stop.num_waiting_hr -= 1
                stop.num_waiting_hr = max(0, stop.num_waiting_hr)

                person.waiting_time = boarding_time - person.start_time  # record waiting time
                person.origin.add_waiting_time(person.destination, person.waiting_time) # update the origin waiting time
                # boarding_time += np.random.triangular(0, 1/60, 5/60)   # boarding times have triangular distribution
                stop.update(boarding_time)  # people arrive while bus is boarding

                person.state = 'standing'

        return boarding_time

    def arrive(self, stop, time, new_route=None, debug=False):
        """Models a bus arriving a BusStop stop at a given time"""

        if self.animate:
            # self.update_animation()
            pass

        assert(isinstance(stop, BusStop)), "must arrive at a BusStop"
        # print('{} arrived at {} at t = {}'.format(self.name, self.next_stop.name, time))
        self.next_stop_num = self.next_stop_num % (len(self.route.stops) - 1) + 1    # update next stop number
        self.next_stop = self.route.stops[self.next_stop_num]

        # change route if necessary
        if new_route is not None:
            self.change_route(new_route)

        # if current stop is destination, passenger will get off
        for person in self.passengers:
            if person.destination == stop:
                self.passengers.remove(person)
                self.occupancy -= 1
                # TODO: add time taken for people to get off?
                person.state = 'arrived'
        if debug:
            print('After arrival, occupancy =', self.occupancy)

        return Event(time, self, stop, 'departure')

    def depart(self, stop, time, earliest_depart):
        """Models a bus driving from one stop to another"""

        distance_travelled = self.route.distances[self.next_stop_num - 1]
        self.distance += distance_travelled                # add distance travelled by bus

        if distance_travelled < 2:
            driving_time = (distance_travelled/20) * 60    # average speed of 20km/hr, convert to minutes
        else:
            # driving_time = np.random.uniform(5, 7)       # average speed of 20km/hr, +/-1 min variability
            driving_time = 6

        done_boarding = self.board(stop, time)
        if done_boarding < earliest_depart:
            done_boarding = self.board(stop, time)

        # first 25 passengers will sit down (or all, if less than 25 people on bus)
        for i in range(min(self.occupancy, 25)):
            self.passengers[i].state = 'sitting'

        return Event(done_boarding + driving_time, self, self.next_stop, 'arrival')

    def add_animation(self, surface, depot):
        self.animate = True
        self.surface = surface
        self.icon = pygame.image.load('images/bus.png')
        self.icon_rect = self.icon.get_rect()
        self.icon_rect.center = (depot.surface_pos[0] - 55, depot.surface_pos[1])
        self.surface.blit(self.icon, self.icon_rect)

    def update_animation(self):
        self.icon_rect.center = (self.next_stop.surface_pos[0] - 55, self.next_stop.surface_pos[1])
        self.surface.blit(self.icon, self.icon_rect)
        pygame.display.flip()

    def reset(self):
        self.next_stop_num = 1
        self.next_stop = self.route.stops[1]
        self.passengers = []
        self.occupancy = 0
        self.distance = 0
        self.avg_occupancy = 0
        self.avg_standing = 0


class BusStop:
    """ Models a bus stop somewhere in Ithaca.

    Attributes:
        name (str): Name of the bus stop.
        num_waiting (int): Number of people currently waiting at this bus stop.
        people_waiting (list): List of person objects representing people waiting at this bus stop

        times (dict): Dict of arrival times of people arriving at this bus stop

    """
    def __init__(self, name):

        self.name = name            # name of bus stop
        self.num_waiting = 0        # bus stop starts with nobody waiting
        self.num_waiting_hr = 0     # hourly waiting number at bus stop
        self.people_waiting = []    # list of people waiting at this stop; initially empty
        self.arrival_rates = {}     # dict of arrival rates (key:destination, value: arrival rate)
        self.times = {}             # dict of arrival times (key:destination, value:list of times)

        self.prev_num_waiting = 0   # used in animation to remove old images
        self.animate = False        # whether or not to generate animation
        self.surface = None         # pygame.Surface object on which to render animation
        self.surface_pos = ()       # location on screen; (0,0) is the top left corner

        self.avg_num_waiting = 0    # statistics for number of people waiting
        self.waiting_time = {}      # destination(str) -> waiting time
        self.num_getoff = {}        # destination(str) -> number of people used this path

        self.avg_num_waiting_t = {} # destination(str) -> list of number per hour

    def add_data(self, arrival_rates):
        """Record arrival rates to this bus stop as a dict (key: destination, value: arrival rate(s))"""
        self.arrival_rates = arrival_rates

    def generate_data(self, max_time):
        # TODO: generate with non-constant arrival rate
        for stop in self.arrival_rates.keys():
            lmbda = self.arrival_rates[stop]
            np.random.seed()
            if isinstance(lmbda, (list, np.ndarray)):
                self.times[stop] = list(generate_arrival(lmbda, interval=180))
            elif isinstance(lmbda, (int, float)):
                self.times[stop] = list(np.cumsum(np.random.exponential(1/lmbda, int(max_time*lmbda))))
            else:
                raise ValueError('Arrival rates must be specified as a number or list/array.')

    def add_animation(self, surface, coords):
        """Set animation attributes
        Args:
            surface (pygame.Surface): pygame Surface object on which to render the animation
            coords (tuple): a tuple of ints/floats specifying the (x,y) location of the bus stop
        """
        self.animate = True
        self.surface = surface
        self.surface_pos = coords

    def update_animation(self):
        """Updates the animation screen to reflect current people waiting at this bus stop"""
        # remove unused images
        clear = pygame.image.load('images/nobody.png')
        for i in range(self.prev_num_waiting):
            clear_rect = clear.get_rect()
            clear_rect.center = (self.surface_pos[0] + 35 + 5*i, self.surface_pos[1])
            self.surface.blit(clear, clear_rect)

        # colour-code images of people by destination
        person_img = {'Wegmans-Eastbound': pygame.image.load('images/person_green.png'),
                      'Wegmans-Westbound': pygame.image.load('images/person_green.png'),
                      'Commons-Eastbound': pygame.image.load('images/person_blue.png'),
                      'Commons-Westbound': pygame.image.load('images/person_blue.png'),
                      'Collegetown': pygame.image.load('images/person_orange.png')}
        for i, person in enumerate(self.people_waiting):
            person_rect = person_img[person.destination.name].get_rect()
            person_rect.center = (self.surface_pos[0] + 35 + 5*i, self.surface_pos[1])
            self.surface.blit(person_img[person.destination.name], person_rect)
        self.prev_num_waiting = self.num_waiting

    def arrival(self, person):
        """Models the arrival of a person to a bus stop"""
        self.num_waiting += 1
        self.num_waiting_hr += 1
        self.people_waiting.append(person)

    def add_waiting_time(self, dest, time):
        """Add waiting time in the dictionary """
        if dest.name in self.waiting_time.keys():
            self.waiting_time[dest.name] += time
            self.num_getoff[dest.name] += 1
        else:
            self.waiting_time[dest.name] = time
            self.num_getoff[dest.name] = 1

    def update(self, time):
        """Updates arrivals to this bus stop until a given time"""
        for destination, arrival_times in self.times.items():
            for arrival_time in arrival_times:
                if arrival_time < time:
                    self.arrival(Person(self, destination, arrival_time))
                    arrival_times.remove(arrival_time)
                else:
                    break
        if self.animate:
            self.update_animation()
            sleep(0.1)              # controls speed of animation
            pygame.display.flip()      # update display

    def reset(self):
        """Reset map to initial (or newly generated) settings"""
        self.num_waiting = 0
        self.people_waiting = []
        self.num_waiting_hr = 0
        self.avg_num_waiting = 0
        self.waiting_time = {}
        self.num_getoff = {}
        self.avg_num_waiting_t = {}


class Person:
    """ Models a person trying to get around Ithaca.

    Attributes:
        origin (BusStop): Where this person starts.
        destination (BusStop): Where this person is trying to get to.

        state (str): Describes state of person. One of 'waiting', 'sitting', 'standing', 'arrived'.
        start_time (float): Time at which person arrived at origin bus stop.
        waiting_time (float): Time spent waiting at origin bus stop.

    """
    def __init__(self, origin, destination, time):

        assert(isinstance(origin, BusStop)), "origin must be a BusStop"
        assert(isinstance(destination, BusStop)), "destination must be a BusStop"

        self.origin = origin               # origin bus stop
        self.destination = destination     # destination bus stop

        self.state = 'waiting'             # status of person, either 'waiting', 'standing' or 'sitting'
        self.start_time = time             # time at which person started waiting
        self.waiting_time = None           # time spent waiting at bus stop
        origin.arrival(self)


class Route:
    """ Models 1 of 3 bus routes around Ithaca.

    Attributes:
        stops (list): A list of BusStop objects representing all the stops on this route. Includes starting
            stop as both the first and last element if the route is a loop (which they all are).
        distances (list): A list of floats representing the distances between each of the stops on the route.
            Length should be one less than the length of stopList.
        num (int): Route number as defined in writeup.

    """
    def __init__(self, stop_list, distance_list, number):

        assert(all(isinstance(stop, BusStop) for stop in stop_list)), "stopList must be a list of BusStop objects"
        assert (len(distance_list) == len(stop_list) - 1), "Input arguments have wrong length!"

        self.stops = stop_list              # list of BusStop objects
        self.distances = distance_list      # list of number, which represents the distance between stations
        self.num = number                   # Route number: one of [1,2,3]
