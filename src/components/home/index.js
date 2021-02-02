// import { Grommet, Box, Grid, Header } from "grommet";
import { Layout, Typography } from "antd";
import { Steps, Popover } from "antd";

// import BackgroundImage from "./assets/cool-background.svg";
import BackgroundImage from "../../assets/cool-background-edited.svg";

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;
const { Step } = Steps;

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

function Home() {
  return (
    <div>
      <Layout>
        <div
          className="home-banner"
          style={{
            backgroundImage: `url(${BackgroundImage})`,
            backgroundColor: "#00152900",
            backgroundRepeat: "no-repeat",
            backgroundSize: "cover",
          }}
        >
          <div className="home-banner-holder">
            <Title style={{ fontSize: "64px", color: "#323377" }}>
              Hi, I'm Vivek
            </Title>
            <Title style={{ fontSize: "22px", color: "#87084E" }}>
              Machine Learning Engineer, Backend Developer
            </Title>
            <Title
              style={{
                fontSize: "18px",
                color: "#87084E",
                fontStyle: "italic",
              }}
            >
              Passionately curious about almost everything!
            </Title>
          </div>
        </div>
        <Content>
          <div className="about-me">
            <Title style={{ fontSize: "24px", color: "#87084E" }}>
              About Me
            </Title>
            <p style={{ lineHeight: "40px", fontSize: "18px" }}>
              Vivek has 4.5+ years overall experience including 2 years in Deep
              Learning and Machine Learning. Currently, working as Data
              Scientist with ‘Innoplexus’ – a Germany-based product company in
              AI/ML serving global pharmaceutical companies. Hands-on experience
              in NLP and in developing ML based algorithms for various use-cases
              which have been integrated in company's flagship products.
              Skill-sets: NLP and ML techniques – Text Classification, Entity
              Extraction, Text Summarization, Decision Trees, Active Learning,
              Transfer Learning IT Skills – Proficient in python, tensorflow,
              keras DB: Elasticsearch and MongoDB
            </p>
          </div>
          <div className="experiences">
            <Title style={{ fontSize: "24px", color: "#87084E" }}>
              Experiences
            </Title>
            <div>
              <Steps current={1} progressDot={customDot} direction="vertical">
                <Step
                  title="Finished"
                  description="You can hover on the dot."
                />
                <Step
                  title="In Progress"
                  description="You can hover on the dot."
                />
                <Step title="Waiting" description="You can hover on the dot." />
                <Step title="Waiting" description="You can hover on the dot." />
              </Steps>
            </div>
          </div>
          <div className="education">
            <Title style={{ fontSize: "24px", color: "#87084E" }}>
              Education
            </Title>
          </div>
          <div className="Projects">
            <Title style={{ fontSize: "24px", color: "#87084E" }}>
              Projects
            </Title>
            <div>Skipping</div>
          </div>
        </Content>
      </Layout>
    </div>
  );
}

export default Home;
