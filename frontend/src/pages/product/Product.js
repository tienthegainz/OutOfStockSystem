import React, { useState, useEffect } from "react";
import { Button } from 'antd';
import ProductPanel from "../../components/ProductPanel/ProductPanel";
import './Product.css';
import ProductForm from "../../components/ProductForm/ProductForm";
import { serverApiWithToken } from "../../common/serverApi";
import { useDispatch } from "react-redux";
import allActions from "../../actions";


const ProductPage = (props) => {

  const [products, setProducts] = useState([]);
  const [add, setAdd] = useState(false);
  const dispatch = useDispatch();

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
          delete={() => {
            const new_products = products.filter(product => product.id !== p.id);
            console.log(new_products);
            setProducts(new_products);
          }}
        />)}
        {add ? <ProductForm
          cancel={() => {
            setAdd(false);
            getData();
          }}
        /> : <Button type="text">
            <span className="func-line" onClick={() => setAdd(true)} >Add products</span>
          </Button>}
      </div>
    </div>
  );
}

export default ProductPage;