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
  SearchOutlined,
  PlusOutlined,
  UploadOutlined,
  EditFilled,
  ReloadOutlined,
  MoreOutlined,
  DeleteOutlined,
  FormOutlined,
  ArrowLeftOutlined,
} from "@ant-design/icons";
import PDFParser from "./pdfParser";
import PDFParserHighlight from "./pdfParserHighlight";

import {
  FileService,
  SearchService,
  SectionSearchService,
  HighlightService,
} from "../../services";
import {
  useMutation,
  useQuery,
  useQueryClient,
  useQueryCache,
} from "react-query";

const { Title } = Typography;
const { TabPane } = Tabs;

const AllPolicyList = ({
  projectList,
  loading,
  total,
  onPageChange,
  page,
  onClick,
  selectedFileIdx,
}) => {
  const openNotificationWithIcon = (type, message, description) => {
    notification[type]({
      message: message,
      description: description,
    });
  };

  return (
    <List
      pagination={{
        onChange: (page) => {
          onPageChange(page);
        },
        total: total,
        // pageSize: 6,
        defaultCurrent: page,
      }}
      dataSource={projectList}
      loading={loading}
      style={{ height: "100%" }}
      renderItem={(item, idx) => (
        <Card
          className={
            selectedFileIdx == idx
              ? "custom-list-active"
              : "custom-list-inactive "
          }
          style={{
            width: "100%",
            margin: "0.5rem 0rem",
          }}
          onClick={() => {
            onClick(idx);
          }}
          hoverable
        >
          <Row>
            <Col span={16}>
              <div>{item.name}</div>
            </Col>
            <Col span={8}>
              <div style={{ float: "right" }}>
                <Popover
                  placement="bottomLeft"
                  content={
                    <div>
                      <div style={{ width: "160px" }}>
                        <Divider
                          style={{
                            backgroundColor: "#d4cbcb91",
                            margin: "5px 0px",
                          }}
                        />
                      </div>
                    </div>
                  }
                  trigger="click"
                >
                  <Button type="link" icon={<MoreOutlined />}></Button>
                </Popover>
              </div>
            </Col>
          </Row>
        </Card>
      )}
    />
  );
};

const AllSearchList = ({
  searchList,
  loading,
  total,
  onPageChange,
  page,
  onClick,
  selectedFileIdx,
}) => {
  const openNotificationWithIcon = (type, message, description) => {
    notification[type]({
      message: message,
      description: description,
    });
  };

  return (
    <List
      pagination={{
        onChange: (page) => {
          onPageChange(page);
        },
        total: total,
        pageSize: 6,
        defaultCurrent: page,
      }}
      dataSource={searchList}
      loading={loading}
      style={{ height: "100%" }}
      renderItem={(item, idx) => (
        <Card
          className={
            selectedFileIdx == idx
              ? "custom-list-active"
              : "custom-list-inactive "
          }
          style={{
            width: "100%",
            margin: "0.5rem 0rem",
          }}
          onClick={() => {
            onClick(idx);
          }}
          hoverable
        >
          <Row>
            <Col span={16}>
              <div>{item["_source"].file_name}</div>
              <div>{item["_source"].page}</div>
              <div>{item.ml_score}</div>
              <div>
                {item.highlight
                  ? item["highlight"]["text"].map((text) => (
                      <span
                        dangerouslySetInnerHTML={{ __html: `... ${text} ...` }}
                      ></span>
                    ))
                  : ""}
              </div>
            </Col>
            <Col span={8}>
              <div style={{ float: "right" }}>
                <Popover
                  placement="bottomLeft"
                  content={
                    <div>
                      <div style={{ width: "160px" }}>
                        <Divider
                          style={{
                            backgroundColor: "#d4cbcb91",
                            margin: "5px 0px",
                          }}
                        />
                      </div>
                    </div>
                  }
                  trigger="click"
                >
                  <Button type="link" icon={<MoreOutlined />}></Button>
                </Popover>
              </div>
            </Col>
          </Row>
        </Card>
      )}
    />
  );
};

