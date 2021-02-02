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
