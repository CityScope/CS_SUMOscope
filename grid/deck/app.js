/* global window */
import React, { Component } from "react";
import { render } from "react-dom";
import { StaticMap } from "react-map-gl";
import DeckGL from "@deck.gl/react";
import { TripsLayer } from "@deck.gl/geo-layers";
let sumo = require("./results.json");

// Set your mapbox token here
const MAPBOX_TOKEN =
    "pk.eyJ1IjoicmVsbm94IiwiYSI6ImNqd2VwOTNtYjExaHkzeXBzYm1xc3E3dzQifQ.X8r8nj4-baZXSsFgctQMsg"; // eslint-disable-line

const INITIAL_VIEW_STATE = {
    longitude: 9.994464922797663,
    latitude: 53.527631743094176,
    zoom: 13,
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
        this._animate();
    }

    componentWillUnmount() {
        if (this._animationFrame) {
            window.cancelAnimationFrame(this._animationFrame);
        }
    }

    _animate() {
        const {
            loopLength = 500, // unit corresponds to the timestamp in source data
            animationSpeed = 10 // unit time per second
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
        const { trips = sumo, trailLength = 10 } = this.props;

        return [
            new TripsLayer({
                id: "trips",
                data: trips,
                getPath: d => d.path,
                getTimestamps: d => d.timestamps,
                getColor: d => {
                    let idInt = parseInt(d.id, 10);
                    let col = (idInt / 100) * 255;
                    return [col, 0, 255 - col];
                },
                opacity: 0.8,
                widthMinPixels: 3,
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
