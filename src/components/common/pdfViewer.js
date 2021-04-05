import React, { Component, useState, useEffect } from "react";
import { Row, Pagination } from "antd";

import { LoadingOutlined } from "@ant-design/icons";

// import { Document, Page } from "react-pdf";
import { pdfjs } from "react-pdf";
import { Document, Page } from "react-pdf";

// import "../../index.css";
pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

const antIcon = (
  <LoadingOutlined style={{ fontSize: 18, color: "white" }} spin />
);

class PDFViewer extends Component {
  constructor(props) {
    super(props);
    this.pageRef = React.createRef();
    this.highlightRef = React.createRef();
    this.scrollToHighlight = (element, page) => {
      if (element && String(page) == this.state.pageNumber) {
        element.scrollIntoView();
      }
    };
    this.state = {
      numPages: null,
      pdfLoaded: false,
      pageNumber: this.props.pageNumber || 1,
      baseurl:
        process.env.REACT_APP_ENV == "prod"
          ? "https://nlp-dashboard.chatteron.io/api"
          : process.env.REACT_APP_ENV == "staging"
          ? "https://staging-nlp-dashboard.chatteron.io/api"
          : "http://0.0.0.0:8005/search_file",
      markDisabled: true,
      pdfFile: this.props.pdfFile,
      height: this.props.height || 1000,
    };
  }

  onDocumentLoadSuccess = ({ numPages }) => {
    this.setState({ numPages, pdfLoaded: true });
    // document.getElementById(`page-${this.props.pageNumber}`).scrollIntoView();
  };

  removeTextLayerOffset() {
    const textLayers = document.querySelectorAll(
      ".react-pdf__Page__textContent"
    );
    textLayers.forEach((layer) => {
      const { style } = layer;
      style.top = "0";
      style.left = "0";
      style.transform = "";
      style.lineHeight = 1.35;
    });
  }

  render() {
    const { pageNumber, numPages } = this.state;
    var pages = [];
    var page = 1;
    while (page < numPages) {
      pages.push(page);
      page += 1;
    }
    return (
      <div>
        <Row>
          <div
            style={{
              display: "flex",
              width: "100%",
              justifyContent: "center",
              justifyItems: "center",
              backgroundColor: "white",
              paddingBottom: "10px",
            }}
          >
            {this.state.pdfLoaded ? (
              <Pagination
                simple
                current={this.state.pageNumber}
                defaultPageSize={1}
                total={numPages}
                disabled={this.state.parsing}
                onChange={(e) => this.setState({ pageNumber: e })}
              />
            ) : null}
          </div>
          <div
            style={{
              height: "80vh",
              overflowY: "auto",
              marginTop: "10px",
              marginLeft: "3rem",
            }}
          >
            {this.state.pdfFile ? (
              <div>
                <Document
                  file={`${this.state.baseurl}/${this.state.pdfFile.id}/download/`}
                  onLoadSuccess={this.onDocumentLoadSuccess.bind(this)}
                >
                  <div
                    style={{
                      position: "relative",
                      zIndex: 100,
                    }}
                  >
                    {pages.map((page) => (
                      <div id={`page-${page}`} key={page}>
                        <Page
                          style={{
                            backgroundColor: "gray",
                          }}
                          height={this.state.height}
                          pageNumber={page}
                          inputRef={(ref) => this.scrollToHighlight(ref, page)}
                          onLoadSuccess={this.removeTextLayerOffset.bind(this)}
                        >
                          <div>
                            {this.props.custom_highlights ? (
                              <div>
                                {(this.props.custom_highlights.es || [])
                                  .filter((item) => item.page == String(page))
                                  .map((rect, idx) => {
                                    return (
                                      <div
                                        className={
                                          this.state.componentIdx == idx
                                            ? "pdf-parser-highlighted"
                                            : null
                                        }
                                        id="highlighted"
                                        key={idx}
                                        style={{
                                          position: "absolute",
                                          top:
                                            String(
                                              (parseInt(rect["top"]) /
                                                parseInt(
                                                  rect["page_data"]["height"]
                                                )) *
                                                this.state.height
                                            ) + "px",
                                          left:
                                            String(
                                              (parseInt(rect["left"]) /
                                                parseInt(
                                                  rect["page_data"]["height"]
                                                )) *
                                                this.state.height
                                            ) + "px",
                                          width:
                                            String(
                                              (parseInt(rect["width"]) /
                                                parseInt(
                                                  rect["page_data"]["height"]
                                                )) *
                                                this.state.height
                                            ) + "px",
                                          height:
                                            String(
                                              (parseInt(rect["height"]) /
                                                parseInt(
                                                  rect["page_data"]["height"]
                                                )) *
                                                this.props.height
                                            ) + "px",
                                          backgroundColor: "#fbff0047",
                                        }}
                                      ></div>
                                    );
                                  })}{" "}
                              </div>
                            ) : null}
                          </div>
                        </Page>
                      </div>
                    ))}
                  </div>
                </Document>
              </div>
            ) : null}
          </div>
        </Row>
      </div>
    );
  }
}

export default PDFViewer;
