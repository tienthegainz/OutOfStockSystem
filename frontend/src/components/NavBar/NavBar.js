import React, { useState, useEffect } from "react";
import { Menu } from 'antd';
import {
  EyeOutlined, FolderViewOutlined,
  VideoCameraAddOutlined, AppstoreAddOutlined,
  LogoutOutlined, UserOutlined
} from '@ant-design/icons';
import { useLocation, Link } from "react-router-dom";
import './NavBar.css';
import { useDispatch, useSelector } from "react-redux";
import allActions from "../../actions";


const NavBar = (props) => {

  const location = useLocation();
  const dispatch = useDispatch();
  const isAdmin = useSelector(state => state.currentUser.user.admin);
  const activeKeys = [
    { url: '/', key: '1' },
    { url: '/log', key: '2' },
    { url: '/camera', key: '3' },
    { url: '/product', key: '4' },
    { url: '/user', key: '5' },
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
        <Menu.Item key="4" icon={<AppstoreAddOutlined />}>
          <Link to="/product">Product</Link>
        </Menu.Item>
        {isAdmin ? <Menu.Item key="5" icon={<UserOutlined />}>
          <Link to="/user">User</Link>
        </Menu.Item> : null}
        <Menu.Item
          key="6"
          icon={<LogoutOutlined />}
          onClick={() => {
            dispatch(allActions.userActions.logout());
          }}
        >
          Logout
        </Menu.Item>
      </Menu>
    </div>
  );
}

export default NavBar;