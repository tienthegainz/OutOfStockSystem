import React, { useState, useEffect } from "react";
import './Log.css';
import { Tabs } from 'antd';
import ImageLog from "../../components/image_log/ImageLog";

const { TabPane } = Tabs;

const LogPage = () => {

  return (<div className="content">
    <Tabs
      defaultActiveKey={1}
      centered={true}
    >
      <TabPane tab="Image log" key={1}>
        <ImageLog />
      </TabPane>
      <TabPane tab="Text log" key={2}>
        Text log
      </TabPane>
    </Tabs>
  </div>);
}

export default LogPage;