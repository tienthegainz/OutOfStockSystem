import axios from 'axios';
import { store } from '../store'


export const serverApi = async ({ url, method = 'get', data = null }) => {
  const ENDPOINT = "http://0.0.0.0:5001";
  const axiosObj = axios.create({
    baseURL: ENDPOINT,
    headers: {
      "Access-Control-Allow-Origin": "*",
    }
  });

  try {
    let result;
    switch (method) {
      case 'post':
        result = await axiosObj.post(url, data, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        break;
      case 'put':
        result = await axiosObj.put(url, data, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        break;
      case 'delete':
        result = await axiosObj.delete(url);
        break;
      case 'patch':
        result = await axiosObj.patch(url, data);
        break;
      default:
        result = await axiosObj.get(url);
        break;
    }
    return result;
  }
  catch (err) {
    return { errorCode: err.response.status };
  }
}

export const serverApiWithToken = async ({ url, method = 'get', data = null }) => {
  const state = store.getState();
  const token = state.currentUser.token;
  if (token === null || token === undefined || token === '')
    return { errorCode: 401 };
  const ENDPOINT = "http://0.0.0.0:5001";
  const axiosObj = axios.create({
    baseURL: ENDPOINT,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Authorization": "Bearer " + token,
    }
  });
  try {
    let result;
    switch (method) {
      case 'post':
        result = await axiosObj.post(url, data, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        break;
      case 'put':
        result = await axiosObj.put(url, data, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        break;
      case 'delete':
        result = await axiosObj.delete(url);
        break;
      case 'patch':
        result = await axiosObj.patch(url, data);
        break;
      default:
        result = await axiosObj.get(url);
        break;
    }
    return result;
  }
  catch (err) {
    return { errorCode: err.response.status };
  }
}