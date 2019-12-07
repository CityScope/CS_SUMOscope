# SUMOScope

### SUMO mobility simulation for CityScope

SUMOScope is a CityScope module for a near real-time traffic simulation of custom demand modeled over OSM or arbitrary networks.

SUMOScope uses [SUMO Traci](https://sumo.dlr.de/) interface to export simulation results as JSON and ship them on demand to cityIO. A visualization example of results is included in `deckgl` folder.

## Setup

### Install SUMO for macOS

https://sumo.dlr.de/wiki/Installing/MacOS_Build

### Install Xquartz

to run SUMO GUI & Netedit:

https://www.xquartz.org/

### Enable TRACI in Python

add this to `‎⁨~/..bash_profile` to expose SUMO libs to python
NOTE: check your SUMO version

```
# sets sumo home path
export SUMO_HOME="/usr/local/Cellar/sumo/__[sumo installed version]__/share/sumo"
export PATH="$SUMO_HOME/bin:$PATH"
export PATH="$SUMO_HOME/tools:$PATH"
```

### DeckGL example

instal via `npm i`
run `npm start`

## Usage

`SUMOscope` exposes several functionalities:

-   `SUMOscope.create_random_network()` create random network
-   `SUMOscope.osm_to_sumo_net()` Convert OSM network to SUMO network
-   `SUMOscope.create_random_demand()` Create random demand for network
-   `SUMOscope.create_routes()` Create random trips from demand
-   `SUMOscope.export_sim_to_json()` Export vehicle locations to `results.json`
