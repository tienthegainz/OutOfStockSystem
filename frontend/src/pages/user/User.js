import React, { useState, useEffect } from "react";
import './User.style.css';
import { Button } from 'antd';
import UserAdd from "../../components/UserAdd/UserAdd";
import UserTable from "../../components/UserTable/UserTable";

const UserPage = () => {

  const [add, setAdd] = useState(false);


  return (
    <div className="content">
      <h1>User management</h1>
      <UserTable />
      {add ? <UserAdd
        collapse={() => setAdd(false)}
      /> : null}
      <Button type="text" onClick={() => setAdd(!add)}>
        <span className="func-line">{add ? "Cancel" : "Add user"}</span>
      </Button>
    </div>
  );
}

export default UserPage;