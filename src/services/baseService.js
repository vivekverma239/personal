import http from "../httpCommon";

export class BaseCRUDService {
  constructor(base) {
    this.base = base;
  }

  getAll = async (params) => {
    return http
      .get(`/${this.base}/`, { params: params })
      .then((res) => res.data);
  };

  get = async (id) => {
    return http.get(`/${this.base}/${id}/`).then((res) => res.data);
  };

  create(data) {
    return http.post(`/${this.base}/`, data).then((res) => res.data);
  }

  update(id, data) {
    return http.put(`/${this.base}/${id}/`, data).then((res) => res.data);
  }

  delete(id) {
    return http.delete(`/${this.base}/${id}/`).then((res) => res.data);
  }

  deleteAll() {
    return http.delete(`/${this.base}/`).then((res) => res.data);
  }
}

export class ChessboardRecService {
  constructor() {
    this.base = "chessboard";
  }

  predict = async (formdata) => {
    return http.post(`/${this.base}/`, formdata).then((res) => res.data);
  };

  getImage = async (id) => {
    return http.get(`/${this.base}/${id}/download`).then((res) => res.data);
  };
}
