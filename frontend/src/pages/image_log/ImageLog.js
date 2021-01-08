import React, { useState, useEffect } from "react";
import './ImageLog.css';
import ImageCard from '../../components/ImageCard/ImageCard';
import axios from 'axios';

const ImageLog = () => {

  const [images, setImages] = useState([[]]);

  const renderImage = (data) => {
    let arr = [];
    let i, chunk = 4;
    const j = data.length;
    for (i = 0; i < j; i += chunk) {
      let rowImage = data.slice(i, i + chunk);
      arr.push(rowImage);
    }
    return arr;
  }

  useEffect(() => {
    const getData = async () => {
      const axiosObj = axios.create({
        baseURL: 'http://0.0.0.0:5001/',
        headers: {
          "Access-Control-Allow-Origin": "*"
        }
      });
      const respond = await axiosObj.get('product/log');
      console.log(respond);
      if (respond.status === 200) {
        setImages(renderImage(respond.data.data));
      }
    };
    getData();
  }, []);

  return (
    <div className="content">
      <h1>Image Log</h1>
      <div className="content">
        {images.map(row => {
          return (<div className="row">
            {row.map(img => { return <ImageCard url={img.url} time={img.time} /> })}
          </div>)
        })}
      </div>
    </div>
  );
}

export default ImageLog;