import React from "react";
import { Row, Col } from "antd";
import { Modal } from "antd";
import PDFViewer from "../../common/pdfViewer";
import MarkdownEditor from "./editor";

const ModalPreview = (props) => {
  return (
    <div>
      <Modal
        // title="Modal 1000px width"
        centered
        footer={null}
        visible={props.pdfFile}
        onOk={() => props.close()}
        onCancel={() => props.close()}
        width={1200}
      >
        <div>
          <Row>
            <Col span={12}>
              <PDFViewer pdfFile={props.pdfFile} height={700} />
            </Col>
            <Col span={12}>
              <MarkdownEditor value={props.markdownValue} />
            </Col>
          </Row>
        </div>
      </Modal>
    </div>
  );
};

export default ModalPreview;
