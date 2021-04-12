import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import { io } from "socket.io-client";
import ProductWatcherPage from './pages/product_watcher/ProductWatcher';
import CameraPage from './pages/camera/Camera';
import NavBar from "./components/NavBar/NavBar";
import "./App.css";
import LogPage from "./pages/log/Log";
import ProductPage from "./pages/product/Product";
import LoginPage from "./pages/login/Login";
import { useDispatch, useSelector } from 'react-redux';
import UserPage from "./pages/employee/Employee";
import { notification } from 'antd';
import allActions from "./actions";
import Notification from "react-web-notification";

const ENDPOINT = "http://0.0.0.0:5001"

const App = () => {
  const userInfo = useSelector(state => state.currentUser);
  const notiInfo = useSelector(state => state.notification);
  const dispatch = useDispatch();
  const [notiMessage, setNotiMessage] = useState({
    title: "",
    message: "",
    display: false
  });

  const openNotification = (title, message) => {
    notification.error({
      message: title,
      description: message,
      duration: 3,
      placement: 'bottomRight'
    });
  };

  useEffect(() => {
    if (notiInfo.trigger) {
      openNotification(notiInfo.title, notiInfo.message);
      dispatch(allActions.notiActions.cancel());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [notiInfo]);

  useEffect(() => {
    const camera_socket = io(ENDPOINT);
    camera_socket.on('noti', data => {
      console.log({ ...data, display: true });
      setNotiMessage({ ...data, display: true });
    });

    // CLEAN UP THE EFFECT
    if (camera_socket)
      return () => camera_socket.disconnect();
  }, []);


  return (<React.Fragment>
    {notiMessage.display ? <Notification
      ignore={false}
      timeout={0}
      title={notiMessage.title}
      options={
        {
          body: notiMessage.message
        }
      }
    /> : null}
    {userInfo.isLoggedIn ? <Router>
      <NavBar />
      <Switch>
        <Route exact path="/log">
          <LogPage />
        </Route>
        <Route exact path="/camera">
          <CameraPage />
        </Route>
        <Route exact path="/product">
          <ProductPage />
        </Route>
        <Route exact path="/product">
          <ProductPage />
        </Route>
        <Route exact path="/user">
          <UserPage />
        </Route>
        <Route exact path={["/", "/watcher"]} >
          <ProductWatcherPage />
        </Route>
      </Switch>
    </Router> : <LoginPage />}
  </React.Fragment >
  );
}

export default App;
