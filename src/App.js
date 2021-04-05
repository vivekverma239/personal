import "./App.less";
// import { Grommet, Box, Grid, Header } from "grommet";
import Model from "./model";
import { BrowserRouter as Router, Route } from "react-router-dom";
import { Layout, Menu, Avatar, Image, Row, Col, Typography } from "antd";
import { Steps, Popover } from "antd";
import { QueryClient, QueryClientProvider, useQuery } from "react-query";

// import BackgroundImage from "./assets/cool-background.svg";
import BackgroundImage from "./assets/cool-background-edited.svg";
import NavBar from "./containers/navbar";
import ProfilePic from "./assets/profilepic.png";
import Home from "./pages/home";
import ChessboardRec from "./pages/chessboard";

import Projects from "./pages/projects";

import SkippingProject from "./components/skippingProject";
import StockPredictions from "./components/stockPredictions";
import FileSearch from "./components/fileSearch";
import PDFParse from "./components/parsePdf";

import * as ROUTES from "./constants/routes";

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;
const { Step } = Steps;
const queryClient = new QueryClient();

const customDot = (dot, { status, index }) => (
  <Popover
    content={
      <span>
        step {index} status: {status}
      </span>
    }
  >
    {dot}
  </Popover>
);

const App = () => (
  <Router>
    <QueryClientProvider client={queryClient}>
      <div>
        <NavBar />
        {/* <Header
          className="header"
          style={{
            background: "none",
            borderBottom: "none",
          }}
        >
          <Row style={{ padding: "5px 0px" }}>
            <Col span={4}>
              <Avatar
                size={64}
                style={{ border: "2px solid rgb(50 51 119)" }}
                src={<Image src={ProfilePic} />}
              />
            </Col>
            <Col span={20}>
              <Menu
                theme="light"
                mode="horizontal"
                defaultSelectedKeys={["1"]}
                style={{ background: "none", borderBottom: "none" }}
              >
                <Menu.Item key="1">About</Menu.Item>
                <Menu.Item key="2">Projects</Menu.Item>
                <Menu.Item key="3">Blog</Menu.Item>
                <Menu.Item key="4">Github</Menu.Item>
              </Menu>
            </Col>
          </Row>
        </Header> */}

        <div style={{ marginTop: "100px" }}>
          <Route exact path={ROUTES.LANDING} component={Home} />
          <Route exact path={ROUTES.PROJECTS} component={Projects} />
          <Route exact path={ROUTES.SKIPPING_APP} component={SkippingProject} />
          <Route exact path={ROUTES.STOCK_PRED} component={StockPredictions} />
          <Route exact path={ROUTES.FILE_SEARCH} component={FileSearch} />
          <Route exact path={ROUTES.PDF_PARSE} component={PDFParse} />
          <Route exact path={ROUTES.Chessboard_REC} component={ChessboardRec} />
        </div>
        {/* <Route exact path={ROUTES.ADMIN} component={AdminPage} /> */}
      </div>
    </QueryClientProvider>
  </Router>
);
export default App;
