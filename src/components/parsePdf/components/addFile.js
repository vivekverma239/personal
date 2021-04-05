import React, { useState } from "react";
import { Input, Button, Form, notification, Upload } from "antd";
import { UploadOutlined } from "@ant-design/icons";

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

export default AddFileForm;
