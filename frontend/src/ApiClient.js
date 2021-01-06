import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://0.0.0.0:5001/',
  headers: { "Access-Control-Allow-Origin": "*" }
});