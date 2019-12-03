from __future__ import absolute_import
from __future__ import print_function
import json
import os
import sys

if 'SUMO_HOME' in os.environ:
    TOOLS = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(TOOLS)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary  # noqa
from sumolib import net  # noqa
import traci  # noqa


class SUMOScope():
    '''sumo'''

    def __init__(self):
        self.car_list = []
        self.check_sumo = checkBinary('sumo')
        self.current_dir = os.path.dirname(__file__)+"/"

    def traciRun(self):
        '''run'''
        traci.start([self.check_sumo, "-c", self.current_dir +
                     "data/sumolympics.sumocfg", "-v"])
        print('\n', traci.route.getIDList(), '\n')
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            for veh_id in traci.vehicle.getIDList():
                x, y = traci.vehicle.getPosition(veh_id)
                lon, lat = traci.simulation.convertGeo(x, y)
                self.car_list.append([veh_id, [lon, lat]])
        traci.close()
        sys.stdout.flush()

        with open(self.current_dir+"results.json", 'w') as outfile:
            json.dump(self.car_list, outfile)


if __name__ == "__main__":
    S = SUMOScope()
    S.traciRun()
