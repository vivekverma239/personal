import React from "react";
import ProfilePic from "../assets/profilepic.png";

const NavBar = () => {
  return (
    <div>
      <nav
        class="navbar is-transparent is-spaced	 is-fixed-top "
        role="navigation"
        aria-label="main navigation"
        style={{ margin: "auto", height: "80px" }}
      >
        <div class="navbar-brand" style={{ margin: "auto" }}>
          {/* <a class="navbar-item" href="https://bulma.bootcss.com">
            <figure class="image is-64x64">
              <img class="is-rounded" src={ProfilePic} />
            </figure>
          </a> */}
          <figure class="image is-64x64">
            <img
              class="is-rounded"
              style={{ margin: "auto" }}
              src={ProfilePic}
            />
          </figure>
          <a
            role="button"
            class="navbar-burger burger"
            aria-label="menu"
            aria-expanded="false"
            data-target="navbarBasicExample"
          >
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </a>
        </div>

        <div id="navbarBasicExample" class="navbar-menu">
          <div class="navbar-end">
            <div class="navbar-item">
              <a
                class="navbar-item is-primary"
                href="https://bulma.io/"
                style={{ marginRight: "3rem" }}
              >
                Home
              </a>
              <a
                class="navbar-item "
                href="https://bulma.io/"
                style={{ marginRight: "3rem" }}
              >
                LinkedIn
              </a>
              <a
                class="navbar-item"
                href="https://bulma.io/"
                style={{ marginRight: "3rem" }}
              >
                Github
              </a>
              <a
                class="navbar-item "
                href="https://bulma.io/"
                style={{ marginRight: "3rem" }}
              >
                Projects
              </a>
              <div class="buttons">
                <a class="button is-primary">
                  <strong>Contact me</strong>
                </a>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </div>
  );
};

export default NavBar;