const AllSectionSearchList = ({
  searchList,
  loading,
  total,
  onPageChange,
  page,
  onClick,
  selectedFileIdx,
}) => {
  const openNotificationWithIcon = (type, message, description) => {
    notification[type]({
      message: message,
      description: description,
    });
  };

  return (
    <List
      pagination={{
        onChange: (page) => {
          onPageChange(page);
        },
        total: total,
        pageSize: 6,
        defaultCurrent: page,
      }}
      dataSource={searchList}
      loading={loading}
      style={{ height: "100%", width: "100%" }}
      renderItem={(item, idx) => (
        <Card
          className={
            selectedFileIdx == idx
              ? "custom-list-active"
              : "custom-list-inactive "
          }
          style={{
            width: "100%",
            margin: "0.5rem 0rem",
          }}
          onClick={() => {
            onClick(idx);
          }}
          hoverable
        >
          <Row>
            <Col span={16}>
              <div>{item["_source"].file_name}</div>
              <div>{item["_source"].page}</div>
              <div>{item.ml_score}</div>

              <div>{item["_source"]["text"]}</div>
            </Col>
            <Col span={8}>
              <div style={{ float: "right" }}>
                <Popover
                  placement="bottomLeft"
                  content={
                    <div>
                      <div style={{ width: "160px" }}>
                        <Divider
                          style={{
                            backgroundColor: "#d4cbcb91",
                            margin: "5px 0px",
                          }}
                        />
                      </div>
                    </div>
                  }
                  trigger="click"
                >
                  <Button type="link" icon={<MoreOutlined />}></Button>
                </Popover>
              </div>
            </Col>
          </Row>
        </Card>
      )}
    />
  );
};

const AddFileForm = (props) => {
  const [loading, updateLoading] = useState(false);
  const [uploadButtonStatus, setUploadButtonStatus] = useState("enabled");

  // Address, to be embedded on Person
  var schema = {
    type: "array",
    items: {
      properties: {
        values: {
          type: "array",
          items: { type: "string" },
        },
        key: { type: "string" },
        label: { type: "string" },
        country: { type: "string" },
      },
      required: ["values", "key", "label"],
    },
  };

  const openNotificationWithIcon = (type, message, description) => {
    notification[type]({
      message: message,
      description: description,
    });
  };

  const layout = {
    labelCol: { span: 8 },
    wrapperCol: { span: 16 },
  };
  const tailLayout = {
    wrapperCol: { offset: 8, span: 16 },
  };

  const [form] = Form.useForm();

  const onFinish = async (values) => {
    var formdata = new FormData();
    formdata.append("name", values.name);
    formdata.append("applicable_for", JSON.stringify(values.condition));
    formdata.append("is_scanned", values.isScanned ? true : false);
    if (values.file) {
      formdata.append(
        "file",
        values.file ? values.file[0].originFileObj : null
      );
      formdata.append("status", "processing");
    } else {
      formdata.append("status", "uploaded");
      formdata.append("auto_parse_status", "na");
    }
    props.addFile.mutate(formdata, {
      onSuccess: (data) => {
        openNotificationWithIcon("success", "File Uploaded");
        onReset();
      },
      onError: (error) => {
        openNotificationWithIcon(
          "error",
          "File Uploading Failed",
          JSON.stringify(error)
        );
      },
    });
  };

  const onReset = () => {
    form.resetFields();
    setUploadButtonStatus("enabled");
  };

  const normFile = (e) => {
    setUploadButtonStatus("disabled");
    if (Array.isArray(e)) {
      return e;
    }
    return e && e.fileList;
  };

  return (
    <Form
      {...layout}
      form={form}
      name="control-hooks"
      onFinish={onFinish}
      initialValues={{ condition: [{}], lang: "en" }}
    >
      <Form.Item
        name="name"
        label="Policy Name"
        rules={[{ required: true, message: "Please enter policy name!" }]}
      >
        <Input placeholder="File Name" />
      </Form.Item>
      <Form.Item
        name="file"
        label="File"
        valuePropName="fileList"
        getValueFromEvent={normFile}
        rules={[{ required: false, message: "Please select a file!" }]}
      >
        <Upload
          name="file"
          multiple={false}
          style={{ width: "300px" }}
          beforeUpload={(file) => {
            return false;
          }}
          listType="picture"
          disabled={uploadButtonStatus != "enabled"}
          onRemove={() => {
            setUploadButtonStatus("enabled");
          }}
        >
          <Button>
            <UploadOutlined /> Click to upload
          </Button>
        </Upload>
      </Form.Item>
      <Form.Item {...tailLayout}>
        <Button
          style={{ marginRight: "1rem" }}
          type="primary"
          htmlType="submit"
          loading={loading}
        >
          Submit
        </Button>
        <Button htmlType="button" onClick={onReset}>
          Reset
        </Button>
      </Form.Item>
    </Form>
  );
};

