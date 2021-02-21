import React, { useState, useEffect } from "react";
import './CameraReadyModal.css';

const CameraReadyModal = (props) => {
  return (
    <div className="modal">
      <p className="ready"><i className="fa fa-refresh fa-spin" /> Waiting</p>
    </div>
  );
}

export default CameraReadyModal;