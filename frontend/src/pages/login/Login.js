import React, { useState, useEffect } from "react";
import { Form, Input, Button } from 'antd';
import { useDispatch } from 'react-redux';
import './Login.style.css'
import { serverApi } from "../../common/serverApi";
import allActions from "../../actions";


const LoginPage = () => {

  const dispatch = useDispatch();

  const login = async (values) => {
    const respond = await serverApi({ url: '/login', method: 'post', data: values });
    if (respond.data && respond.data.success) {
      // TODO: login and use Redux
      const token = respond.data.access_token;
      const user = respond.data.user;
      dispatch(allActions.userActions.login({
        token: token,
        user: user
      }));
    }
  };

  return (
    <div className='login-page'>
      <div className='form-box'>
        <h1>Login</h1>
        <Form
          className="form"
          layout="vertical"
          name="login"
          onFinish={login}
        >
          <Form.Item
            name="username"
            rules={[
              {
                required: true,
                message: 'Please input your username!',
              },
            ]}
          >
            <Input
              placeholder="Username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              {
                required: true,
                message: 'Please input your password!',
              },
            ]}
          >
            <Input
              type="password"
              placeholder="Password"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" size="large" htmlType="submit">
              Submit
        </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default LoginPage;