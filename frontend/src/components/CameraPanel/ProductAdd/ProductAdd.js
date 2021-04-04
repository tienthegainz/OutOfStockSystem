import React, { useState, useEffect } from "react";
import './ProductAdd.css';
import { Menu, Button, Dropdown, InputNumber } from 'antd';
import { DownOutlined } from '@ant-design/icons';
import { serverApiWithToken } from "../../../common/serverApi";
import { useDispatch } from "react-redux";
import allActions from "../../../actions";

const ProductAdd = (props) => {

  const [data, setData] = useState({ id: null });
  const [allProducts, setAllProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();

  useEffect(() => {
    const getProduct = async () => {
      let respond = await serverApiWithToken({ url: 'product' })
      console.log(respond);
      if (respond.status === 200 && respond.data.success === true) {
        let data = respond.data.products.map(p => { return { id: p.id, name: p.name }; });
        setAllProducts(data);
      }
    }
    getProduct();
  }, [])

  return (
    <div className="add-box" >
      <p>Add new product: </p>
      <Dropdown
        overlay={<Menu>
          {allProducts.map((e) => <Menu.Item key={e.id} onClick={() => setData(e)} >{e.name}</Menu.Item>)}
        </Menu>}
        placement="bottomLeft"
        style={{ marginRight: '10px' }}
      >
        <Button style={{ marginRight: '10px' }} >{data.id === null ? "Choose product" : data.name}<DownOutlined /></Button>
      </Dropdown>
      <InputNumber min={1} max={5}
        style={{ marginRight: '10px' }}
        onChange={(value) => setData({ ...data, quantity: value })}
      />
      <Button type="primary"
        disabled={!(data.id && data.quantity)}
        loading={loading}
        onClick={async () => {
          setLoading(true);
          let respond = await serverApiWithToken({
            url: '/camera/product',
            data: {
              camera_id: props.cameraId,
              product_id: data.id,
              quantity: data.quantity
            },
            method: 'post'
          })
          console.log(respond);
          if (respond.status === 200) {
            props.getData();
          }
          props.collapse();
        }}
      >
        Confirm
      </Button>
    </div>
  );
}

export default ProductAdd;