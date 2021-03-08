import React, { useState, useEffect } from "react";
import socketIOClient from "socket.io-client";
import './ProductWatcher.css';
import { Menu, Dropdown, Button } from 'antd';
import { DownOutlined, VideoCameraOutlined } from '@ant-design/icons';
import CameraReadyModal from "../../components/CameraReadyModal/CameraReadyModal";
import { serverApiWithToken } from "../../common/serverApi";
import { useDispatch } from "react-redux";
import allActions from "../../actions";

const ENDPOINT = "http://0.0.0.0:5001"


const ProductWatcherPage = () => {
  const [image, setImage] = useState("");
  const [logs, setLogs] = useState([]);
  const [logCounter, setLogCounter] = useState(0);
  const [ready, setReady] = useState(false);
  const [fire, setFire] = useState(false);
  const [cameraList, setCameraList] = useState([]);
  const [camera, setCamera] = useState();
  const dispatch = useDispatch();

  useEffect(() => {
    // handle CCTV image
    const socket = socketIOClient(ENDPOINT);
    if (camera)
      socket.emit('join', { id: camera.id });
    socket.on('image', data => {
      let byteArray = data.image;
      let img = 'data:image/png;base64,' + byteArray
      setImage(img);
    });

    // CLEAN UP THE EFFECT
    if (socket)
      return () => socket.disconnect();
  }, [camera]);

  useEffect(() => {
    // handle CCTV log
    const socket = socketIOClient(ENDPOINT);
    if (camera)
      socket.emit('join', { id: camera.id });
    socket.on('log', data => {
      let new_logs = [...logs];
      console.log(new_logs);
      new_logs.push({ 'id': logCounter, 'log': data.log });
      let a = logCounter + 1;
      setLogCounter(a);
      setLogs(new_logs);
    });

    // CLEAN UP THE EFFECT
    if (socket)
      return () => socket.disconnect();
  }, [logCounter, logs, camera]);

  useEffect(() => {
    // handle image is sending effect
    const socket = socketIOClient(ENDPOINT);
    if (camera)
      socket.emit('join', { id: camera.id });
    socket.on('ready', data => {
      setReady(data.ready);
    });

    // CLEAN UP THE EFFECT
    if (socket)
      return () => socket.disconnect();
  }, [camera]);

  useEffect(() => {
    // handle fire warning
    const socket = socketIOClient(ENDPOINT);
    if (camera)
      socket.emit('join', { id: camera.id });
    socket.on('fire', data => {
      console.log(data.fire);
      setFire(data.fire);
    });

    // CLEAN UP THE EFFECT
    if (socket)
      return () => socket.disconnect();
  }, [camera]);

  useEffect(() => {
    const getAllCamera = async () => {
      let respond = await serverApiWithToken({ url: '/camera/active' });
      if (respond.status === 200 && respond.data.success === true) {
        // console.log(result);
        setCameraList(respond.data.cameras)
      }
      else if (respond.errorCode === 401) {
        dispatch(allActions.userActions.logout());
      }
    }
    getAllCamera();
    const camera_socket = socketIOClient(ENDPOINT);
    camera_socket.on('camera_list', data => {
      console.log(data);
      setCameraList(data.cameras);
      if (data.cameras.length === 0) {
        // Reset
        setCamera(null);
        setReady(false);
        setFire(false);
      }
    });

    // CLEAN UP THE EFFECT
    if (camera_socket)
      return () => camera_socket.disconnect();
  }, []);

  return (
    <div className="content">
      <div className="select-camera">
        <Dropdown
          overlay={(
            <Menu >
              {cameraList.map(cam => <Menu.Item
                key={cam.id}
                icon={<VideoCameraOutlined />}
                onClick={async () => {
                  console.log('Select: ', cam);
                  setCamera(cam);
                  setReady(true);
                }}
              >
                {cam.name}
              </Menu.Item>)}
            </Menu>
          )}
          trigger={['click']}
        >
          <Button>
            {camera ? camera.name : "Select camera"} <DownOutlined />
          </Button>
        </Dropdown>
      </div>
      <h1>Product watcher</h1>
      {/* {ready ? null : <CameraReadyModal />} */}
      {fire ? <div className="fire"><p>Warning!!!!<br />There may be fire</p></div> : null}
      <div className="main" >
        <div className={fire ? "left firebox" : "left"} >
          {ready ? null : <CameraReadyModal />}
          {image === "" ? null : <img src={image} className="image" alt="Img" />}
        </div>
        <div className="right">
          {logs.map((log) => <p className="log" key={log.id}>{log.log}</p>)}
        </div>
      </div>
    </div>
  );
}

export default ProductWatcherPage;
