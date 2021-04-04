import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
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

const App = () => {
  const userInfo = useSelector(state => state.currentUser);
  const notiInfo = useSelector(state => state.notification);
  const dispatch = useDispatch();

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
  }, [notiInfo]);

  return (<React.Fragment>
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
