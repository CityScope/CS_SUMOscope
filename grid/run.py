from __future__ import absolute_import
from __future__ import print_function
import json
import os
from subprocess import call
import sys


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
        # [{ "id": [],"path": [],"timestamps":[]},{}]
        self.trips_list = []
        self.sim_length = 500
        self.vehicles_count = 100
        self.current_dir = os.path.dirname(__file__)+"/"

    def create_random_network(self):
        self.netgenBinary = checkBinary('netgenerate')
        call([self.netgenBinary, '-c', 'data/create_network.netgcfg'])

    def osm_to_sumo_net(self):
        self.netconvertBinary = checkBinary('netconvert')
        call([self.netconvertBinary, '--osm-files',
              'data/map.osm',
              '-o',
              'data/net.net.xml',
              '--geometry.remove',
              '--ramps.guess',
              '--junctions.join',
              '--tls.guess-signals',
              '--tls.discard-simple',
              '--tls.join'])

    def create_random_flows(self):
        ''' create random'''
        randomTrips.main(randomTrips.get_options([
            '--flows', str(self.vehicles_count),
            '-b', '0',
            '-e', '1',
            '-n', 'data/net.net.xml',
            '-o', 'data/trips.xml',
            '--jtrrouter',
            '--trip-attributes', 'departPos="random" departSpeed="max"']))

    def simple_random_trips(self):
        ''' create trips'''
        randomTrips.main(randomTrips.get_options([
            '-e', str(self.sim_length),
            '-n', 'data/net.net.xml',
            '-o', 'data/trips.xml']))

    def create_routes(self):
        '''create routes'''
        self.jtrrouterBinary = checkBinary('jtrrouter')
        call([self.jtrrouterBinary, '-c',
              'data/routes_config.jtrrcfg', '--repair', 'true'])

    def export_sim_to_json(self):
        '''run'''
        self.sumoBinary = checkBinary('sumo')

        traci.start([self.sumoBinary, "-c", self.current_dir +
                     'data/sumo.sumocfg', "-v"])

        # while traci.simulation.getMinExpectedNumber() > 0:
        step = 0
        while step < self.sim_length:
            print('sim step', step)
            traci.simulationStep()

            for veh_id in traci.vehicle.getIDList():
                x, y = traci.vehicle.getPosition(veh_id)
                lon, lat = traci.simulation.convertGeo(x, y)
                car_loc = [lon, lat]
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
                        {"id": [veh_id], "path": [
                            car_loc], "timestamps": [step]}
                    )

            step += 1
        traci.close()
        sys.stdout.flush()
#
        with open(self.current_dir+"results.json", 'w') as outfile:
            json.dump(self.trips_list, outfile)

    def existing_car_bool(self, veh_id):
        '''returns if a car is in list already'''
        return any(i['id'] == [str(veh_id)] for i in self.trips_list)


if __name__ == "__main__":

    sumo = SUMOScope()

    # make network
    # ? sumo.create_random_network()
    # ? sumo.osm_to_sumo_net()

    # make random trips
    sumo.create_random_flows()
    # ? sumo.create_random_trips()

    # make routes
    sumo.create_routes()

    # run and save to json
    sumo.export_sim_to_json()
