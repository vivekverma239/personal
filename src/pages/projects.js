import React from "react";

const ProjectCard = ({ item }) => {
  return (
    <div class="card mr-2 mb-2">
      <div class="card-content">
        <div class="columns is-multiline">
          <div class="column is-narrow is-flex is-justify-content-center">
            <figure class="image is-128x128">
              <img
                src="https://bulma.io/images/placeholders/128x128.png"
                alt="Placeholder image"
              />
            </figure>
          </div>
          <div class="column is-narrow">
            <p class="is-size-6 mb-2 has-text-primary">{item.name}</p>
            <p class="is-size-7 mb-2 has-text-gray">{item.description}</p>
            <div>
              {item.tags.map((tag) => (
                <span class="tag is-info is-light mr-1">{tag}</span>
              ))}
            </div>
            <button class="button is-secondary is-light is-small mt-3">
              <span>Show demo</span>
              <span class="icon is-small">
                <i class="fas fa-chevron-right"></i>
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const projects = [
  {
    name: "Chess Board Recognition",
    description:
      "Segment chessboard from a screenshot/image and identify individual pieces to create a digital board from which a person can resume playing",
    img: "",
    tags: [
      "Image Segmentation",
      "Image Classification",
      "DeepLabV3",
      "Image Processing",
      "Augmentation",
    ],
  },
  {
    name: "Jump Rope Counter",
    description: "Count number of time jumped using computer vision",
    img: "",
    tags: ["Posenet", "Video Processing"],
  },
  {
    name: "Face Emotion Recognition",
    description: "Count number of time jumped using computer vision",
    img: "",
    tags: ["Image Classification"],
  },
];

const ProjectList = () => {
  return (
    <>
      {projects.map((item) => (
        <ProjectCard item={item} />
      ))}
    </>
  );
};

export default ProjectList;
