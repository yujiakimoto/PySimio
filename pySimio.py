import numpy as np


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
    def __init__(self, route):

        assert(isinstance(route, Route)), "route must be a Route object"
        
        self.route = route
        self.next_stop_num = 1                             # bus starts at first stop, i.e. index 0
        self.next_stop = self.route[1]
        
        self.passengers = []                               # bus starts with nobody on it
        self.occupancy = 0
        self.num_seats = 25                                # default number of seats is 25
        self.standing_cap = 10                             # default standing capacity is 10
        self.max_cap = self.num_seats + self.standing_cap  # default total capacity is 25+10=35
        
        self.distance = 0                                  # distance travelled by this bus
        # TODO: other relevant performance metrics?

    def goes_to(self, stop):
        """Returns True if this bus goes to the specified stop (in logical fashion, i.e. it did not just
        leave it) and False otherwise"""

        assert(isinstance(stop, BusStop)), "stop must be a BusStop"

        in_route = stop in self.route.stops
        if not in_route:
            return False
        else:
            # TODO: implement better decision logic of whether or not to board a given bus
            return True

    def arrive(self, stop, time):

        assert(isinstance(stop, BusStop)), "must arrive at a BusStop"
        self.next_stop_num = self.next_stop_num % len(self.route.stops) + 1    # update next stop number
        self.next_stop = self.route.stops[self.next_stop_num]

        # if current stop is destination, passenger will get off
        for person in self.passengers:
            if person.destination == stop:
                self.passengers.remove(person)
                self.occupancy -= 1

                person.state = 'arrived'

        # people waiting at bus stop will get on if bus goes to desired destination and there is space on the bus
        boarding_time = time
        for person in stop.people_waiting:
            if self.goes_to(person.destination) and self.occupancy < self.max_cap:
                self.passengers.append(person)
                self.occupancy += 1

                stop.people_waiting.remove(person)
                stop.num_waiting -= 1

                boarding_time += np.random.triangular(0, 1/60, 5/60)    # boarding times have triangular distribution
                person.state = 'standing'
                person.waiting_time = boarding_time - person.start_time

        # first 25 passengers will sit down (or all, if less than 25 people on bus)
        for i in range(min(self.occupancy, 25)):
            self.passengers[i].state = 'sitting'

        # TODO: buses can wait at stops for longer if necessary

        # when done boarding, depart from bus stop
        self.depart(boarding_time)

    def depart(self, time):
        """Models a bus driving from one stop to another"""

        distance_travelled = self.route.distances[self.next_stop_num - 1]

        self.distance += distance_travelled                # add distance travelled by bus

        if distance_travelled < 2:
            driving_time = (distance_travelled/20) * 60    # average speed of 20km/hr, convert to minutes
        else:
            driving_time = np.random.uniform(5, 7)         # average speed of 20km/hr, +/-1 min variability

        self.arrive(self.next_stop, time + driving_time)   # arrive at next bus stop


class BusStop:
    """ Models a bus stop somewhere in Ithaca.
    
    Attributes:
        name (str): Name of the bus stop.
        num_waiting (int): Number of people currently waiting at this bus stop.
    
    """
    def __init__(self, name):
        
        self.name = name            # name of bus stop
        self.num_waiting = 0        # bus stop starts with nobody waiting
        self.people_waiting = []    # list of people waiting at this stop; initially empty
        
    def arrival(self, person):
                
        self.num_waiting += 1
        self.people_waiting.append(person)
        
        
class Person:
    """ Models a person trying to get around Ithaca.
    
    Attributes:
        origin (BusStop): Where this person starts.
        destination (BusStop): Where this person is trying to get to.

        state (str): Describes state of person. One of 'waiting', 'sitting', 'standing', 'arrived'.
        start_time (float): Time at which person arrived at origin bus stop
        waiting_time (float): Time spent waiting at origin bus stop.
    
    """    
    def __init__(self, origin, destination, time):
        
        assert(isinstance(origin, BusStop)), "origin must be a BusStop"
        assert(isinstance(destination, BusStop)), "destination must be a BusStop"
        
        self.origin = origin               # origin bus stop
        self.destination = destination     # destination bus stop

        self.state = 'waiting'
        self.start_time = time             # time at which person started waiting
        self.waiting_time = 0              # time spent waiting at bus stop
        origin.arrival(self)


class Route:
    """ Models 1 of 3 bus routes around Ithaca.
    
    Attribtues:
        stopList (list): A list of BusStop objects representing all the stops on this route. Includes starting 
            stop as both the first and last element if the route is a loop (which they all are).
        distanceList (list): A list of floats representing the distances between each of the stops on the route.
            Length should be one less than the length of stopList.
        number (int): Route number as defined in writeup.
    
    """
    
    def __init__(self, stop_list, distance_list, number):
        
        assert(all(isinstance(stop, BusStop) for stop in stop_list)), "stopList must be a list of BusStop objects"
        assert (len(distance_list) == len(stop_list) - 1), "Input arguments have wrong length!"
        
        self.stops = stop_list
        self.distances = distance_list
        self.num = number

        # TODO: all buses should start at Depot, including those on Route 2
