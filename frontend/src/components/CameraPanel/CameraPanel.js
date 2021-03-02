import React, { useState, useEffect } from "react";
import './CameraPanel.css';
import { Collapse, Button } from 'antd';
import ProductAdd from "./ProductAdd/ProductAdd";
import CameraTable from "../CameraTable/CameraTable";

const { Panel } = Collapse;

const CameraPanel = (props) => {

  const [edit, setEdit] = useState(false);


  return (
    <Collapse style={{ marginBottom: "10px" }} >
      <Panel header={props.data.name}>
        <h2>Tracking products:</h2>
        <CameraTable data={props.data.products} cameraId={props.data.id} getData={props.getData} />
        {edit ? <ProductAdd
          cameraId={props.data.id}
          collapse={() => setEdit(false)}
          getData={props.getData}
        /> : null}
        <Button type="text" onClick={() => setEdit(!edit)}>
          <span className="func-line">{edit ? "Cancel" : "Add products"}</span>
        </Button>
      </Panel>
    </Collapse>
  );
}

export default CameraPanel;