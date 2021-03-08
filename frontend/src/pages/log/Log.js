import React, { useState, useEffect } from "react";
import './Log.css';
import { Tabs, DatePicker, Menu, Dropdown, Button } from 'antd';
import { DownOutlined, VideoCameraOutlined } from '@ant-design/icons';
import ImageLog from "../../components/image_log/ImageLog";
import LogBox from "../../components/LogBox/LogBox";
import { serverApiWithToken } from "../../common/serverApi";
import { useDispatch } from "react-redux";
import allActions from "../../actions";

const { TabPane } = Tabs;

const LogPage = () => {

  const [date, setDate] = useState();
  const [allCamera, setAllCamera] = useState([]);
  const [camera, setCamera] = useState();
  // 0: not clicked, 1: ok, -1: error
  const [check, setCheck] = useState(0);
  const dispatch = useDispatch();

  useEffect(() => {
    const getData = async () => {
      let respond = await serverApiWithToken({ url: '/camera' })
      console.log(respond);
      if (respond.status === 200 && respond.data.success === true) {
        let data = respond.data.cameras;
        setAllCamera(data);
      }
      else if (respond.errorCode === 401) {
        dispatch(allActions.userActions.logout());
      }
    };
    getData();
  }, [])

  return (<div className="content" style={{ width: '92%', marginLeft: '8%' }} >
    <div className='log-form' >
      <h2>Pick camera and date to check</h2>

      <DatePicker
        size='large'
        onChange={(date, dateString) => {
          console.log(date, dateString);
          setDate(dateString);
          setCheck(0);
        }}
        format='YYYY/MM/DD'
        style={{ marginBottom: '15px', width: '100%' }}
      />
      <Dropdown
        overlay={(
          <Menu >
            {allCamera.map(c => <Menu.Item
              icon={<VideoCameraOutlined />}
              onClick={async () => {
                setCamera(c);
                setCheck(0);
              }}
            >
              {c.name}
            </Menu.Item>)}
          </Menu>
        )}
        trigger={['click']}
        style={{ marginBottom: '15px', width: '100%' }}
      >
        <Button style={{ marginBottom: '15px', width: '100%' }} >
          {camera ? camera.name : "Select camera"}<DownOutlined />
        </Button>
      </Dropdown>
      <Button
        type="primary"
        style={{ marginBottom: '15px', width: '40%' }}
        onClick={() => {
          if (date && camera) setCheck(1);
          else setCheck(-1)
        }}
      >
        Check
      </Button>
      {(check === -1) ? <div className='error' >Please fill all info required</div> : null}
    </div>
    <Tabs
      defaultActiveKey={1}
      centered={true}
    >
      <TabPane tab="Image log" key={1}>
        <ImageLog
          query={(check === 1)}
          date={date}
          cameraId={camera}
        />
      </TabPane>
      <TabPane tab="Text log" key={2}>
        <LogBox
          query={(check === 1)}
          date={date}
          cameraId={camera}
        />
      </TabPane>
    </Tabs>
  </div>);
}

export default LogPage;