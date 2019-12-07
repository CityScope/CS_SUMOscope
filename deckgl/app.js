/* global window */
import React, { Component } from "react";
import { render } from "react-dom";
import { StaticMap } from "react-map-gl";
import DeckGL from "@deck.gl/react";
import { TripsLayer } from "@deck.gl/geo-layers";
import { ScatterplotLayer } from "@deck.gl/layers";
let sumoData = require("../results.json");

export default class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            time: 0,
            opacity: 0.2,
            simSpeed: 100
        };

        this.vehicles_count = sumoData.meta.vehicles_count;
        // Set your mapbox token here
        this.MAPBOX_TOKEN =
            "pk.eyJ1IjoicmVsbm94IiwiYSI6ImNqd2VwOTNtYjExaHkzeXBzYm1xc3E3dzQifQ.X8r8nj4-baZXSsFgctQMsg"; // eslint-disable-line

        this.INITIAL_VIEW_STATE = {
            longitude: sumoData.trips[0].path[0][0],
            latitude: sumoData.trips[0].path[0][1],
            zoom: 14,
            pitch: 45,
            bearing: 0
        };

        this.randomColorsArray = this.randomColors(this.vehicles_count);
        console.log(this.randomColorsArray);
    }

    randomColors(number) {
        let colArr = [];
        for (let i = 0; i < number; i++) {
            let r = Math.floor(Math.random() * 255);
            let g = Math.floor(Math.random() * 255);
            let b = Math.floor(Math.random() * 255);
            colArr[i] = [r, g, b];
        }
        return colArr;
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
            loopLength = sumoData.meta.sim_length,
            animationSpeed = this.state.simSpeed
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

    _controlOpacity(slider) {
        this.setState({ opacity: slider.target.value });
    }

    _controlSimSpeed(slider) {
        this.setState({ simSpeed: slider.target.value });
    }

    _renderLayers() {
        const {
            trips = sumoData.trips,
            scatter = sumoData.scatterplot,
            trailLength = 50
        } = this.props;

        return [
            new TripsLayer({
                id: "trips",
                data: trips,
                getPath: d => {
                    // const noisePath =
                    //     Math.random() < 0.5
                    //         ? Math.random() * 0.00005
                    //         : Math.random() * -0.00005;

                    // for (let i in d.path) {
                    //     d.path[i][0] = d.path[i][0] + noisePath;
                    //     d.path[i][1] = d.path[i][1] + noisePath;
                    // }

                    return d.path;
                },
                getTimestamps: d => d.timestamps,
                getColor: d => {
                    let idInt = parseInt(d.id, 10);
                    return this.randomColorsArray[idInt];
                },
                opacity: 0.7,
                widthMinPixels: 1,
                rounded: true,
                trailLength,
                currentTime: this.state.time,

                shadowEnabled: false
            }),
            new ScatterplotLayer({
                id: "scatterplot-layer",
                data: scatter,
                opacity: this.state.opacity,
                stroked: true,
                filled: false,
                radiusScale: 1,
                radiusMinPixels: 1,
                radiusMaxPixels: 5,
                lineWidthMinPixels: 1,
                getPosition: d => d.coordinates,
                getRadius: d => 1 / d.speed,
                getLineColor: d => {
                    let speedRatio = d.speed / d.maxSpeed;
                    let r,
                        g,
                        b = 0;
                    if (speedRatio < 0.5) {
                        r = 255;
                        g = Math.round(51 * speedRatio);
                    } else {
                        g = 255;
                        r = Math.round(510 - 51 * speedRatio);
                    }
                    return [r, g, b];
                }
            })
        ];
    }

    render() {
        const {
            time = this.state.time,
            viewState,
            mapStyle = "mapbox://styles/relnox/cjl58dpkq2jjp2rmzyrdvfsds"
        } = this.props;

        return (
            <div>
                <div style={{ position: "fixed", zIndex: 1, color: "white" }}>
                    <h2>sim step: {Math.floor(time)}</h2>
                    <input
                        id="inputSlider"
                        type="range"
                        min="0"
                        max="0.1"
                        defaultValue={this.state.opacity}
                        onChange={this._controlOpacity.bind(this)}
                        step="0.01"
                    />
                    <input
                        id="inputSlider"
                        type="range"
                        min="0"
                        max="100"
                        defaultValue={this.state.simSpeed}
                        onChange={this._controlSimSpeed.bind(this)}
                        step="1"
                    />
                </div>
                <DeckGL
                    layers={this._renderLayers()}
                    initialViewState={this.INITIAL_VIEW_STATE}
                    viewState={viewState}
                    controller={true}
                >
                    <StaticMap
                        reuseMaps
                        mapStyle={mapStyle}
                        preventStyleDiffing={true}
                        mapboxApiAccessToken={this.MAPBOX_TOKEN}
                    />
                </DeckGL>
            </div>
        );
    }
}

export function renderToDOM(container) {
    render(<App />, container);
}
