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
import { useSelector } from 'react-redux';
import UserPage from "./pages/user/User";

const App = () => {
  const userInfo = useSelector(state => state.currentUser);

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
