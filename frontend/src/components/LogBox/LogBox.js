import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import allActions from "../../actions";
import { serverApiWithToken } from "../../common/serverApi";
import './LogBox.css';


const LogBox = (props) => {

  const [logs, setLogs] = useState([]);
  const dispatch = useDispatch();

  useEffect(() => {
    const getData = async (id, date) => {
      const data = {
        "from": date + " 00:00:00",
        "to": date + " 23:59:99"
      };
      let respond = await serverApiWithToken({ url: '/log/text/' + id, data: data, method: 'post' })
      console.log(respond);
      if (respond.status === 200 && respond.data.success === true) {
        setLogs(respond.data.data);
      }
    };
    if (props.query && props.cameraId.id)
      getData(props.cameraId.id, props.date);
  }, [props]);

  return (<React.Fragment>
    <h1>Text Log</h1>
    <div className="box" >
      {logs.map((log) => <p className="log" key={log.id}>{log.message}</p>)}
    </div>
  </React.Fragment>);
}

export default LogBox;