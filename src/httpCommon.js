import axios from "axios";

export default axios.create({
  baseURL: "http://0.0.0.0:8005/",
  headers: {
    "Content-type": "application/json",
  },
});
