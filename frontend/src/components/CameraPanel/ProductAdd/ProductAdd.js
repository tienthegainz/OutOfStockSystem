import React, { useState, useEffect } from "react";
import './ProductAdd.css';
import { Menu, Button, Dropdown } from 'antd';
import { DownOutlined } from '@ant-design/icons';

const ProductAdd = (props) => {

  const [data, setData] = useState({ id: null })
  const allProducts = [
    {
      id: 1,
      name: "Gucci Guilt INTENSE"
    },
    {
      id: 2,
      name: "Water bottle"
    }
  ]

  const menu = () => <Menu>
    {allProducts.map((e) => <Menu.Item key={e.id} onClick={() => setData(e)} >{e.name}</Menu.Item>)}
  </Menu>;

  return (
    <div className="add-box" >
      <p>Add new product: </p>
      <Dropdown overlay={menu} placement="bottomLeft">
        <Button>{data.id === null ? "Choose product" : data.name}<DownOutlined /></Button>
      </Dropdown>
      <Button type="primary" style={{ marginLeft: "10px" }} >Confirm</Button>
    </div>
  );
}

export default ProductAdd;