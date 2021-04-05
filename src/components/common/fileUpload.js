import React from "react";

const FileButton = (props) => {
  return (
    <div className={`file ${props.className}`}>
      <label className={`file-label`}>
        <input
          onChange={(e) => props.onSelect(e)}
          className="file-input"
          type="file"
        />
        <span className={`file-cta`}>
          <span className="file-icon">
            <i className="fas fa-upload"></i>
          </span>
          <span className="file-label">Choose a file…</span>
        </span>
      </label>
    </div>
  );
};

export default FileButton;
