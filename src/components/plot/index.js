import Plot from "react-plotly.js";
import React, { PureComponent } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

function getRandomColor() {
  var letters = "0123456789ABCDEF";
  var color = "#";
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

const UNIQUE_FIELDS = [
  "nose",
  "leftEye",
  "rightEye",
  "leftEar",
  "rightEar",
  "leftShoulder",
  "rightShoulder",
  "leftElbow",
  "rightElbow",
  "leftWrist",
  "rightWrist",
  "leftHip",
  "rightHip",
  "leftKnee",
  "rightKnee",
  "leftAnkle",
  "rightAnkle",
];

const COLOR_MAP = UNIQUE_FIELDS.map((item) => getRandomColor());
class SteamPlot extends React.Component {
  // Get unique data values
  constructor() {
    super();

    this.state = { data: [] };
  }

  componentDidUpdate() {
    if (
      JSON.stringify(this.state.data) !==
      JSON.stringify(this.props.streamValues)
    ) {
      this.setState({
        data: JSON.parse(JSON.stringify(this.props.streamValues)),
      });
    }
  }

  //   updateP() {
  //     setInterval(() => {
  //       var temp = {};
  //       for (var key of UNIQUE_FIELDS) {
  //         temp[key] = this.state.data.length;
  //       }
  //       temp["name"] = this.state.data.length;
  //       this.setState({ data: [...this.state.data, temp] });
  //     }, 500);
  //   }

  render() {
    console.log("Rendering");
    console.log(this.props.streamValues);
    return (
      <LineChart
        width={400}
        height={400}
        data={this.props.streamValues}
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
        syncId="anyId"
      >
        <XAxis dataKey="name" type="number" domain={["auto", "auto"]} />
        <YAxis />
        <Tooltip />
        <CartesianGrid stroke="#f5f5f5" />
        {UNIQUE_FIELDS.map((lineName) => (
          <Line
            type="monotone"
            dataKey={lineName}
            stroke={COLOR_MAP[[lineName]]}
            yAxisId={0}
          />
        ))}
      </LineChart>
    );
  }
}

export default SteamPlot;
