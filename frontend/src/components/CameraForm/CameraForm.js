import React, { useState, useEffect } from "react";
import { Form, Input, Button } from 'antd';
import './CameraForm.style.css';
import { serverApiWithToken } from "../../common/serverApi";


const CameraForm = (props) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    console.log('Upload: ', values);
    const respond = await serverApiWithToken({ url: '/camera', data: values, method: 'post' });
    console.log(respond);
    props.cancel();
    props.getData();
  };

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo);
  };

  return (
    <div className='product-form'>
      <h2>Camera form</h2>
      <Form
        form={form}
        layout="vertical"
        requiredMark={true}
        onFinish={onFinish}
        onFinishFailed={onFinishFailed}
      >
        <Form.Item
          name="name"
          label="Name"
          required
          tooltip="Example: Row 1 Column A"
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="password"
          label="Password"
          required
          tooltip="Do not leak it out"
        >
          <Input.Password
            placeholder="Input password"
          />
        </Form.Item>
        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
          >
            Submit
          </Button>
          <Button type="default" onClick={props.cancel}>Cancel</Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default CameraForm;