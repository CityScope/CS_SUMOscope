import optparse
import os
import sys
import requests
import time
import threading
import json

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    print(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
from sumolib import net  # noqa
import traci  # noqa

# edit this to fit your cityIO endpoint
CITYIO_ENDPOINT = "https://cityio.media.mit.edu/api/table/update/sumo2cityio/sumo/"


def get_options():
    # get user input options on CLI
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


def cityio_post_json():
    global vahicles_data_global_var
    while True:
        time.sleep(1)
        # defining cityio api-endpoint
        json_data_struct = {"objects": json.dumps(
            vahicles_data_global_var)}
        request = requests.post(CITYIO_ENDPOINT, json=json_data_struct)
        # extracting response text
        cityio_response = request.text
        print("response:", cityio_response)


# sets a temp data point
vahicles_data_global_var = 'Wait for it...'


def run():  # contains TraCI control loop

    # step counter
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        # sleep python for time

        traci.simulationStep()
        car_list = []

        for veh_id in traci.vehicle.getIDList():
            # veh_pos = traci.vehicle.getPosition(veh_id)
            x, y = traci.vehicle.getPosition(veh_id)
            lon, lat = traci.simulation.convertGeo(x, y)

            car_list.append([veh_id, [lon, lat]])
        print('simulation step:', step)
        step += 1
        global vahicles_data_global_var
        vahicles_data_global_var = car_list

    traci.close()
    sys.stdout.flush()


# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    traci_options = [sumoBinary, "-c", "osm/osm.sumocfg", "-v"]
    traci.start(traci_options)

    # n = net.readNet('osm/osm.net.xml')
    # # retrieve the coordinate of a node based on its ID
    # print(n)

    thread = threading.Thread(target=cityio_post_json)
    thread.start()
    run()
