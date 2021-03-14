import React, { useState, useEffect } from "react";
import { Table, Space, Input, Menu, Button, Dropdown } from 'antd';
import { DeleteOutlined, EditOutlined, StopOutlined, CheckOutlined } from '@ant-design/icons';
import { DownOutlined } from '@ant-design/icons';
import './EmployeeTable.style.css';
import { serverApiWithToken } from "../../common/serverApi";
import DeleteModal from "../DeleteModal/DeleteModal";
import EditModal from "../EditModal/EditModal";


const UserTable = (props) => {

  const userData = props.data;
  const [editRow, setEditRow] = useState({ id: null });
  // 0: normal, 1: edit confirm, 2: delete confirm
  const [actionInfo, setActionInfo] = useState({ display: 0 });


  const menu = (
    <Menu>
      <Menu.Item
        key="1"
        onClick={() => setEditRow({ ...editRow, admin: true })}
      >
        Admin
      </Menu.Item>
      <Menu.Item
        key="2"
        onClick={() => setEditRow({ ...editRow, admin: false })}
      >
        Employee
      </Menu.Item>
    </Menu>
  );

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
          onChange={(e) => {
            // console.log(e.target.value)
            setEditRow({ ...editRow, password: e.target.value });
          }}
        /> : <span>*******</span>
      )
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: (text, record) => (
        (editRow.id === record.id) ?
          <Dropdown overlay={menu}>
            <Button>
              {editRow.admin ? 'Admin' : 'Employee'} <DownOutlined />
            </Button>
          </Dropdown> :
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
                  password: editRow.password,
                  admin: editRow.admin
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
              onClick={() => setEditRow(record)}
            />
            < DeleteOutlined
              style={{ color: 'red' }}
              onClick={() => {
                setActionInfo({
                  display: 2,
                  userId: record.id,
                  username: record.username
                })
              }}
            />
          </React.Fragment>}
        </Space >
      ),
    },
  ];


  return (<React.Fragment>
    {actionInfo.display === 1 ? <EditModal
      cancel={() => setActionInfo({ display: 0 })}
      name={actionInfo.username}
      ok={async () => {
        let respond = await serverApiWithToken({
          url: '/user/' + actionInfo.userId,
          data: {
            password: actionInfo.password,
            admin: actionInfo.admin
          },
          method: 'put'
        })
        console.log(respond);
        if (respond.status === 200 && respond.data.success === true) {
          props.getData();
        }
        setActionInfo({ display: 0 });
        setEditRow({ id: null });
      }}
      visible={true}
    /> : null}
    {actionInfo.display === 2 ? <DeleteModal
      cancel={() => setActionInfo({ display: 0 })}
      visible={true}
      name={actionInfo.username}
      ok={async () => {
        let respond = await serverApiWithToken({
          url: '/user/' + actionInfo.userId,
          method: 'delete'
        })
        console.log(respond);
        if (respond.status === 200 && respond.data.success === true) {
          props.getData();
        }
        setActionInfo({ display: 0 });
        setEditRow({ id: null });
      }}
    /> : null}
    <Table columns={columns} dataSource={userData} />
  </React.Fragment>
  );
}

export default UserTable;