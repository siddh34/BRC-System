import { useState } from "react";
import React from 'react'
import { uploadFile } from "react-s3";

const S3_BUCKET = "YOUR_BUCKET_NAME";
const REGION = "YOUR_REGION_NAME";
const ACCESS_KEY = "YOUR_ACCESS_KEY";
const SECRET_ACCESS_KEY = "YOUR_SECRET_ACCESS_KEY";

const config = {
    bucketName: S3_BUCKET,
    region: REGION,
    accessKeyId: ACCESS_KEY,
    secretAccessKey: SECRET_ACCESS_KEY,
};

export default function UploadToS3() {
    const [selectedFile, setSelectedFile] = useState(null);

    const handleFileInput = (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleUpload = async (file) => {
        uploadFile(file, config)
        .then((data) => console.log(data))
        .catch((err) => console.error(err));
    };

    return (
        <div>
        <div>React S3 File Upload</div>
        <input type="file" onChange={handleFileInput} />
        <button onClick={() => handleUpload(selectedFile)}> Upload to S3</button>
        </div>
    );
}
