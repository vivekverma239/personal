import React, { useEffect, useState } from "react";
import { useQuery } from "react-query";
import { Select } from "antd";

import * as posenet from "@tensorflow-models/posenet";
// import { useEffect, useState, useRef } from "react";
import ReactJson from "react-json-view";
import Chart from "kaktana-react-lightweight-charts";
import { LineStyle } from "lightweight-charts";
import { StockService, ConstantService, StrategyService } from "../../services";
import { ReactQueryDevtools } from "react-query/devtools";

const { Option } = Select;

const StockData = (props) => {
  const [stock, updateStock] = useState(null);
  const [timeStep, updateTimeStep] = useState("1M");
  const [strategy, updateStrategy] = useState(null);
  const [staticData, updateStaticData] = useState(null);

  const options = {
    alignLabels: true,
    timeScale: {
      rightOffset: 12,
      barSpacing: 3,
      fixLeftEdge: true,
      lockVisibleTimeRangeOnResize: true,
      rightBarStaysOnScroll: true,
      borderVisible: false,
      borderColor: "#fff000",
      visible: true,
      timeVisible: true,
      secondsVisible: false,
    },
  };

  const constants = useQuery("constants", () => ConstantService.getAll({}), {});

  const stockList =
    constants.data && constants.data.length > 0
      ? constants.data.filter((item) => item["key"] == "stock")[0]["data"][
          "list"
        ]
      : null;

  const stockData = useQuery(
    ["stock", { stock: stock, res: timeStep }],
    () => StockService.getAll({ stock: stock, res: timeStep }),
    { enabled: stock != null }
  );

  const strategyData = useQuery(
    ["strategy", { stock: stock, res: timeStep }],
    () => StrategyService.getAll({ stock: stock, res: timeStep }),
    { enabled: stock != null }
  );

  const priceLines = [
    {
      price: 0.25,
      color: "red",
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
      axisLabelVisible: false,
    },
    {
      price: 0.75,
      color: "green",
      lineWidth: 1,
      lineStyle: LineStyle.Dashed,
      axisLabelVisible: false,
    },
  ];

  const candlestickSeries = [
    {
      data: (stockData.data || []).map((item) => {
        return {
          time: item.time,
          open: item.open,
          close: item.close,
          low: item.low,
          high: item.high,
        };
      }),
    },
  ];

  const lineSeries = [
    {
      data: (strategyData.data || []).map((item) => {
        return {
          time: item.time,
          value: item.score,
        };
      }),
      priceLines,
    },
  ];
  console.log(strategyData.data);
  const markers = [
    {
      price: 90.0,
      color: "red",
      lineWidth: 3,
      lineStyle: LineStyle.Dashed,
      axisLabelVisible: false,
    },
  ];

  console.log(lineSeries);
  return (
    <div style={{ margin: "20px auto", maxWidth: "1200px" }}>
      <Select
        showSearch
        style={{ width: 200 }}
        placeholder="Search Stock"
        optionFilterProp="children"
        value={stock}
        onChange={(e) => updateStock(e)}
        filterOption={(input, option) =>
          option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
        }
      >
        {stockList
          ? stockList.map((symbol) => <Option value={symbol}>{symbol}</Option>)
          : null}
      </Select>
      <Select
        showSearch
        style={{ width: 200 }}
        placeholder="Select TimeFrame"
        optionFilterProp="children"
        onChange={(e) => updateTimeStep(e)}
        style={{ marginLeft: "10px" }}
        value={timeStep}
        filterOption={(input, option) =>
          option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
        }
      >
        <Option value="1m">1M</Option>
        <Option value="5m">5M</Option>
        <Option value="15m">15M</Option>
        <Option value="1d">1D</Option>
      </Select>
      <Chart
        options={options}
        candlestickSeries={candlestickSeries}
        autoWidth
        height={320}
      />
      <Chart options={options} lineSeries={lineSeries} autoWidth height={200} />
      <ReactQueryDevtools initialIsOpen />
    </div>
  );
};

export default StockData;
