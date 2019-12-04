/* global window */
import React, { Component } from "react";
import { render } from "react-dom";
import { StaticMap } from "react-map-gl";
import DeckGL from "@deck.gl/react";
import { TripsLayer } from "@deck.gl/geo-layers";
let sumo = require("../results.json");

// Set your mapbox token here
const MAPBOX_TOKEN =
    "pk.eyJ1IjoicmVsbm94IiwiYSI6ImNqd2VwOTNtYjExaHkzeXBzYm1xc3E3dzQifQ.X8r8nj4-baZXSsFgctQMsg"; // eslint-disable-line

const INITIAL_VIEW_STATE = {
    longitude: sumo[0].path[0][0],
    latitude: sumo[0].path[0][1],
    zoom: 14,
    pitch: 45,
    bearing: 0
};

export default class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            time: 0
        };
    }

    componentDidMount() {
        document
            .getElementById("deckgl-wrapper")
            .addEventListener("contextmenu", evt => evt.preventDefault());
        this._animate();
    }

    componentWillUnmount() {
        if (this._animationFrame) {
            window.cancelAnimationFrame(this._animationFrame);
        }
    }

    _animate() {
        const {
            loopLength = 1000, // unit corresponds to the timestamp in source data
            animationSpeed = 50 // unit time per second
        } = this.props;
        const timestamp = Date.now() / 1000;
        const loopTime = loopLength / animationSpeed;

        this.setState({
            time: ((timestamp % loopTime) / loopTime) * loopLength
        });
        this._animationFrame = window.requestAnimationFrame(
            this._animate.bind(this)
        );
    }

    _renderLayers() {
        const { trips = sumo, trailLength = 100 } = this.props;

        return [
            new TripsLayer({
                id: "trips",
                data: trips,
                getPath: d => {
                    const noisePath =
                        Math.random() < 0.5
                            ? Math.random() * 0.00005
                            : Math.random() * -0.00005;

                    for (let i in d.path) {
                        d.path[i][0] = d.path[i][0] + noisePath;
                        d.path[i][1] = d.path[i][1] + noisePath;
                    }

                    return d.path;
                },

                // d =>
                // d.path,
                getTimestamps: d => d.timestamps,
                getColor: d => {
                    let idInt = parseInt(d.id, 10);
                    let col = (idInt / 100) * 255;
                    return [col, 0, 255];
                },
                opacity: 0.7,
                widthMinPixels: 1,
                rounded: true,
                trailLength,
                currentTime: this.state.time,

                shadowEnabled: false
            })
        ];
    }

    render() {
        const {
            viewState,
            mapStyle = "mapbox://styles/relnox/cjl58dpkq2jjp2rmzyrdvfsds"
        } = this.props;

        return (
            <DeckGL
                layers={this._renderLayers()}
                initialViewState={INITIAL_VIEW_STATE}
                viewState={viewState}
                controller={true}
            >
                <StaticMap
                    reuseMaps
                    mapStyle={mapStyle}
                    preventStyleDiffing={true}
                    mapboxApiAccessToken={MAPBOX_TOKEN}
                />
            </DeckGL>
        );
    }
}

export function renderToDOM(container) {
    render(<App />, container);
}
