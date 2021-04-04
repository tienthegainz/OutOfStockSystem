import React, { useState, useEffect } from "react";
import { Modal, Button } from 'antd';

const EditModal = (props) => {

  const [confirmLoading, setConfirmLoading] = React.useState(false);

  const handleOk = async () => {
    setConfirmLoading(true);
    await props.ok();
  };

  const handleCancel = () => {
    props.cancel();
  };

  return (<React.Fragment>
    <Modal
      title="Edit confirm"
      visible={props.visible}
      onOk={handleOk}
      confirmLoading={confirmLoading}
      onCancel={handleCancel}
    >
      Are you sure to edit item:&nbsp;{props.name}
    </Modal>
  </React.Fragment>
  );
}

export default EditModal;