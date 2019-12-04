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
        self.current_dir = os.path.dirname(__file__)+"/"

    def create_network(self):
        '''
        <location netOffset="-565120.67,-5930830.85" convBoundary="0.00,0.00,4010.49,3225.15"
        origBoundary="9.913090,53.450981,10.085598,53.551251"
        projParameter="+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"/>
        '''
        self.netgenBinary = checkBinary('netgenerate')
        call([self.netgenBinary, '-c', 'data/grid.netgcfg'])

    def create_flows(self):
        ''' create flows'''
        self.jtrrouterBinary = checkBinary('jtrrouter')
        call([self.jtrrouterBinary, '-c', 'data/grid.jtrrcfg'])

    def create_trips(self):
        # create random trips
        randomTrips.main(randomTrips.get_options([
            '--flows', '200',
            '-b', '0',
            '-e', '1',
            '-n', 'data/net.net.xml',
            '-o', 'data/flows.xml',
            '--jtrrouter',
            '--trip-attributes', 'departPos="random" departSpeed="max"']))

    def existing_car_bool(self, veh_id):
        return any(i['id'] == [str(veh_id)] for i in self.trips_list)

    def traciRun(self):
        self.sumoBinary = checkBinary('sumo')

        '''run'''
        # ! https://sumo.dlr.de/docs/Simulation/Output.html

        traci.start([self.sumoBinary, "-c", self.current_dir +
                     'data/grid.sumocfg', "-v"])

        # while traci.simulation.getMinExpectedNumber() > 0:
        step = 0
        while step < 5000:
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


if __name__ == "__main__":
    sumo = SUMOScope()
    sumo.traciRun()
