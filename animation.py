import sys
import pandas as pd
import numpy as np
import pygame
import datetime
from pySimio import *


def create_map(buses_per_route=(7, 0, 0), arrival_data='data/Test.xlsx', name=None):

    # create BusStop objects
    depot = BusStop('TDOG Depot')
    weg_east = BusStop('Wegmans-Eastbound')
    weg_west = BusStop('Wegmans-Westbound')
    com_east = BusStop('Commons-Eastbound')
    com_west = BusStop('Commons-Westbound')
    ctown = BusStop('Collegetown')

    # feed arrival rate data to each bus stop
    rates = pd.read_excel(arrival_data)
    weg_east.add_data({com_east: rates['Weg to Com'].values, ctown: rates['Weg to Ctown'].values})
    com_east.add_data({ctown: rates['Com to Ctown'].values})
    com_west.add_data({weg_west: rates['Com to Weg'].values})
    ctown.add_data({com_west: rates['Ctown to Com'].values, weg_west: rates['Ctown to Weg'].values})

    # create a Route object for each of the 3 routes
    route1 = Route([depot, weg_east, com_east, ctown, com_west, weg_west, depot], [0.5, 2, 2, 2, 2, 0.5], 1)
    route2 = Route([com_east, ctown, com_west, com_east], [2, 2, 0.3], 2)
    route3 = Route([depot, weg_east, com_east, com_west, weg_west, depot], [0.5, 2, 2, 2, 0.5], 3)

    # create Bus objects
    assert(sum(buses_per_route) == 7), "There must be 7 buses total"
    bus_list = []
    bus_num = 1
    for i, num in enumerate(buses_per_route):
        route_num = i + 1
        for j in range(num):
            bus_list.append(Bus('Bus ' + str(bus_num), eval('route' + str(route_num))))
            bus_num += 1

    return Map([route1, route2, route3], bus_list,
               {'TDOG Depot': depot, 'Wegmans-Eastbound': weg_east, 'Wegmans-Westbound': weg_west,
                'Commons-Eastbound': com_east, 'Commons-Westbound': com_west, 'Collegetown': ctown}, name = name)


def make_button(picture, coords, surface):
    image = pygame.image.load(picture)
    image_rect = image.get_rect()
    image_rect.center = coords
    surface.blit(image, image_rect)
    return image, image_rect


def animate(map, time):

    pygame.init()
    size = width, height = 1080, 720
    screen = pygame.display.set_mode(size)

    font_small = pygame.font.SysFont("Helvetica", 12)
    font_med = pygame.font.SysFont("Helvetica", 15)

    button_size = 32
    margin = 10
    start = make_button('images/start.png', (width - 0.5*button_size - margin, 0.5*button_size + margin), screen)
    restart = make_button('images/restart.png', (width - 0.5*button_size - margin, 1.5*button_size + 2*margin), screen)
    edit = make_button('images/settings.png', (width - 0.5*button_size - margin, 2.5*button_size + 3*margin), screen)
    close = make_button('images/stop.png', (width - 0.5*button_size - margin, 3.5*button_size + 4*margin), screen)

    stop_coordinates = {'TDOG Depot': (0.1*width, 0.5*height),
                        'Wegmans-Eastbound': (0.3*width, 0.3*height),
                        'Wegmans-Westbound': (0.3*width, 0.7*height),
                        'Commons-Eastbound': (0.55*width, 0.3*height),
                        'Commons-Westbound': (0.55*width, 0.7*height),
                        'Collegetown': (0.8*width, 0.5*height)}

    bus_stop_icons = {}
    images = {'TDOG Depot': 'images/bus_stop_red.png',
              'Wegmans-Eastbound': 'images/bus_stop_green.png',
              'Wegmans-Westbound': 'images/bus_stop_green.png',
              'Commons-Eastbound': 'images/bus_stop_blue.png',
              'Commons-Westbound': 'images/bus_stop_blue.png',
              'Collegetown': 'images/bus_stop_orange.png'}
    for bus_stop in map.bus_stops.values():
        bus_stop_icons[bus_stop.name] = make_button(images[bus_stop.name], stop_coordinates[bus_stop.name], screen)
        label = font_small.render(bus_stop.name, 1, (255, 255, 255))
        screen.blit(label, (stop_coordinates[bus_stop.name][0] - 20, stop_coordinates[bus_stop.name][1] + 30))

    clock = font_med.render('Time: ' + str(datetime.time(6, 0))[:5], 1, (255, 255, 255))
    screen.blit(clock, (990, 690))

    while True:
        for event in pygame.event.get():
            # exit simulation
            if event.type == pygame.QUIT:
                sys.exit()
            # start simulation
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = pygame.mouse.get_pos()
                if start[1].collidepoint(mouse):
                    # TODO: disable start button after clicking?
                    print('Start')
                    map.simulate(time, debug=False, animate=True, surface=screen, coordinates=stop_coordinates)
                if restart[1].collidepoint(mouse):
                    print('Reset')
                    map.reset()
                if close[1].collidepoint(mouse):
                    print('Exit')
                    sys.exit()

        pygame.display.update()

if __name__ == "__main__":

    ithaca = create_map(buses_per_route=(7, 0, 0))
    animate(ithaca, 120)
