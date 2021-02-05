import axios from 'axios';


export const serverApi = async ({ url, method = 'get', data = null }) => {
  const ENDPOINT = "http://0.0.0.0:5001";
  const request = async ({ url, method, data }) => {
    const axiosObj = axios.create({
      baseURL: ENDPOINT,
      headers: {
        "Access-Control-Allow-Origin": "*",
      }
    });

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
  };
  try {
    let result = await request({ url: url, method: method, data: data });
    return result;
  }
  catch (err) {
    return { error: err.response.status };
  }
}