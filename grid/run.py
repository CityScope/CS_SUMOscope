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
        self.netgenBinary = checkBinary('netgenerate')
        self.jtrrouterBinary = checkBinary('jtrrouter')
        self.sumoBinary = checkBinary('sumo')
        # [{ "id": [],"path": [],"timestamps":[]},{}]
        self.trips_list = []
        #
        self.current_dir = os.path.dirname(__file__)+"/"

        # # create flows
        # call([self.netgenBinary, '-c', 'data/grid.netgcfg'])
        # randomTrips.main(randomTrips.get_options([
        #     '--flows', '100',
        #     '-b', '0',
        #     '-e', '1',
        #     '-n', 'data/net.net.xml',
        #     '-o', 'data/flows.xml',
        #     '--jtrrouter',
        #     '--trip-attributes', 'departPos="random" departSpeed="max"']))

        # # create routes
        # call([self.jtrrouterBinary, '-c', 'data/grid.jtrrcfg'])

    def existing_car_bool(self, veh_id):
        return any(i['id'] == [str(veh_id)] for i in self.trips_list)

    def traciRun(self):
        '''run'''
        # ! https://sumo.dlr.de/docs/Simulation/Output.html

        traci.start([self.sumoBinary, "-c", self.current_dir +
                     'data/grid.sumocfg', "-v"])

        # while traci.simulation.getMinExpectedNumber() > 0:
        step = 0
        while step < 500:
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
