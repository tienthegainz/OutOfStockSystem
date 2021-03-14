import React, { useState, useEffect } from "react";
import './CameraPanel.css';
import { Collapse, Button, Space, Input } from 'antd';
import { DeleteOutlined, EditOutlined, CheckOutlined, StopOutlined } from '@ant-design/icons';
import ProductAdd from "./ProductAdd/ProductAdd";
import CameraTable from "../CameraTable/CameraTable";
import DeleteModal from "../DeleteModal/DeleteModal";
import EditModal from "../EditModal/EditModal";
import { serverApiWithToken } from "../../common/serverApi";

const { Panel } = Collapse;

const CameraPanel = (props) => {

  const [add, setAdd] = useState(false);
  const [edit, setEdit] = useState(false);
  const [editData, setEditData] = useState({});
  const [editConfirm, setEditConfirm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);


  return (
    <React.Fragment>
      {deleteConfirm ? <DeleteModal
        visible={true}
        ok={async () => {
          let respond = await serverApiWithToken({ url: '/camera/' + props.data.id, method: 'delete' });
          console.log(respond);
          setDeleteConfirm(false);
          props.getData();
        }}
        cancel={() => setDeleteConfirm(false)}
        name={props.data.name}
      /> : null}
      {editConfirm ? <EditModal
        visible={true}
        ok={async () => {
          let respond = await serverApiWithToken({
            url: '/camera/' + props.data.id,
            data: editData,
            method: 'put'
          });
          console.log(respond);
          setEditConfirm(false);
          props.getData();
          setEdit(false);
        }}
        cancel={() => setDeleteConfirm(false)}
        name={props.data.name}
      /> : null}
      <Collapse style={{ marginBottom: "10px" }} >
        <Panel
          header={props.data.name}
          extra={
            edit ?
              <Space size="middle">
                <CheckOutlined
                  style={{ color: 'green' }}
                  onClick={() => {
                    setEditConfirm(true);
                  }}
                />
                <StopOutlined
                  style={{ color: 'red' }}
                  onClick={() => {
                    setEdit(false);
                    setEditData({});
                  }}
                />
              </Space> :
              <Space size="middle">
                <EditOutlined
                  onClick={(event) => {
                    event.stopPropagation();
                    setEdit(true);
                  }}
                />
                <DeleteOutlined
                  onClick={async (event) => {
                    event.stopPropagation();
                    setDeleteConfirm(true);
                  }}
                  style={{ color: "red" }}
                />
              </Space>
          }
        >
          {edit ?
            <React.Fragment>
              <h3>Name:</h3>
              <Input
                style={{ width: '50%' }}
                defaultValue={props.data.name}
                onChange={(e) => {
                  setEditData({ ...editData, name: e.target.value });
                }}
              />
              <h3>Password:</h3>
              <Input.Password
                style={{ width: '50%' }}
                onChange={(e) => {
                  setEditData({ ...editData, password: e.target.value });
                }}
              />
            </React.Fragment>
            : null
          }
          <h2>Tracking products:</h2>
          <CameraTable data={props.data.products} cameraId={props.data.id} getData={props.getData} />
          {add ? <ProductAdd
            cameraId={props.data.id}
            collapse={() => setAdd(false)}
            getData={props.getData}
          /> : null}
          <Button type="text" onClick={() => setAdd(!add)}>
            <span className="func-line">{add ? "Cancel" : "Add products"}</span>
          </Button>
        </Panel>
      </Collapse>
    </React.Fragment>
  );
}

export default CameraPanel;