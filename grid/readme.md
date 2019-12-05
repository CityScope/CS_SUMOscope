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
