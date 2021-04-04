import React, { useState, useEffect } from "react";
import './ProductPanel.css';
import { Collapse, Button, Space, Input, InputNumber } from 'antd';
import { DeleteOutlined, LeftOutlined, RightOutlined, EditOutlined, CheckOutlined, StopOutlined } from '@ant-design/icons';
import { serverApiWithToken } from "../../common/serverApi";
import DeleteModal from "../DeleteModal/DeleteModal";
import EditModal from "../EditModal/EditModal";

const { Panel } = Collapse;

const ProductPanel = (props) => {

  const [edit, setEdit] = useState(false);
  const [editData, setEditData] = useState({});
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [editConfirm, setEditConfirm] = useState(false);

  return (<React.Fragment>
    {deleteConfirm ? <DeleteModal
      visible={true}
      ok={async () => {
        let respond = await serverApiWithToken({ url: '/product/' + props.data.id, method: 'delete' });
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
          url: '/product/' + props.data.id,
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
    <Collapse>
      <Panel
        header={props.data.name}
        key={props.data.id}
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
                  setEditData(props.data);
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
        style={{ marginBottom: '10px' }}
      >
        <div className="product-spec">
          <h3>Name:</h3>
          {edit ?
            <Input
              style={{ width: '50%' }}
              defaultValue={props.data.name}
              onChange={(e) => {
                setEditData({ ...editData, name: e.target.value });
              }}
            />
            :
            <p>{props.data.name}</p>
          }
          <h3>Price:</h3>
          {edit ?
            <InputNumber
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/\$\s?|(,*)/g, '')}
              style={{ width: '50%' }}
              defaultValue={props.data.price}
              onChange={(value) => {
                setEditData({ ...editData, price: value });
              }}
            /> :
            <p>{props.data.price} VND</p>
          }
          <h3>Images:</h3>
          <div className='img-list'>
            <Button
              type="primary"
              shape="circle"
              icon={<LeftOutlined />}
              disabled={true}
            />
            <div className='img-space'>
              {props.data.images.map(img => <img className='tree-img' src={img.url} alt="preview" />)}
            </div>
            <Button
              type="primary"
              shape="circle"
              icon={<RightOutlined />}
              disabled={true}
            />
          </div>
          <span>*Note: 3-4 images per products is recommended</span>
        </div>
      </Panel>
    </Collapse >
  </React.Fragment>
  );
}

export default ProductPanel;