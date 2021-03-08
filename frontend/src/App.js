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

const App = () => {
  const userInfo = useSelector(state => state.currentUser);

  return (<React.Fragment>
    {userInfo.isLoggedIn ? <Router>
      <NavBar />
      <Switch>
        <Route path="/log">
          <LogPage />
        </Route>
        <Route path="/camera">
          <CameraPage />
        </Route>
        <Route path="/product">
          <ProductPage />
        </Route>
        <Route path="/">
          <ProductWatcherPage />
        </Route>
      </Switch>
    </Router> : <LoginPage />}
  </React.Fragment >
  );
}

export default App;
