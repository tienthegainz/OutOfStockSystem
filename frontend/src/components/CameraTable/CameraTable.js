import React, { useState, useEffect } from "react";
import { Table, Space, InputNumber } from 'antd';
import { DeleteOutlined, EditOutlined, StopOutlined, CheckOutlined } from '@ant-design/icons';
import './CameraTable.css';
import { serverApi } from "../../common/serverApi";
import DeleteModal from "../DeleteModal/DeleteModal";
import EditModal from "../EditModal/EditModal";

const CameraTable = (props) => {

  const data = props.data.map(x => {
    return { ...x, key: x.id }
  });

  const [editRows, setEditRows] = useState([]);
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
        editRows.map(row => row.id).includes(record.id) ? <InputNumber
          min={1}
          max={5}
          defaultValue={record.quantity}
          onChange={(value) => {
            let newValue = { id: record.id, quantity: value }
            let newEditRows = editRows.filter(row => row.id !== record.id);
            setEditRows([...newEditRows, newValue]);
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
          {editRows.map(row => row.id).includes(record.id) ? <React.Fragment>
            <CheckOutlined
              style={{ color: 'green' }}
              onClick={() => {
                setActionInfo({
                  display: 1,
                  quantity: editRows.find(row => row.id === record.id).quantity,
                  productId: record.id,
                  name: record.name
                })
              }}
            />
            <StopOutlined
              style={{ color: 'red' }}
              onClick={() => setEditRows(editRows.filter(r => r.id !== record.id))}
            />
          </React.Fragment> : <React.Fragment>
              < EditOutlined
                style={{ color: 'blue' }}
                onClick={() => setEditRows([...editRows, { id: record.id, quantity: record.quantity }])}
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
        let respond = await serverApi({
          url: '/camera/' + props.cameraId + '/product/' + actionInfo.productId,
          data: { quantity: actionInfo.quantity },
          method: 'put'
        })
        console.log(respond);
        if (respond.status === 200) {
          props.getData();
        }
        setActionInfo({ display: 0 });
      }}
      visible={actionInfo.display === 1}
    />
    <DeleteModal
      cancel={() => setActionInfo({ display: 0 })}
      visible={actionInfo.display === 2}
      name={actionInfo.name}
      ok={async () => {
        let respond = await serverApi({
          url: '/camera/' + props.cameraId + '/product/' + actionInfo.productId,
          method: 'delete'
        })
        console.log(respond);
        if (respond.status === 200) {
          props.getData();
        }
        setActionInfo({ display: 0 });
      }}
    />
    <Table columns={columns} dataSource={data} />
  </React.Fragment>
  );
}

export default CameraTable;