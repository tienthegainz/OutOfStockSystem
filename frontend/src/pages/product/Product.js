import React, { useState, useEffect } from "react";
import { Button } from 'antd';
import ProductPanel from "../../components/ProductPanel/ProductPanel";
import './Product.css';
import ProductForm from "../../components/ProductForm/ProductForm";


const ProductPage = (props) => {

  const [products, setProducts] = useState([
    {
      id: 1,
      name: "Gucci Guilt INTENSE",
      price: 1500000,
      img: "https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F1.jpeg?alt=media"
    },
    {
      id: 2,
      name: "Water bottle",
      price: 10000,
      img: "https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F2.png?alt=media"
    }
  ]);
  const [add, setAdd] = useState(false);

  return (
    <div className="content">
      <h1>Product management</h1>
      <div class="product">
        {products.map(p => <ProductPanel data={p} key={p.id} />)}
        {add ? <ProductForm cancel={() => setAdd(false)} /> : <Button type="text">
          <span className="func-line" onClick={() => setAdd(true)} >Add products</span>
        </Button>}
      </div>
    </div>
  );
}

export default ProductPage;