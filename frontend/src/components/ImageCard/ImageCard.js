import React, { useState, useEffect } from "react";
import './ImageCard.css';

const ImageCard = (props) => {
  return (
    <div className="card">
      <img src={props.url} alt="a" />
      <span className="time">{props.time}</span>
      {/* <span className="product">Chivas 92</span> */}
    </div>
  );
}

export default ImageCard;