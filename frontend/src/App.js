import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import ProductWatcher from './pages/product_watcher/ProductWatcher';
import ImageLog from './pages/image_log/ImageLog';
import NavBar from "./components/NavBar/NavBar";


const App = () => {

  return (
    <Router>
      <NavBar />
      <Switch>
        <Route path="/image">
          <ImageLog />
        </Route>
        <Route path="/">
          <ProductWatcher />
        </Route>
      </Switch>

    </Router>
  );
}

export default App;
