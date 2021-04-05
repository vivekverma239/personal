import React, { useEffect, useState, useRef } from "react";
import {
  List,
  Card,
  Input,
  Typography,
  Button,
  Form,
  Drawer,
  PageHeader,
  Tag,
  Tabs,
  Select,
  notification,
  Upload,
  Row,
  Col,
  Empty,
  Divider,
  Popover,
  Checkbox,
} from "antd";
import {
  PlusOutlined,
  UploadOutlined,
  MoreOutlined,
  ArrowLeftOutlined,
} from "@ant-design/icons";
import AddFileForm from "./components/addFile";
import AllPolicyList from "./components/policyList";
import ModalPreview from "./components/preview";

import {
  FileService,
  SearchService,
  SectionSearchService,
  HighlightService,
} from "../../services";

import { useMutation, useQuery, useQueryClient } from "react-query";

const PDFParse = (props) => {
  const [flag, updateFlag] = useState({});
  const [fileIdx, updateFileIdx] = useState(null);

  const [searchStr, updateSearchStr] = useState("");
  const [pdfFile, updatePDFFile] = useState(null);
  const [searchParams, updateSearchParams] = useState({});
  const [sectionSearchParams, updateSSearchParams] = useState({});

  const [fileParams, updateFileParams] = useState({});

  const queryClient = useQueryClient();

  // Search Files
  const searchFiles = useQuery(["searchFiles", fileParams], () =>
    FileService.getAll(fileParams)
  );
  // Add file mutation
  const addFile = useMutation(async (data) => FileService.create(data), {
    onSuccess: () => {
      queryClient.invalidateQueries("searchFiles");
    },
  });

  const [policyUpdate, updatePolicyUpdate] = useState(false);

  return (
    <div style={{ margin: "20px auto", maxWidth: "1200px" }}>
      <PageHeader
        style={{ paddingLeft: "0px" }}
        title={"PDF Search"}
        className="site-page-header"
        extra={[
          <div style={{ display: "flex", alignItems: "center" }}>
            <Button
              style={{ marginRight: "2rem" }}
              onClick={() => {
                updateFlag({ ...flag, addFile: true });
              }}
              type="primary"
              icon={<PlusOutlined />}
            >
              New File
            </Button>
          </div>,
        ]}
      ></PageHeader>
      <Drawer
        title="New File"
        placement="right"
        width={600}
        closable={true}
        onClose={() => {
          updateFlag({ ...flag, addFile: false });
        }}
        visible={flag.addFile}
      >
        <div>
          <div style={{ width: "80%" }}>
            <AddFileForm
              addFile={addFile}
              close={() => {
                updateFlag({ ...flag, addFile: false });
              }}
            />
          </div>
        </div>
      </Drawer>
      <Row style={{ marginTop: "2rem" }}>
        <Input.Search
          onSearch={(e) => updateFileParams({ ...fileParams, search: e })}
          placeholder="Search"
        ></Input.Search>
        <AllPolicyList
          projectList={searchFiles.data ? searchFiles.data.results || [] : []}
          page={0}
          total={searchFiles.data ? searchFiles.data.count || 0 : 0}
          loading={searchFiles.isLoading}
          onPageChange={(page) =>
            updateFileParams({ ...fileParams, page: page })
          }
          onClick={(file) => updatePDFFile(file)}
          selectedFile={pdfFile || {}}
        />
      </Row>
      <ModalPreview pdfFile={pdfFile} close={() => updatePDFFile(null)} />
    </div>
  );
};

export default PDFParse;
