# SUMOScope: SUMO for CityScope

A CityScope module for streaming traffic simulations to cityIO during SUMO runtime.
`osm` folder contains sample SUMO network for the Grasbrook area in Hamburg with pre-generated traffic.

## Install SUMO for macOS

https://sumo.dlr.de/wiki/Installing/MacOS_Build

## Install Xquartz for SUMO GUI

https://www.xquartz.org/

## Enable TRACI in Python

- add this to `‎⁨~/..bash_profile` to expose SUMO libs to python
  NOTE: check your SUMO version

```
# sets sumo home path
export SUMO_HOME="/usr/local/Cellar/sumo/__1.2.0__[version]/share/sumo"
export PATH="$SUMO_HOME/bin:$PATH"
export PATH="$SUMO_HOME/tools:$PATH"
```

## Create random trips for network

`$ python3 randomTrips.py -n ___NETWORK_NAME___.net.xml -e 100 -l`

## Export vehicle locations to cityIO

`$ python SUMOScope.py`

change cityIO endpoint to your exciting one. This module does not create new cityIO table instances.

## Optional: export vehicles position post-simulation

- https://sumo.dlr.de/wiki/Simulation/Output/FCDOutput

- run sumo with this option to export the overall paths
  `sumo -c osm/osm.sumocfg --fcd-output "fcd.xml"`
