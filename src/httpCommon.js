import axios from "axios";
import { apiURL } from "./constants/";
export default axios.create({
  baseURL: `${apiURL}/`,
  headers: {
    "Content-type": "application/json"
  }
});
