import React, { useState, useEffect } from "react";
import { Table, Space, InputNumber } from 'antd';
import { DeleteOutlined, EditOutlined, StopOutlined, CheckOutlined } from '@ant-design/icons';
import './CameraTable.css';
import { serverApiWithToken } from "../../common/serverApi";
import DeleteModal from "../DeleteModal/DeleteModal";
import EditModal from "../EditModal/EditModal";

const CameraTable = (props) => {

  const data = props.data.map(x => {
    return { ...x, key: x.id }
  });

  const [editRow, setEditRow] = useState({ id: null });
  // 0: normal, 1: edit confirm, 2: delete confirm
  const [actionInfo, setActionInfo] = useState({ display: 0 });

  const columns = [
    {
      title: 'Product ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (text, record) => (
        (editRow.id === record.id) ? <InputNumber
          min={1}
          max={5}
          defaultValue={record.quantity}
          onChange={(value) => {
            setEditRow({ ...editRow, quantity: value });
          }}
        /> : record.quantity
      )
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
    },
    {
      title: 'Action',
      key: 'action',
      render: (text, record) => (
        <Space size="middle">
          {(editRow.id === record.id) ? <React.Fragment>
            <CheckOutlined
              style={{ color: 'green' }}
              onClick={() => {
                setActionInfo({
                  display: 1,
                  quantity: editRow.quantity,
                  productId: record.id,
                  name: record.name
                })
              }}
            />
            <StopOutlined
              style={{ color: 'red' }}
              onClick={() => setEditRow({ id: null })}
            />
          </React.Fragment> : <React.Fragment>
              < EditOutlined
                style={{ color: 'blue' }}
                onClick={() => setEditRow({ id: record.id, quantity: record.quantity })}
              />
              < DeleteOutlined
                style={{ color: 'red' }}
                onClick={() => {
                  setActionInfo({
                    display: 2,
                    productId: record.id,
                    name: record.name
                  })
                }}
              />
            </React.Fragment>}
        </Space >
      ),
    },
  ];

  return (<React.Fragment>
    <EditModal
      cancel={() => setActionInfo({ display: 0 })}
      name={actionInfo.name}
      ok={async () => {
        let respond = await serverApiWithToken({
          url: '/camera/' + props.cameraId + '/product/' + actionInfo.productId,
          data: { quantity: actionInfo.quantity },
          method: 'put'
        })
        console.log(respond);
        if (respond.status === 200 && respond.data.success === true) {
          props.getData();
        }
        setActionInfo({ display: 0 });
        setEditRow({ id: null });
      }}
      visible={actionInfo.display === 1}
    />
    <DeleteModal
      cancel={() => setActionInfo({ display: 0 })}
      visible={actionInfo.display === 2}
      name={actionInfo.name}
      ok={async () => {
        let respond = await serverApiWithToken({
          url: '/camera/' + props.cameraId + '/product/' + actionInfo.productId,
          method: 'delete'
        })
        console.log(respond);
        if (respond.status === 200 && respond.data.success === true) {
          props.getData();
        }
        setActionInfo({ display: 0 });
        setEditRow({ id: null });
      }}
    />
    <Table columns={columns} dataSource={data} />
  </React.Fragment>
  );
}

export default CameraTable;