import React from "react";

import { Grommet, Box, Grid, Tabs, Tab, Button } from "grommet";
import * as posenet from "@tensorflow-models/posenet";
import { useEffect, useState, useRef } from "react";
import ReactJson from "react-json-view";
import {
  drawPoint,
  drawKeypoints,
  drawSegment,
  drawBoundingBox,
  drawSkeleton,
} from "../../utils";
import SkippingCounter from "../skippingCounter";
import StreamPlot from "../plot";
import Stats from "stats.js";
import FPSStats from "react-fps-stats";

const noop = () => {};

const videoWidth = 600;
const videoHeight = 500;
var net = null;
function isAndroid() {
  return /Android/i.test(navigator.userAgent);
}

function isiOS() {
  return /iPhone|iPad|iPod/i.test(navigator.userAgent);
}

function isMobile() {
  return isAndroid() || isiOS();
}

async function loadModel(props) {
  const { video } = props;
  if (video) {
    net = await posenet.load({
      inputResolution: { width: videoWidth, height: videoHeight },
      architecture: "MobileNetV1",
      outputStride: 8,
      multiplier: 0.5,
    });
  } else {
    net = await posenet.load();
  }
}
const FileInput = ({ value, onChange = noop, ...rest }) => {
  const inputRef = useRef(null);

  const handleOpenFileInput = () => {
    inputRef.current.click();
  };

  return (
    <div>
      {value.length && (
        <div>Selected files: {value.map((f) => f.name).join(", ")}</div>
      )}
      <label>
        <input
          ref={inputRef}
          {...rest}
          style={{ display: "none" }}
          type="file"
          onChange={(e) => {
            onChange([...e.target.files]);
          }}
        />
        <Button primary label="Upload file" onClick={handleOpenFileInput} />
      </label>
    </div>
  );
};

const RunOnWebCam = (props) => {
  const vidRef = useRef(null);
  const canvasRef = useRef(null);
  const [video, updateVideo] = useState(null);
  const [streamValues, updateStreamValues] = useState({
    xValues: [],
    yValues: [],
  });
  const [finalCount, updateFinalCount] = useState(0);
  const counter = new SkippingCounter({
    onChangeCallback: (xValues, yValues) =>
      updateStreamValues({ xValues, yValues }),
    increaseCount: (count) => updateFinalCount(count),
  });

  useEffect(() => {
    loadModel({ video: true });
  }, []);

  const getPose = async (image) => {
    const temp = await net.estimateSinglePose(image, {
      flipHorizontal: true,
    });
    return temp;
  };

  useEffect(async () => {
    var video = await loadVideo();
    updateVideo(video);
  }, []);

  useEffect(() => {
    if (video) {
      poseDetectionFrame();
    }
  }, [video]);

  async function setupCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error(
        "Browser API navigator.mediaDevices.getUserMedia not available"
      );
    }

    const video = vidRef.current;
    video.width = videoWidth;
    video.height = videoHeight;

    const mobile = isMobile();
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: {
        facingMode: "user",
        width: mobile ? undefined : videoWidth,
        height: mobile ? undefined : videoHeight,
      },
    });
    video.srcObject = stream;

    return new Promise((resolve) => {
      video.onloadedmetadata = () => {
        resolve(video);
      };
    });
  }

  async function loadVideo() {
    const video = await setupCamera();
    video.play();
    return video;
  }

  const poseDetectionFrame = async () => {
    var pose = await getPose(video);
    var width = videoWidth;
    var height = videoHeight;
    canvasRef.current.width = width;
    canvasRef.current.height = height;
    var ctx = canvasRef.current.getContext("2d");
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(video, 0, 0, width, height);
    var { score, keypoints } = pose;
    drawKeypoints(keypoints, 0.1, ctx);
    counter.insertPose(pose);
    requestAnimationFrame(poseDetectionFrame);
  };

  return (
    <div style={{ margin: "20px 0px", width: "100%" }}>
      <div style={{ display: "flex" }}>
        <video ref={vidRef} style={{ display: "none" }} />
        <canvas ref={canvasRef} />
      </div>
      <div style={{ fontSize: "40px" }}>Final Count: {finalCount}</div>
    </div>
  );
};

