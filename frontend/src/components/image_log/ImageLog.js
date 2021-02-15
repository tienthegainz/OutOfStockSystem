import React, { useState, useEffect } from "react";
import './ImageLog.css';
import ImageCard from '../ImageCard/ImageCard';
import { serverApi } from "../../common/serverApi";
import { Button } from 'antd';
import { LeftOutlined, RightOutlined } from '@ant-design/icons';

const ImageLog = (props) => {
  const limit = 8;
  const [images, setImages] = useState([[]]);
  const [page, setPage] = useState(1);
  const [totalPage, setTotalPage] = useState(1);

  const renderImage = (data) => {
    let arr = [];
    let i, chunk = 4;
    const j = data.length;
    for (i = 0; i < j; i += chunk) {
      let rowImage = data.slice(i, i + chunk);
      arr.push(rowImage);
    }
    return arr;
  }

  useEffect(() => {
    const getData = async (id, date) => {
      const data = {
        "limit": limit,
        "page": page,
        "from": date + " 00:00:00",
        "to": date + " 23:59:99"
      };
      let respond = await serverApi({ url: '/log/image/' + id, data: data, method: 'post' })
      console.log(respond);
      if (respond.status === 200) {
        setImages(renderImage(respond.data.data));
      }
    };
    if (props.query && props.cameraId.id)
      getData(props.cameraId.id, props.date);
  }, [page, props]);

  useEffect(() => {
    const getTotal = async (id, date) => {
      const data = {
        "from": date + " 00:00:00",
        "to": date + " 23:59:99"
      };
      let respond = await serverApi({ url: '/log/image/count/' + id, data: data, method: 'post' })
      console.log(respond);
      if (respond.status === 200) {
        let total = Math.round(respond.data.total / limit)
        setTotalPage(total);
      }
    };
    if (props.query && props.cameraId.id)
      getTotal(props.cameraId.id, props.date);
  }, [props])

  return (
    <React.Fragment>
      <h1>Image Log</h1>
      {images.map((row, idx) => {
        return (<div className="row" key={idx}>
          {row.map((img, sidx) => <ImageCard url={img.url} time={img.time} key={sidx} />)}
        </div>)
      })}
      <div className="paging-btn">
        <Button
          type="primary"
          shape="circle"
          icon={<LeftOutlined />}
          disabled={page === 1}
          onClick={() => {
            let curPage = page;
            setPage((curPage === 1) ? 1 : (curPage -= 1))
          }
          }
        />
        <Button
          type="primary"
          shape="circle"
          icon={<RightOutlined />}
          disabled={page === totalPage}
          onClick={() => {
            let curPage = page;
            setPage((curPage === totalPage) ? totalPage : (curPage += 1))
          }
          }
        />
      </div>
      {totalPage ? <div className="paging-note">Page: {page}/{totalPage}</div> : null}
    </React.Fragment>
  );
}

export default ImageLog;