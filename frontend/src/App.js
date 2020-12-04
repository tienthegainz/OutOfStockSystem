import React, { useState, useEffect } from "react";
import socketIOClient from "socket.io-client";
import './App.style.css';

const ENDPOINT = "http://0.0.0.0:5001"
const axios = require('axios');

const App = () => {
  const [image, setImage] = useState("");
  const [logs, setLogs] = useState([]);
  const [logCounter, setLogCounter] = useState(0);
  const [ready, setReady] = useState(false);
  const [fire, setFire] = useState(true);

  useEffect(() => {
    const socket = socketIOClient(ENDPOINT);
    socket.on('image', data => {
      let byteArray = data.image;
      let img = 'data:image/png;base64,' + byteArray
      setImage(img);
    });

    // CLEAN UP THE EFFECT
    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    const socket = socketIOClient(ENDPOINT);
    socket.on('log', data => {
      let new_logs = [...logs];
      console.log(new_logs);
      new_logs.push({ 'id': logCounter, 'log': data.log });
      let a = logCounter + 1;
      setLogCounter(a);
      setLogs(new_logs);
    });

    // CLEAN UP THE EFFECT
    return () => socket.disconnect();
  }, [logCounter, logs]);

  useEffect(() => {
    const socket = socketIOClient(ENDPOINT);
    socket.on('ready', data => {
      setReady(data.ready);
    });

    // CLEAN UP THE EFFECT
    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    const socket = socketIOClient(ENDPOINT);
    socket.on('fire', data => {
      setFire(data.fire);
    });

    // CLEAN UP THE EFFECT
    return () => socket.disconnect();
  }, []);

  return (
    <div>
      <h1 className="title">Product watcher</h1>
      {ready ? null : <p className="ready"><i className="fa fa-refresh fa-spin" /> Booting</p>}
      {fire ? <div className="fire"><p>Warning!!!!<br />There may be fire</p></div> : null}
      <div className="main" >
        <div className="left">
          <img src={image} className="image" alt="Img" />
        </div>
        <div className="right">
          {logs.map((log) => <p className="log" key={log.id}>{log.log}</p>)}
        </div>
      </div>
    </div>
  );
}

export default App;
