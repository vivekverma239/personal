import React, { useEffect, useState } from "react";
import { ChessboardRecService } from "../../services/baseService";
import FileButton from "../../components/common/fileUpload";
import { useQuery } from "react-query";
import Loader from "react-loader-spinner";

const Chessboard = () => {
  const [data, updateData] = useState(null);

  useEffect(() => {
    predictRandom();
  }, []);

  useEffect(() => {
    if (data) {
      predict.refetch();
    }
  }, [data]);

  const predictRandom = () => {
    const data = new FormData();
    data.append("random", true);
    updateData(data);
  };

  const predict = useQuery(
    "chessboardPredict",
    () => chessService.predict(data),
    {
      enabled: false,
    }
  );

  const onSelect = (e) => {
    const file = e.target.files[0];
    const data = new FormData();
    data.append("file", file);
    updateData(data);
  };

  const chessService = new ChessboardRecService();

  return (
    <>
      {/* <div
        className="is-capitalized  pt-6"
        style={{ color: "#c383a6", letterSpacing: "4px", fontSize: "22px" }}
      >
        CHESSBOARD RECOGNITION
      </div> */}
      <div className="section mr-6 ml-6">
        <div
          className="has-text-bold"
          style={{
            color: "#c383a6",
            //   letterSpacing: "2px",
            fontSize: "48px",
            fontWeight: "bold",
          }}
        >
          Chessboard Recognition
        </div>
        <div className="columns mt-4 is-centered">
          <div className="column is-2 is-flex is-justify-content-center">
            <FileButton onSelect={onSelect} />
          </div>
          <div className="column is-1 is-flex is-align-items-center is-justify-content-center	">
            OR
          </div>
          <div className="column is-2 is-flex is-justify-content-center">
            <button
              className="button is-outlined is-primary is-light"
              onClick={predictRandom}
            >
              Random Image
            </button>
          </div>
        </div>
      </div>
      {predict.data ? (
        <>
          {predict.isLoading ? (
            <Loader
              type="Puff"
              color="#00BFFF"
              height={100}
              width={100}
              timeout={3000} //3 secs
            />
          ) : null}
          <div className="columns is-centered mt-4 ">
            <div className="column is-4 ">
              <p class="has-text-centered	mb-2 is-italic">Original Image</p>
              <figure className="image is-square ">
                <img
                  src={`http://localhost:8003/chessboard/download/?file=${encodeURI(
                    predict.data.image
                  )}`}
                ></img>
              </figure>
            </div>

            <div className="column is-4">
              <p class="has-text-centered	mb-2 is-italic">Identified Mask</p>

              <figure className="image is-square">
                <img
                  src={`http://localhost:8003/chessboard/download/?file=${encodeURI(
                    predict.data.blend
                  )}`}
                ></img>
              </figure>
            </div>
          </div>

          <div className="columns  is-centered mt-4 ">
            <div className="column is-4">
              <p class="has-text-centered	mb-2 is-italic">Segmented Board</p>

              <figure className="image is-square">
                <img
                  src={`http://localhost:8003/chessboard/download/?file=${encodeURI(
                    predict.data.board
                  )}`}
                ></img>
              </figure>
            </div>

            <div className="column is-4">
              <p class="has-text-centered	mb-2 is-italic">Detected Board</p>
              <figure className="image is-square">
                <img
                  src={`http://localhost:8003/chessboard/download/?file=${encodeURI(
                    predict.data.predicted
                  )}`}
                ></img>
              </figure>
            </div>
          </div>
        </>
      ) : null}
    </>
  );
};

export default Chessboard;
