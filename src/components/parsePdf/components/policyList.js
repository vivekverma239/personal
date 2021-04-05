import React, { useEffect, useState, useRef } from "react";
import {
  List,
  Card,
  Button,
  notification,
  Row,
  Col,
  Divider,
  Popover,
} from "antd";
import { MoreOutlined } from "@ant-design/icons";

const PolicyList = ({
  projectList,
  loading,
  total,
  onPageChange,
  page,
  onClick,
  selectedFile,
}) => {
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
            selectedFile.id == item.id
              ? "custom-list-active"
              : "custom-list-inactive "
          }
          style={{
            width: "100%",
            margin: "0.5rem 0rem",
          }}
          onClick={() => {
            onClick(item);
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

export default PolicyList;
