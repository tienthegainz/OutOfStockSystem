import React, { useState, useEffect } from "react";
import { Button } from 'antd';
import ProductPanel from "../../components/ProductPanel/ProductPanel";
import './Product.css';
import ProductForm from "../../components/ProductForm/ProductForm";
import { serverApiWithToken } from "../../common/serverApi";


const ProductPage = (props) => {

  const [products, setProducts] = useState([]);
  const [add, setAdd] = useState(false);

  const getData = async () => {
    let respond = await serverApiWithToken({ url: '/product' })
    console.log(respond);
    if (respond.status === 200 && respond.data.success === true) {
      let data = respond.data.products;
      setProducts(data);
    }
  };

  useEffect(() => {
    getData();
  }, [])

  return (
    <div className="content">
      <h1>Product management</h1>
      <div class="product">
        {products.map(p => <ProductPanel
          data={p}
          key={p.id}
          getData={getData}
        />)}
        {add ? <ProductForm
          cancel={() => {
            setAdd(false);
          }}
          getData={getData}
        /> : <Button type="text">
            <span className="func-line" onClick={() => setAdd(true)} >Add products</span>
          </Button>}
      </div>
    </div>
  );
}

export default ProductPage;