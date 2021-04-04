import React, { useState, useEffect } from "react";
import { Form, Input, Button } from 'antd';
import './RegisterForm.style.css'
import { serverApiWithToken } from "../../common/serverApi";


const RegisterForm = (props) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    let respond = await serverApiWithToken({
      url: '/register',
      data: values,
      method: 'post'
    })
    console.log(respond);
    if (respond.status === 200 && respond.data.success === true) {
      props.getData();
    }
    props.cancel();
  };

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo);
  };

  return (
    <div>
      <h2>Employee register</h2>
      <Form
        form={form}
        layout="vertical"
        requiredMark={true}
        onFinish={onFinish}
        onFinishFailed={onFinishFailed}
      >
        <Form.Item
          name="username"
          label="Username"
          required
          tooltip="The username must be unique"
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="password"
          label="Password"
          required
          tooltip="Do not show password to other"
        >
          <Input.Password
            placeholder="input password"
          />
        </Form.Item>
        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            style={{ marginRight: '10px' }}
          >
            Submit
          </Button>
          <Button type="default" onClick={props.cancel}>Cancel</Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default RegisterForm;