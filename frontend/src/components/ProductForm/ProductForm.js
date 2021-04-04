import React, { useState, useEffect } from "react";
import { Form, Input, InputNumber, Button, Upload } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import './ProductForm.css'
import { serverApiWithToken } from "../../common/serverApi";


const normFile = (e) => {
  // console.log('Upload: ', e)
  return e.fileList;
};

const dummyRequest = ({ file, onSuccess }) => {
  setTimeout(() => {
    onSuccess("ok");
  }, 0);
};

const getBase64 = (file) => {
  return new Promise(function (resolve) {
    var reader = new FileReader();
    reader.onloadend = function () {
      resolve(reader.result)
    }
    reader.readAsDataURL(file);
  })
}

const ProductForm = (props) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = (values) => {
    const upload = async (values) => {
      setLoading(true);
      let images = values.images;
      for (const key in images) {
        let f = images[key].originFileObj;
        images[key] = await getBase64(f);
      }
      values.images = images;
      console.log('Upload: ', values);
      const respond = await serverApiWithToken({ url: '/product', data: values, method: 'post' });
      console.log(respond);
      props.getData();
      props.cancel();
    }
    upload(values);
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
          <InputNumber
            formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
            parser={value => value.replace(/\$\s?|(,*)/g, '')}
            style={{ width: '50%' }}
          />
        </Form.Item>
        <Form.Item
          name="images"
          label="Upload"
          required
          tooltip="Recommend 3 to 4 image"
          valuePropName="fileList"
          getValueFromEvent={normFile}
        >
          <Upload
            name="product"
            listType="picture"
            customRequest={dummyRequest}
          >
            <Button icon={<UploadOutlined />}>Click to upload</Button>
          </Upload>
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

export default ProductForm;