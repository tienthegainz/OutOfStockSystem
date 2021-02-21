import React, { useState, useEffect } from "react";
import './ProductPanel.css';
import { Collapse, Button } from 'antd';
import { DeleteOutlined, LeftOutlined, RightOutlined, EditOutlined } from '@ant-design/icons';

const { Panel } = Collapse;

const ProductPanel = (props) => {

  const [edit, setEdit] = useState(false);

  return (<Collapse>
    <Panel
      header={props.data.name}
      key={props.data.id}
      extra={edit ? <DeleteOutlined
        onClick={event => {
          // If you don't want click extra trigger collapse, you can prevent this:
          event.stopPropagation();
          console.log('Delete');
        }}
        style={{ color: "red" }}
      /> : <EditOutlined
          onClick={(event) => {
            // If you don't want click extra trigger collapse, you can prevent this:
            event.stopPropagation();
            console.log('Delete');
            setEdit(true);
          }}
        />}
      style={{ marginBottom: '10px' }}
    >
      <div className="product-spec">
        <h3>Name:</h3>
        <p>{props.data.name}</p>
        <h3>Price:</h3>
        <p>{props.data.price} VND</p>
        <h3>Images:</h3>
        <div className='img-list'>
          <Button
            type="primary"
            shape="circle"
            icon={<LeftOutlined />}
            disabled={true}
          />
          <div className='img-space'>
            {props.data.images.map(img => <img className='tree-img' src={img} alt="preview" />)}
          </div>
          <Button
            type="primary"
            shape="circle"
            icon={<RightOutlined />}
            disabled={true}
          />
        </div>
        <span>*Note: 3-4 images per products is recommended</span>
        {edit ? <Button
          type="primary"
          style={{
            textAlign: "center",
            fontSize: "20px",
            width: "fit-content",
            height: "fit-content",
            margin: "auto"
          }}
          onClick={() => setEdit(false)}
        >Confirm</Button> : null}
      </div>
    </Panel>
  </Collapse >
  );
}

export default ProductPanel;