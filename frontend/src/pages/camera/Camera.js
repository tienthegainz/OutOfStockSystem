import React, { useState, useEffect } from "react";
import './Camera.css';
import { Collapse } from 'antd';
import CameraPanel from "../../components/CameraPanel/CameraPanel";

const CameraPage = () => {

  const [cameras, setCamera] = useState([
    {
      id: 1,
      name: "Camera 1",
      objects: [
        {
          name: "Gucci Guilt INTENSE",
          quantity: 1,
          price: 1500000,
          img: "https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F1.jpeg?alt=media"
        },
        {
          name: "Water bottle",
          quantity: 1,
          price: 10000,
          img: "https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F2.png?alt=media"
        }
      ],
    },
    {
      id: 2,
      name: "Camera 2",
      objects: [
        {
          name: "Gucci Guilt INTENSE",
          quantity: 1,
          price: 1500000,
          img: "https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F1.jpeg?alt=media"
        },
        {
          name: "Water bottle",
          quantity: 1,
          price: 10000,
          img: "https://firebasestorage.googleapis.com/v0/b/graduation-thesis-46291.appspot.com/o/products%2F2.png?alt=media"
        }
      ],
    }
  ]);

  return (
    <div className="content">
      <h1>Camera management</h1>
      <div class="camera">
        {cameras.map(c => <CameraPanel camera={c} key={c.id} />)}
      </div>
    </div>
  );
}

export default CameraPage;