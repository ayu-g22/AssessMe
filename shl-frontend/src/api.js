import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export const recommend = async (payload) => {
  const res = await axios.post(`${API_BASE}/recommend`, payload);
  return res.data;
};
