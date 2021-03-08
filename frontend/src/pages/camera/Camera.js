import React, { useState, useEffect } from "react";
import './Camera.css';
import CameraPanel from "../../components/CameraPanel/CameraPanel";
import { serverApiWithToken } from "../../common/serverApi";
import { useDispatch } from "react-redux";
import allActions from "../../actions";

const CameraPage = () => {

  const [cameras, setCameras] = useState([]);
  const dispatch = useDispatch();

  const getData = async () => {
    let respond = await serverApiWithToken({ url: '/camera/product' })
    console.log(respond);
    if (respond.status === 200 && respond.data.success === true) {
      let data = respond.data.cameras;
      setCameras(data);
    }
    else if (respond.errorCode === 401) {
      dispatch(allActions.userActions.logout());
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