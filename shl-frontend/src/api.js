import axios from "axios";

const API_BASE = "http://127.0.0.1:8000" || process.env.VITE_API_BASE;

export const recommend = async (payload) => {
  const res = await axios.post(`${API_BASE}/recommend`, payload);
  return res.data;
};
