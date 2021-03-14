import React, { useState, useEffect } from "react";
import './Camera.style.css';
import CameraPanel from "../../components/CameraPanel/CameraPanel";
import CameraForm from "../../components/CameraForm/CameraForm";
import { serverApiWithToken } from "../../common/serverApi";
import { useDispatch } from "react-redux";
import allActions from "../../actions";
import { Button } from 'antd';

const CameraPage = () => {

  const [cameras, setCameras] = useState([]);
  const [add, setAdd] = useState(false);

  const getData = async () => {
    let respond = await serverApiWithToken({ url: '/camera/product' })
    console.log(respond);
    if (respond.status === 200 && respond.data.success === true) {
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
        {add ? < CameraForm
          cancel={() => {
            setAdd(false);
          }}
          getData={getData}
        /> : <Button type="text">
          <span className="func-line" onClick={() => setAdd(true)} >Add camera</span>
        </Button>}
      </div>
    </div>
  );
}

export default CameraPage;