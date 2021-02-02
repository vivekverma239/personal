const savitzkyGolay = require("ml-savitzky-golay");

const FILTER = [1, -8, 0, 8, -1];

class SkippingCounter {
  constructor(props) {
    this.onChangeCallback = props.onChangeCallback;
    this.increaseCount = props.increaseCount;
    this.count = 0;
    this.records = [];
    this.xplotRecords = [];
    this.yplotRecords = [];
    this.totalPoses = 0;
    this.yDerivative = -1;
    this.xPositions = {
      nose: [],
      leftEye: [],
      rightEye: [],
      leftEar: [],
      rightEar: [],
      leftShoulder: [],
      rightShoulder: [],
      leftElbow: [],
      rightElbow: [],
      leftWrist: [],
      rightWrist: [],
      leftHip: [],
      rightHip: [],
      leftKnee: [],
      rightKnee: [],
      leftAnkle: [],
      rightAnkle: [],
    };
    this.yPositions = {
      nose: [],
      leftEye: [],
      rightEye: [],
      leftEar: [],
      rightEar: [],
      leftShoulder: [],
      rightShoulder: [],
      leftElbow: [],
      rightElbow: [],
      leftWrist: [],
      rightWrist: [],
      leftHip: [],
      rightHip: [],
      leftKnee: [],
      rightKnee: [],
      leftAnkle: [],
      rightAnkle: [],
    };
    console.log("In constructor");
    setInterval(() => this.syncPositions(), 3000);
  }

  syncPositions = () => {
    console.log("Synicing");
    this.onChangeCallback(
      JSON.parse(JSON.stringify(this.xplotRecords)),
      JSON.parse(JSON.stringify(this.yplotRecords))
    );
  };

  computeDerivativeY = () => {
    if (this.totalPoses > 5) {
      var i = -5;
      var derivative = {};
      while (i < 0) {
        for (var key of Object.keys(this.yPositions)) {
          derivative[[key]] =
            (derivative[[key]] || 0) +
            FILTER[i + 5] * this.yPositions[[key]][this.totalPoses + i];
        }
        i += 1;
      }
      var overallDerivative = 0;
      for (var key of Object.keys(derivative)) {
        overallDerivative += derivative[[key]];
      }
      overallDerivative /= 12;
      var z = overallDerivative * this.yDerivative;
      if (z < 0 && Math.abs(z) > 20) {
        this.yDerivative = overallDerivative;
        this.count += 1;
        this.increaseCount(Math.round(this.count / 2));
      }
    }
  };

  insertPose = (pose) => {
    if (pose.score > 0.5) {
      //   console.log("Score", pose.score);
      this.records.push(pose);
      this.totalPoses += 1;
      var keypoints = pose.keypoints;
      var positions = {};
      for (var item of keypoints) {
        this.xPositions[[item.part]].push(item.position.x);
        positions[[item.part]] = item.position.x;
      }
      positions["name"] = this.totalPoses;
      this.xplotRecords.push(positions);
      var positions = {};
      for (var item of keypoints) {
        this.yPositions[[item.part]].push(item.position.y);
        positions[[item.part]] = item.position.y;
      }
      positions["name"] = this.totalPoses;
      this.yplotRecords.push(positions);
      this.computeDerivativeY();
      //   this.syncPositions();
    }
  };

  clearData = () => {
    this.counts = 0;
    this.records = [];
    this.totalPoses = 0;
    this.xPositions = {
      nose: [],
      leftEye: [],
      rightEye: [],
      leftEar: [],
      rightEar: [],
      leftShoulder: [],
      rightShoulder: [],
      leftElbow: [],
      rightElbow: [],
      leftWrist: [],
      rightWrist: [],
      leftHip: [],
      rightHip: [],
      leftKnee: [],
      rightKnee: [],
      leftAnkle: [],
      rightAnkle: [],
    };
    this.yPositions = {
      nose: [],
      leftEye: [],
      rightEye: [],
      leftEar: [],
      rightEar: [],
      leftShoulder: [],
      rightShoulder: [],
      leftElbow: [],
      rightElbow: [],
      leftWrist: [],
      rightWrist: [],
      leftHip: [],
      rightHip: [],
      leftKnee: [],
      rightKnee: [],
      leftAnkle: [],
      rightAnkle: [],
    };
  };
}

export default SkippingCounter;
