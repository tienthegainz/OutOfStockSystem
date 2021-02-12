import React, { useState, useEffect } from "react";
import { Menu } from 'antd';
import { EyeOutlined, FolderViewOutlined, VideoCameraAddOutlined } from '@ant-design/icons';
import { useLocation, Link } from "react-router-dom";
import './NavBar.css';


const NavBar = (props) => {

  const location = useLocation();
  const activeKeys = [
    { url: '/', key: '1' },
    { url: '/log', key: '2' },
    { url: '/camera', key: '3' },
  ];

  return (
    <div className="nav-bar">
      <h2>Menu</h2>
      <Menu
        selectedKeys={activeKeys.find(e => e.url === location.pathname).key}
        theme='light'
      >
        <Menu.Item key="1" icon={<EyeOutlined />}>
          <Link to="/">CCTV</Link>
        </Menu.Item>
        <Menu.Item key="2" icon={<FolderViewOutlined />}>
          <Link to="/log">Log</Link>
        </Menu.Item>
        <Menu.Item key="3" icon={<VideoCameraAddOutlined />}>
          <Link to="/camera">Camera</Link>
        </Menu.Item>
      </Menu>
    </div>
  );
}

export default NavBar;