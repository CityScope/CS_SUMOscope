# SUMOScope: SUMO for CityScope

A CityScope module for streaming traffic simulations to cityIO during SUMO runtime.
`osm` folder contains sample SUMO network for the Grasbrook area in Hamburg with pre-generated traffic.

## Install SUMO for macOS

https://sumo.dlr.de/wiki/Installing/MacOS_Build

## Install Xquartz for SUMO GUI

https://www.xquartz.org/

## Enable TRACI in Python

-   add this to `‎⁨~/..bash_profile` to expose SUMO libs to python
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

-   https://sumo.dlr.de/wiki/Simulation/Output/FCDOutput

-   run sumo with this option to export the overall paths
    `sumo -c osm/osm.sumocfg --fcd-output "fcd.xml"`

### create net from osm

```
netconvert
--osm-files __FILE__.osm -o __FILE__.net.xml
--geometry.remove
--ramps.guess
--junctions.join
--tls.guess-signals
--tls.discard-simple
--tls.join
```

### Outputs

https://sumo.dlr.de/docs/Simulation/Output.html

### certain geo-ref in `.net`

```
    <
    location netOffset=
    "-565120.67,-5930830.85"
    convBoundary=
    "0.00,0.00,4010.49,3225.15"
    origBoundary=
    "9.913090,53.450981,10.085598,53.551251"
    projParameter=
    "+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
    />
```
