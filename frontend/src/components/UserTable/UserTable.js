import React, { useState, useEffect } from "react";
import { Table, Space, Input } from 'antd';
import { DeleteOutlined, EditOutlined, StopOutlined, CheckOutlined } from '@ant-design/icons';
import './UserTable.style.css';
import { serverApiWithToken } from "../../common/serverApi";
import DeleteModal from "../DeleteModal/DeleteModal";
import EditModal from "../EditModal/EditModal";
import allActions from "../../actions";
import { useDispatch } from "react-redux";

const UserTable = () => {


  const [userData, setUserData] = useState([]);
  const [editRow, setEditRow] = useState({ id: null });
  // 0: normal, 1: edit confirm, 2: delete confirm
  const [actionInfo, setActionInfo] = useState({ display: 0 });
  const dispatch = useDispatch();

  const columns = [
    {
      title: 'User ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'Password',
      dataIndex: 'password',
      key: 'password',
      colSpan: 1,
      render: (text, record) => (
        (editRow.id === record.id) ? <Input.Password
          placeholder="input password"
          onChange={(value) => {
            setEditRow({ ...editRow, password: value })
          }}
        /> : <span>*******</span>
      )
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: (text, record) => (
        record.admin ? <span>Admin</span> : <span>Employee</span>
      )
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
                  userId: editRow.id,
                  username: editRow.username,
                  password: editRow.password
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
                onClick={() => setEditRow({ id: record.id, username: record.username })}
              />
              < DeleteOutlined
                style={{ color: 'red' }}
                onClick={() => {
                  setActionInfo({
                    display: 2,
                    userId: editRow.id,
                    username: editRow.username
                  })
                }}
              />
            </React.Fragment>}
        </Space >
      ),
    },
  ];

  const getData = async () => {
    let respond = await serverApiWithToken({ url: '/user' })
    console.log(respond);
    if (respond.status === 200 && respond.data.success === true) {
      let data = respond.data.users.map(user => {
        return { ...user, key: user.id };
      });
      setUserData(data);
    }
  };

  useEffect(() => {
    getData();
  }, [])


  return (<React.Fragment>
    <EditModal
      cancel={() => setActionInfo({ display: 0 })}
      name={actionInfo.name}
      ok={async () => {
        // let respond = await serverApiWithToken({
        //   url: '/camera/' + props.cameraId + '/product/' + actionInfo.productId,
        //   data: { quantity: actionInfo.quantity },
        //   method: 'put'
        // })
        // console.log(respond);
        // if (respond.status === 200 && respond.data.success === true) {
        //   props.getData();
        // }
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
        // let respond = await serverApiWithToken({
        //   url: '/camera/' + props.cameraId + '/product/' + actionInfo.productId,
        //   method: 'delete'
        // })
        // console.log(respond);
        // if (respond.status === 200 && respond.data.success === true) {
        //   props.getData();
        // }
        setActionInfo({ display: 0 });
        setEditRow({ id: null });
      }}
    />
    <Table className='user-table' columns={columns} dataSource={userData} />
  </React.Fragment>
  );
}

export default UserTable;