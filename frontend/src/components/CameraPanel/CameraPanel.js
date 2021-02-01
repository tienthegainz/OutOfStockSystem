import React, { useState, useEffect } from "react";
import './CameraPanel.css';
import { Collapse, InputNumber, Button } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import ProductAdd from "./ProductAdd/ProductAdd";

const { Panel } = Collapse;

const CameraPanel = (props) => {

  const [edit, setEdit] = useState(false);


  return (
    <Collapse style={{ marginBottom: "10px" }} >
      <Panel header={props.camera.name}>
        <h2>Tracking product:</h2>
        <Collapse>
          {props.camera.objects.map((p, idx) => <Panel
            header={p.name}
            key={idx}
            extra={edit ? <DeleteOutlined
              onClick={event => {
                // If you don't want click extra trigger collapse, you can prevent this:
                event.stopPropagation();
                console.log('Delete');
              }}
              style={{ color: "red" }}
            /> : null}
          >
            <div className="product-spec">
              <h3>Name:</h3>
              <p>{p.name}</p>
              <h3>Quantity:</h3>
              {edit ? <InputNumber min={1} defaultValue={p.quantity} /> : <p>{p.quantity}</p>}
              <h3>Price:</h3>
              <p>{p.price} VND</p>
              <h3>Image:</h3>
              <img src={p.img} alt="preview" />
              {edit ? <Button
                type="primary"
                style={{
                  textAlign: "center",
                  fontSize: "20px",
                  width: "fit-content",
                  height: "fit-content",
                  margin: "auto"
                }}
              >Confirm</Button> : null}
            </div>
          </Panel>)}
        </Collapse>
        {edit ? <ProductAdd /> : null}
        <Button type="text" onClick={() => setEdit(!edit)}>
          <span className="func-line">{edit ? "Cancel" : "Add/Remove tracking objects"}</span>
        </Button>
      </Panel>
    </Collapse>
  );
}

export default CameraPanel;