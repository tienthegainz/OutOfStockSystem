import React, { useState, useEffect } from "react";
import './ImageLog.css';
import ImageCard from '../ImageCard/ImageCard';
import { serverApi } from "../../common/serverApi";
import { Button } from 'antd';
import { LeftOutlined, RightOutlined } from '@ant-design/icons';

const ImageLog = () => {
  const limit = 8;
  const [images, setImages] = useState([[]]);
  const [page, setPage] = useState(1);
  const [totalPage, setTotalPage] = useState();

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
    const getData = async () => {
      const data = {
        "limit": limit,
        "page": page
      };
      let respond = await serverApi({ url: '/log/image/1', data: data, method: 'post' })
      console.log(respond);
      if (respond.status === 200) {
        setImages(renderImage(respond.data.data));
      }
    };
    getData();
  }, [page]);

  useEffect(() => {
    const getTotal = async () => {
      let respond = await serverApi({ url: '/log/image/count/1' })
      console.log(respond);
      if (respond.status === 200) {
        let total = Math.round(respond.data.total / limit)
        setTotalPage(total);
      }
    };
    getTotal();
  }, [])

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