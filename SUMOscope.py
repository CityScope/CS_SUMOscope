from __future__ import absolute_import
from __future__ import print_function
import json
import os
from subprocess import call
import sys
import time
import requests

try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary  # noqa

except ImportError:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
from sumolib import net  # noqa
import traci  # noqa
import randomTrips  # noqa


class SUMOScope():
    '''sumo'''

    def __init__(self):
        self.network_filename = 'detroit'
        self.osm_path = 'data/osm/'+self.network_filename+'.map.osm'
        self.trips_list = []
        self.scatterplot_list = []
        # max sim time
        self.max_sim_length = 500
        # how much time did the sim took
        self.actual_sim_length = 0
        self.vehicles_count = 300
        self.current_dir = os.path.dirname(__file__)+"/"

    def osm_to_sumo_net(self):
        self.netconvertBinary = checkBinary('netconvert')
        call([self.netconvertBinary, '--osm-files',
              self.osm_path,
              '-o',
              'data/network/net.net.xml',
              '--geometry.remove',
              '--ramps.guess',
              '--keep-edges.by-vclass', 'private, public_transport, public_emergency, public_authority, public_army, vip',
              '--junctions.join',
              '--tls.guess-signals',
              '--tls.discard-simple',
              '--tls.join'])

    def create_random_demand(self):
        ''' create random flows'''
        randomTrips.main(randomTrips.get_options([
            '--flows', str(self.vehicles_count),
            '-b', '0',
            '-e', '1',
            '-n', 'data/network/net.net.xml',
            '-o', 'data/demand/demand.xml',
            '--jtrrouter',
            '--trip-attributes', 'departPos="random" departSpeed="max"']))

    def create_routes(self):
        '''create routes'''
        self.jtrrouterBinary = checkBinary('jtrrouter')
        call([self.jtrrouterBinary, '-c',
              'data/routes/routes_config.jtrrcfg'])

    def existing_car_bool(self, veh_id):
        '''returns if a car is in list already'''
        return any(i['id'] == [str(veh_id)] for i in self.trips_list)

    def export_sim_to_json(self):
        '''compute sim results from traci'''
        self.sumoBinary = checkBinary('sumo')
        traci.start([self.sumoBinary, "-c", self.current_dir +
                     'data/sumo.sumocfg', "-v"])
        #
        self.run_simulation_loop()

        speed_results = {'meta':
                         {'sim_length': self.actual_sim_length,
                          'vehicles_count': self.vehicles_count},
                         'scatterplot': self.scatterplot_list}

        trips_results = self.trips_list

        with open(self.current_dir+"trips.json", 'w') as outfile:
            json.dump(trips_results, outfile)

        with open(self.current_dir+"speed.json", 'w') as outfile:
            json.dump(speed_results, outfile)

        traci.close()
        sys.stdout.flush()

    def run_simulation_loop(self):
        '''compute'''
        print('\nrun_simulation_loop...\n')
        step = 0

        while step < self.max_sim_length and traci.simulation.getMinExpectedNumber() > 0:
            print('sim step:', step)
            traci.simulationStep()

            for veh_id in traci.vehicle.getIDList():
                x, y = traci.vehicle.getPosition(veh_id)
                lon, lat = traci.simulation.convertGeo(x, y)
                car_loc = [lon, lat]
                speed = traci.vehicle.getSpeed(veh_id)
                max_speed = traci.vehicle.getMaxSpeedLat(veh_id)

                # check if behicle is in list alreay
                # if so, add locations and timestamps
                if self.existing_car_bool(veh_id):
                    for i in self.trips_list:
                        if i['id'] == [str(veh_id)]:
                            i['path'].append(car_loc)
                            i['timestamps'].append(step)
                # else create new vehicle
                else:
                    self.trips_list.append(
                        {"id": [veh_id], "path": [car_loc], "timestamps": [step]})

                self.scatterplot_list.append({
                    'name': str(veh_id), 'coordinates': car_loc, 'speed': speed, 'maxSpeed': max_speed})

            step += 1
            self.actual_sim_length = step

        def control_vehicle_behavior(vehicle, speed, max_speed, new_taget):
            '''
            control the behavior of each vehicle
            '''
            try:
                # some time parameter for now
                if speed/max_speed < 0.5 and self.actual_sim_length > 100:
                    traci.vehicle.changeTarget(vehicle, new_taget)
                elif self.actual_sim_length > self.max_sim_length/2:
                    traci.vehicle.changeTarget(vehicle, new_taget)
                return vehicle
            except traci.TraCIException:
                pass


if __name__ == "__main__":
    # init the class
    sumo = SUMOScope()

    # # make network
    # sumo.osm_to_sumo_net()

    # # make random trips
    sumo.create_random_demand()

    # # make routes
    sumo.create_routes()

    # # run and save to json
    sumo.export_sim_to_json()
