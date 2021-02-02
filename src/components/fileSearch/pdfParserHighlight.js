// @flow
/* eslint import/no-webpack-loader-syntax: 0 */

import React, { Component } from "react";

import {
  PdfLoader,
  PdfHighlighter,
  Tip,
  Highlight,
  Popup,
  AreaHighlight,
  setPdfWorker,
} from "react-pdf-highlighter";
import PDFWorker from "worker-loader!pdfjs-dist/lib/pdf.worker";
setPdfWorker(PDFWorker);

const getNextId = () => String(Math.random()).slice(2);

const parseIdFromHash = () =>
  document.location.hash.slice("#highlight-".length);

const resetHash = () => {
  document.location.hash = "";
};

const HighlightPopup = ({ comment }) =>
  comment.text ? (
    <div className="Highlight__popup">
      {comment.emoji} {comment.text}
    </div>
  ) : null;

class App extends Component {
  constructor(props) {
    super(props);
  }

  state = {
    baseurl: "http://0.0.0.0:8005/search_file",
    pdfFile: this.props.pdfFile,
    highlights: this.props.highlights,
  };

  resetHighlights = () => {
    this.setState({
      highlights: [],
    });
  };

  scrollViewerTo = (highlight) => {};

  scrollToHighlightFromHash = () => {
    const highlight = this.getHighlightById(parseIdFromHash());

    if (highlight) {
      this.scrollViewerTo(highlight);
    }
  };

  componentDidMount() {
    window.addEventListener(
      "hashchange",
      this.scrollToHighlightFromHash,
      false
    );
  }

  getHighlightById(id) {
    const { highlights } = this.state;

    return highlights.find((highlight) => highlight.id === id);
  }

  //   addHighlight(highlight) {
  //     const { highlights } = this.state;

  //     console.log("Saving highlight", highlight);

  //     this.setState({
  //       highlights: [{ ...highlight, id: getNextId() }, ...highlights],
  //     });
  //   }

  updateHighlight(highlightId, position, content) {
    console.log("Updating highlight", highlightId, position, content);

    this.setState({
      highlights: this.state.highlights.map((h) => {
        const {
          id,
          position: originalPosition,
          content: originalContent,
          ...rest
        } = h;
        return id === highlightId
          ? {
              id,
              position: { ...originalPosition, ...position },
              content: { ...originalContent, ...content },
              ...rest,
            }
          : h;
      }),
    });
  }

  render() {
    const { highlights } = this.state;
    // var url = `${this.state.baseurl}/${this.state.pdfFile.id}/download/`;
    var url = "https://arxiv.org/pdf/1708.08021.pdf";
    console.log(url, highlights);
    return (
      <div style={{ display: "flex", height: "100vh" }}>
        <div
          style={{
            height: "100vh",
            width: "75vw",
            position: "relative",
          }}
        >
          <PdfLoader url={url} beforeLoad={<div>Loading...</div>}>
            {/* {(pdfDocument) => console.log(pdfDocument)} */}
          </PdfLoader>
        </div>
      </div>
    );
  }
}

export default App;
