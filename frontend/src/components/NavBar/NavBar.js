import React, { useState, useEffect } from "react";
import { Menu } from 'antd';
import { EyeOutlined, FolderViewOutlined } from '@ant-design/icons';
import { useLocation, Link } from "react-router-dom";
import './NavBar.css';


const NavBar = (props) => {

  const location = useLocation();

  return (
    <div className="nav-bar">
      <h2>Menu</h2>
      <Menu
        selectedKeys={location.pathname === '/image' ? ['2'] : ['1']}
        theme='light'
      >
        <Menu.Item key="1" icon={<EyeOutlined />}>
          <Link to="/">CCTV</Link>
        </Menu.Item>
        <Menu.Item key="2" icon={<FolderViewOutlined />}>
          <Link to="/image">Image Log</Link>
        </Menu.Item>
      </Menu>
    </div>
  );
}

export default NavBar;