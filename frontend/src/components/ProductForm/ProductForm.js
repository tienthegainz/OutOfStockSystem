import React, { useState, useEffect } from "react";
import { Form, Input, Button, Upload } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import './ProductForm.css'

const normFile = (e) => {
  console.log('Upload event:', e);
  if (Array.isArray(e)) {
    return e;
  }
  return e && e.fileList;
};

const dummyRequest = ({ file, onSuccess }) => {
  setTimeout(() => {
    onSuccess("ok");
  }, 0);
};

const ProductForm = (props) => {
  const [form] = Form.useForm();

  const onFinish = (values) => {
    console.log('Success:', values);
  };

  const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo);
  };

  return (
    <div className='product-form'>
      <h2>Product form</h2>
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
          tooltip="The product name must be unique"
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="price"
          label="Price"
          required
          tooltip="Price in VND"
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="upload"
          label="Upload"
          required
          tooltip="Recommend 3-4 image"
          valuePropName="fileList"
          getValueFromEvent={normFile}
        >
          <Upload
            name="logo"
            listType="picture"
            customRequest={dummyRequest}
          >
            <Button icon={<UploadOutlined />}>Click to upload</Button>
          </Upload>
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">Submit</Button>
          <Button type="default" onClick={props.cancel}>Cancel</Button>
        </Form.Item>
      </Form>
    </div>
  );
}

export default ProductForm;