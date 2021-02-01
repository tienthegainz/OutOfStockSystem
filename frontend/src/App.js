import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import ProductWatcherPage from './pages/product_watcher/ProductWatcher';
import ImageLogPage from './pages/image_log/ImageLog';
import CameraPage from './pages/camera/Camera';
import NavBar from "./components/NavBar/NavBar";
import "./App.css";

const App = () => {

  return (
    <Router>
      <NavBar />
      <Switch>
        <Route path="/image">
          <ImageLogPage />
        </Route>
        <Route path="/camera">
          <CameraPage />
        </Route>
        <Route path="/">
          <ProductWatcherPage />
        </Route>
      </Switch>

    </Router>
  );
}

export default App;