const ProjectPolicyView = (props) => {
  const [flag, updateFlag] = useState({});
  const [fileIdx, updateFileIdx] = useState(null);
  const [searchResultIdx, updateSearchResultIdx] = useState(null);
  const [page, updatePage] = useState(null);

  const [searchStr, updateSearchStr] = useState("");
  const [pdfFile, updatePDFFile] = useState(null);
  const [searchParams, updateSearchParams] = useState({});
  const [sectionSearchParams, updateSSearchParams] = useState({});

  const [fileParams, updateFileParams] = useState({});

  const queryClient = useQueryClient();
  const searchFiles = useQuery(["searchFiles", fileParams], () =>
    FileService.getAll(fileParams)
  );

  const searchResults = useQuery(
    ["searchResults", searchParams],
    () => SearchService.getAll(searchParams),
    { enabled: searchParams.query && searchParams.project_id ? true : false }
  );
  const searchSearchResults = useQuery(
    ["searchSearchResults", sectionSearchParams],
    () => SectionSearchService.getAll(sectionSearchParams),
    {
      enabled:
        sectionSearchParams.query && sectionSearchParams.project_id
          ? true
          : false,
    }
  );

  const highlights = useQuery(
    [
      "searchHighlights",
      searchParams.query || sectionSearchParams.query,
      searchResultIdx,
    ],
    () =>
      HighlightService.getAll({
        ...sectionSearchParams,
        ...searchParams,
        page: searchResults.data[searchResultIdx]["_source"]["page"],
        file_id: searchResults.data[searchResultIdx]["_source"]["file_id"],
      }),
    {
      enabled:
        (searchParams.query || sectionSearchParams.query) &&
        searchResultIdx != null
          ? true
          : false,
    }
  );

  const [policyUpdate, updatePolicyUpdate] = useState(false);
  const addFile = useMutation(async (data) => FileService.create(data), {
    onSuccess: () => {
      queryClient.invalidateQueries("searchFiles");
    },
  });

  console.log(
    fileIdx && searchFiles.data.results[fileIdx]
      ? searchFiles.data.results[fileIdx]
      : null,
    fileIdx
  );
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
      <Tabs defaultActiveKey="2">
        <TabPane tab="Section Search" key="2">
          <div
            style={{
              width: "100%",
              marginTop: "20px",
              display: "flex",
              justifyContent: "center",
            }}
          >
            <Input.Search
              placeholder="input search text"
              allowClear
              size="large"
              onSearch={(e) =>
                updateSSearchParams({ ...sectionSearchParams, query: e })
              }
              enterButton="Search"
              style={{
                width: "70%",
                borderRadius: "10px",
              }}
            />
          </div>
          <Row
            style={{
              marginTop: "2rem",
              display: "flex",
              justifyContent: "center",
            }}
          >
            {searchResultIdx != null &&
            searchSearchResults.data &&
            searchSearchResults.data[searchResultIdx] ? (
              <div>
                <Button
                  onClick={() => {
                    updateSearchResultIdx(null);
                  }}
                  icon={<ArrowLeftOutlined />}
                >
                  Back to Results
                </Button>
                <PDFParser
                  pdfFile={{
                    id:
                      searchSearchResults.data[searchResultIdx]["_source"][
                        "file_id"
                      ],
                  }}
                  pageNumber={parseInt(
                    searchSearchResults.data[searchResultIdx]["_source"]["page"]
                  )}
                  highlights={[]}
                  custom_highlights={{
                    es:
                      (searchSearchResults.data[searchResultIdx]["_source"]
                        .component || {})["rects"] || [],
                  }}
                />
              </div>
            ) : (
              <AllSectionSearchList
                searchList={
                  searchSearchResults.data ? searchSearchResults.data || [] : []
                }
                page={0}
                total={
                  searchSearchResults.data
                    ? searchSearchResults.data.length || 0
                    : 0
                }
                loading={searchResults.isLoading}
                onClick={(idx) => updateSearchResultIdx(idx)}
                selectedFileIdx={searchResultIdx}
              />
            )}
          </Row>
        </TabPane>
        <TabPane tab="All Files" key="3">
          <Row style={{ marginTop: "2rem" }}>
            <Col span={7}>
              <Input.Search
                onSearch={(e) => updateFileParams({ ...fileParams, search: e })}
                placeholder="Search"
              ></Input.Search>
              <AllPolicyList
                projectList={
                  searchFiles.data ? searchFiles.data.results || [] : []
                }
                page={0}
                total={searchFiles.data ? searchFiles.data.count || 0 : 0}
                loading={searchFiles.isLoading}
                onPageChange={(page) =>
                  updateFileParams({ ...fileParams, page: page })
                }
                onClick={(idx) => updateFileIdx(idx)}
                selectedFileIdx={fileIdx}
              />
            </Col>
            <Divider
              type={"vertical"}
              style={{
                height: "100%",
                backgroundColor: "#d4cbcb91",
                margin: "0px 12px",
              }}
            ></Divider>
            <Col span={16}>
              {fileIdx != undefined && searchFiles.data.results[fileIdx] ? (
                <PDFParser
                  pdfFile={searchFiles.data.results[fileIdx]}
                  highlights={[]}
                />
              ) : (
                <Empty description={"Select a file"} />
              )}
            </Col>
          </Row>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default ProjectPolicyView;
