import React, { useState, useEffect } from "react";
import './Employee.style.css';
import { Button } from 'antd';
import RegisterForm from "../../components/RegisterForm/RegisterForm";
import EmployeeTable from "../../components/EmployeeTable/EmployeeTable";
import { serverApiWithToken } from "../../common/serverApi";

const EmployeePage = () => {

  const [add, setAdd] = useState(false);
  const [userData, setUserData] = useState([]);

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
  }, []);


  return (
    <div className="content employee-outline">
      <h1>Employee management</h1>
      <EmployeeTable
        data={userData}
        getData={getData}
      />
      <Button type="text" onClick={() => setAdd(!add)}>
        {add ? null : <span className="func-line">Add employee</span>}
      </Button>
      {add ? <RegisterForm
        cancel={() => setAdd(false)}
        getData={getData}
      /> : null}
    </div>
  );
}

export default EmployeePage;