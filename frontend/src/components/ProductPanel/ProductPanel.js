import React, { useState, useEffect } from "react";
import './ProductPanel.css';
import { Collapse, Button } from 'antd';
import { DeleteOutlined, LeftOutlined, RightOutlined, EditOutlined } from '@ant-design/icons';
import { serverApiWithToken } from "../../common/serverApi";
import DeleteModal from "../DeleteModal/DeleteModal";
import { useDispatch } from "react-redux";
import allActions from "../../actions";

const { Panel } = Collapse;

const ProductPanel = (props) => {

  const [edit, setEdit] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const dispatch = useDispatch();

  return (<React.Fragment>
    {deleteConfirm ? <DeleteModal
      visible={deleteConfirm}
      ok={async () => {
        let respond = await serverApiWithToken({ url: '/product/' + props.data.id, method: 'delete' });
        console.log(respond);
        if (respond.errorCode === 401) {
          dispatch(allActions.userActions.logout());
        }
        setDeleteConfirm(false);
        props.delete();
      }}
      cancel={() => setDeleteConfirm(false)}
      name={props.data.name}
    /> : null}
    <Collapse>
      <Panel
        header={props.data.name}
        key={props.data.id}
        extra={edit ? <DeleteOutlined
          onClick={async (event) => {
            event.stopPropagation();
            setDeleteConfirm(true);
          }}
          style={{ color: "red" }}
        /> : <EditOutlined
            onClick={(event) => {
              event.stopPropagation();
              console.log('Delete');
              setEdit(true);
            }}
          />}
        style={{ marginBottom: '10px' }}
      >
        <div className="product-spec">
          <h3>Name:</h3>
          <p>{props.data.name}</p>
          <h3>Price:</h3>
          <p>{props.data.price} VND</p>
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
          {edit ? <Button
            type="primary"
            style={{
              textAlign: "center",
              fontSize: "20px",
              width: "fit-content",
              height: "fit-content",
              margin: "auto"
            }}
            onClick={() => setEdit(false)}
          >Confirm</Button> : null}
        </div>
      </Panel>
    </Collapse >
  </React.Fragment>
  );
}

export default ProductPanel;