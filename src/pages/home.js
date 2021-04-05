import React from "react";
// import BackgroundImage from "../assets/Happy Bunch - Desk.png";
import BackgroundImage from "../assets/undraw_dev_productivity_umsq.svg";

const ExperienceComponent = ({ data }) => {
  return (
    <div class="content is-normal is-flex">
      <div
        class="is-flex is-flex-direction-column"
        style={{ marginBottom: "20px" }}
      >
        <div
          style={{
            position: "relative",
            top: "10px",
            left: "0px",
            width: "9px",
            height: "9px",
            borderRadius: "50%",
            backgroundColor: "gray",
          }}
        ></div>
        <div
          style={{
            position: "relative",
            top: "20px",
            left: "4px",
            height: "100%",
            overflow: "hidden",
            borderLeft: "1px dashed",
          }}
        ></div>
      </div>
      <div style={{ paddingLeft: "20px" }}>
        <div style={{ marginBottom: "10px" }}>
          <p className="is-size-5" style={{ marginBottom: "0px" }}>
            {data.designation}
          </p>
          <div>
            <p className="is-size-6 has-text-grey">{data.timeline}</p>
          </div>
        </div>

        <div>
          <ul style={{ marginTop: "0px" }}>
            {data.bullets.map((bullet) => (
              <li>{bullet}</li>
            ))}
          </ul>
        </div>
        <div className="mt-4">
          Tools:{" "}
          {data.tools.map((tool) => (
            <span class="tag is-info is-light mr-1">{tool}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

const experiences = [
  {
    designation: "Machine Learning Engineer",
    timeline: "Leena AI · 2020 – Present",
    bullets: [
      "Developed a complete ML back end to classify user queries from bot to more than 500 intents, this reduced prediction time per query by more than 5x, also reduced training time by 10x.",
      "Ideated and developed a front end and back end to facilitate internal bot data creation and management, used by more than 15 analysts. Reduced bot development time by 2x.",
      "Developed a PDF Parser utility to prepare FAQs and parse tables out of scanned PDF documents, reducing the time required by a factor of 5x.",
    ],
    tools: [
      "Amazon Web Services (AWS)",
      "Docker",
      "React",
      "Django",
      "Scikit-learn",
      "Keras",
      "TensorFlow",
      "Natural Language Processing (NLP)",
      " Machine Learning",
    ],
  },
  {
    designation: "Machine Learning Engineer",
    timeline: "PolicyBazaar · 2019 – 2020",
    bullets: [
      "Achieved a 25% increase in lead conversion and a 30% increase in revenue by using an AI-lead ranking algorithm.",
      "Built a lead rejection model using call transcriptions data, leading to an estimated cost savings of 10%.",
    ],
    tools: [
      "Amazon Web Services (AWS)",
      "Natural Language Processing (NLP)",
      "Machine Learning",
    ],
  },
  {
    designation: "Data Scientist",
    timeline: "Innoplexus · 2017 – 2019",
    bullets: [
      "Developed an NLP-based model to identify adverse reactions associated with a particular drug with an accuracy of over 80%.",
      "Built a state-of-the-art biomedical entity extractor to identify new biomedical entities from a corpus of biomedical abstracts, gaining more than 10% accuracy over the existing process.",
    ],
    tools: [
      "React",
      "Django",
      "PyTorch",
      "Keras",
      "TensorFlow",
      "Elasticsearch",
      "Machine Learning",
      " Natural Language Processing (NLP)",
    ],
  },
];

const HomePage = () => {
  return (
    <>
      <div className="columns is-vcentered">
        <div className="column is-6 ">
          <p style={{ fontSize: "64px", color: "#323377" }}>Hi, I'm Vivek</p>
          <p style={{ fontSize: "22px", color: "#c383a6" }}>
            Machine Learning Engineer, Backend Developer
          </p>
          <p
            style={{
              fontSize: "18px",
              color: "#c383a6",
              fontStyle: "italic",
            }}
          >
            Passionately curious about almost everything!
          </p>
        </div>
        <div className="column is-6">
          <img style={{ height: "400px" }} src={BackgroundImage} />
        </div>
      </div>
      <div className="mb-6">
        <p class="menu-label is-size-6" style={{ color: "#c383a6" }}>
          About Me
        </p>
        <p>
          Vivek has more than four years of experience developing end-to-end
          solutions based on machine learning (ML) and deep learning. He's
          worked on projects from different sectors including Fortune 500
          pharmaceutical companies like Merck and Pfizer. Vivek excels at
          providing end-to-end solutions using ML not just coding an algorithm.
          Apart from being an expert in natural language processing, Vivek also
          has robust development skills with React and Django.
        </p>
      </div>
      <div className="mb-6">
        <p class="menu-label is-size-6" style={{ color: "#c383a6" }}>
          Experiences
        </p>
        <div>
          {experiences.map((experience) => (
            <ExperienceComponent data={experience} />
          ))}
        </div>
      </div>
      <div className="mb-6">
        <p class="menu-label is-size-6" style={{ color: "#c383a6" }}>
          Education
        </p>
        <div>
          <p>Bachelor's Degree in Mechanical Engineering</p>
          <p> 2012 - 2016</p>
          <p> Indian Institute of Technology Delhi - New Delhi</p>
          <p>India</p>
        </div>
      </div>
    </>
  );
};
export default HomePage;
