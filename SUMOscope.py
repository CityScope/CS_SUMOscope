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
        self.osm_path = 'data/paris.map.osm'
        self.trips_list = []
        self.scatterplot_list = []
        # max sim time
        self.max_sim_length = 100
        # how much time did the sim took
        self.actual_sim_length = 0
        self.vehicles_count = 10
        self.current_dir = os.path.dirname(__file__)+"/"
        self.cityio_table = 'virtual_table'
        self.cityio_endpoint = 'https://cityio.media.mit.edu/api/table/update/' + \
            self.cityio_table+'/sumo/'

    def stream_sumo(self, data_to_stream):
        '''streaming method to cityio'''
        while True:
            time.sleep(1)
            # defining cityio api-endpoint
            json_data_struct = {"objects": json.dumps(data_to_stream)}
            request = requests.post(
                self.cityio_endpoint, json=json_data_struct)
            # extracting response text
            cityio_response = request.text
            print("response:", cityio_response)

    def create_random_network(self):
        self.netgenBinary = checkBinary('netgenerate')
        call([self.netgenBinary, '-c', 'data/create_network.netgcfg'])

    def osm_to_sumo_net(self):
        self.netconvertBinary = checkBinary('netconvert')
        call([self.netconvertBinary, '--osm-files',
              self.osm_path,
              '-o',
              'data/net.net.xml',
              '--geometry.remove',
              '--ramps.guess',
              '--keep-edges.by-vclass', 'private',
              '--junctions.join',
              '--tls.guess-signals',
              '--tls.discard-simple',
              '--tls.join'])

    def create_random_flows(self):
        ''' create random flows'''
        randomTrips.main(randomTrips.get_options([
            '--flows', str(self.vehicles_count),
            '-b', '0',
            '-e', '1',
            '-n', 'data/net.net.xml',
            '-o', 'data/trips.xml',
            '--jtrrouter',
            '--trip-attributes', 'departPos="random" departSpeed="max"']))

    def create_routes(self):
        '''create routes'''
        self.jtrrouterBinary = checkBinary('jtrrouter')
        call([self.jtrrouterBinary, '-c',
              'data/routes_config.jtrrcfg'])

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

        json_results = {'meta':
                        {'sim_length': self.actual_sim_length,
                         'vehicles_count': self.vehicles_count},
                        'trips': self.trips_list,
                        'scatterplot': self.scatterplot_list}
        #
        with open(self.current_dir+"results.json", 'w') as outfile:
            json.dump(json_results, outfile)

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

                # try:
                #     # some time parameter for now
                #     if self.actual_sim_length > self.max_sim_length/2:
                #         traci.vehicle.changeTarget(veh_id, '27286674')
                # except traci.TraCIException:
                #     print("An exception occurred")

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


if __name__ == "__main__":

    sumo = SUMOScope()

    # make network
    # sumo.create_random_network()
    # sumo.osm_to_sumo_net()

    # make random trips
    sumo.create_random_flows()

    # make routes
    sumo.create_routes()

    # run and save to json
    sumo.export_sim_to_json()
