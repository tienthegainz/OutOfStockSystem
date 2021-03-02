import React, { useState, useEffect } from "react";
import './Camera.css';
import CameraPanel from "../../components/CameraPanel/CameraPanel";
import { serverApi } from "../../common/serverApi";

const CameraPage = () => {

  const [cameras, setCameras] = useState([]);

  const getData = async () => {
    let respond = await serverApi({ url: '/camera/product' })
    console.log(respond);
    if (respond.status === 200) {
      let data = respond.data.cameras;
      setCameras(data);
    }
  };

  useState(() => {
    getData();
  }, []);

  return (
    <div className="content">
      <h1>Camera management</h1>
      <div className="camera">
        {cameras.map(c => <CameraPanel data={c} key={c.id} getData={getData} />)}
      </div>
    </div>
  );
}

export default CameraPage;