const RunOnVideo = (props) => {
  useEffect(() => {
    loadModel({ video: true });
  }, []);
  const [filePath, updateFilePath] = useState([]);
  const [dataURI, updateDataUri] = useState(null);
  const [videoLoading, updateVideoLoading] = useState(false);
  const [streamValues, updateStreamValues] = useState({
    xValues: [],
    yValues: [],
  });
  const [finalCount, updateFinalCount] = useState(0);
  const [counter, updateCounter] = useState(null);
  const vidRef = useRef(null);
  const canvasRef = useRef(null);
  const divRef = useRef(null);
  //   var stats = new Stats();
  //   stats.showPanel(0); // 0: fps, 1: ms, 2: mb, 3+: custom

  useEffect(() => {
    // divRef.current.appendChild(stats.dom);
    updateCounter(
      new SkippingCounter({
        onChangeCallback: (xValues, yValues) =>
          updateStreamValues({ xValues, yValues }),
        increaseCount: (count) => updateFinalCount(count),
      })
    );
  }, []);

  const getPose = async (image) => {
    const temp = await net.estimateSinglePose(image, {
      flipHorizontal: false,
    });
    return temp;
  };

  useEffect(() => {
    if (filePath.length > 0) {
      var reader = new FileReader();
      reader.onload = (e) => {
        updateDataUri(e.target.result);
      };
      reader.readAsDataURL(filePath[0]);
    }
  }, [filePath]);

  const poseDetectionFrame = async () => {
    // stats.begin();
    // console.log("Detecting pose");
    updateVideoLoading(false);
    var pose = await getPose(vidRef.current);
    var image = vidRef.current;
    var width = videoWidth;
    var height = videoHeight;
    canvasRef.current.width = width;
    canvasRef.current.height = height;
    var ctx = canvasRef.current.getContext("2d");
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(image, 0, 0, width, height);
    var { score, keypoints } = pose;
    drawKeypoints(keypoints, 0.1, ctx);
    counter.insertPose(pose);
    // stats.end();
    requestAnimationFrame(poseDetectionFrame);
  };

  const playVideo = () => {
    vidRef.current.play();
  };

  return (
    <div style={{ margin: "20px 0px", width: "100%" }}>
      <FileInput value={filePath} onChange={updateFilePath} />
      <div style={{ display: "flex" }}>
        {dataURI ? (
          ~videoLoading ? (
            <video
              //   autoPlay={true}
              onCanPlay={playVideo}
              muted={true}
              onLoadStart={() => updateVideoLoading(true)}
              onLoadedData={poseDetectionFrame}
              ref={vidRef}
              src={dataURI}
              height={videoHeight}
              width={videoWidth}
              style={{ display: "none" }}
            />
          ) : (
            <p>Loading...</p>
          )
        ) : null}
        <canvas ref={canvasRef} />
      </div>
      <StreamPlot streamValues={streamValues.xValues} />
      <StreamPlot streamValues={streamValues.yValues} />
      <div>Final Count: {finalCount}</div>
      <div ref={divRef}></div>
      {/* <FPSStats /> */}
    </div>
  );
};

const RunOnPic = (props) => {
  useEffect(() => {
    loadModel({ video: false });
  }, []);
  const [filePath, updateFilePath] = useState([]);
  const [dataURI, updateDataUri] = useState(null);
  const imgRef = useRef(null);
  const canvasRef = useRef(null);

  const getPose = async (image) => {
    const temp = await net.estimateSinglePose(image, {
      flipHorizontal: false,
    });
    return temp;
  };

  useEffect(() => {
    if (filePath.length > 0) {
      var reader = new FileReader();
      reader.onload = (e) => {
        updateDataUri(e.target.result);
      };
      reader.readAsDataURL(filePath[0]);
    }
  }, [filePath]);

  useEffect(async () => {
    if (dataURI) {
      var pose = await getPose(imgRef.current);
      var image = imgRef.current;
      canvasRef.current.width = image.width;
      canvasRef.current.height = image.height;
      var ctx = canvasRef.current.getContext("2d");
      var height = image.height;
      var width = image.width;
      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(image, 0, 0, width, height);
      var { score, keypoints } = pose;
      drawKeypoints(keypoints, 0.5, ctx);
    }
  }, [dataURI]);

  return (
    <div style={{ margin: "20px 0px", width: "100%" }}>
      <FileInput value={filePath} onChange={updateFilePath} />
      <div style={{ display: "flex" }}>
        {dataURI ? (
          <img ref={imgRef} src={dataURI} style={{ width: "500px" }} />
        ) : null}
        <canvas ref={canvasRef} />
      </div>
    </div>
  );
};

const SkippingApp = (props) => {
  const [pose, updatePose] = useState({});

  return (
    <div style={{ width: "100%" }}>
      <Tabs style={{ margin: "20px 0px" }}>
        {/* <Tab title="Picture" style={{ margin: "20px 0px" }}>
          <RunOnPic />
        </Tab> */}
        <Tab title="Video" style={{ margin: "20px 0px" }}>
          <RunOnVideo />
        </Tab>
        <Tab title="Webcam">
          <RunOnWebCam />
        </Tab>
      </Tabs>
    </div>
  );
};

export default SkippingApp;
