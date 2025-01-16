import React, { useState, useRef } from "react";
import { BrowserRouter as Router, Route, Routes, Link} from "react-router-dom";
import axios from "axios";
import ScheduledPosts from "./ScheduledPosts"; 
import "./App.css";

function App() {
  const [postType, setPostType] = useState("image");
  const [caption, setCaption] = useState("");
  const [hashtags, setHashtags] = useState("");
  const [media, setMedia] = useState(null);
  const [message, setMessage] = useState("");
  const [scheduledTime, setScheduledTime] = useState(""); 
  const [fileError, setFileError] = useState(""); // Added state for file error message
  const mediaInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    const allowedImageTypes = ["image/jpeg", "image/png", "image/webp"];
    const allowedVideoTypes = ["video/mp4"];
    const fileType = file?.type;

    // Check file type based on selected post type
    if (postType === "image" && !allowedImageTypes.includes(fileType)) {
      setFileError("Only JPG, JPEG, PNG, or WEBP files are allowed for images.");
      setMedia(null); // Clear the media if invalid file
    } else if (postType === "video" && !allowedVideoTypes.includes(fileType)) {
      setFileError("Only MP4 files are allowed for videos.");
      setMedia(null); // Clear the media if invalid file
    } else {
      setFileError(""); // Clear the error message if file is valid
      setMedia(file); // Set the selected file
    }
  };

  const resetForm = () => {
    setTimeout(() => {
      setPostType("image");
      setCaption("");
      setHashtags("");
      setMedia(null);
      setMessage("");
      if (mediaInputRef.current) {
        mediaInputRef.current.value = "";
      };
      setScheduledTime("");
    }, 3000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!media) {
      setMessage("Please select a media file.");
      return;
    }

    const formData = new FormData();
    formData.append("post_type", postType);
    formData.append("caption", caption);
    formData.append("hashtags", hashtags);
    formData.append("media", media);
    formData.append("scheduled_time", scheduledTime);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setMessage(response.data.message);
      resetForm();
    } catch (error) {
      setMessage(error.response?.data?.message || "An error occurred");
    }
  };

  return (
    <Router>
      <div className="App">
        <h1>Instagram Post - FARM2</h1>
        <Routes>
          <Route path="/" element={
            <div>
            <form onSubmit={handleSubmit}>
              <div>
                <label htmlFor="postType">Post Type:</label>
                <select
                  id="postType"
                  value={postType}
                  onChange={(e) => setPostType(e.target.value)}
                >
                  <option value="image">Image</option>
                  <option value="video">Video</option>
                </select>
              </div>
              <div>
                <label htmlFor="caption">Caption:</label>
                <textarea
                  id="caption"
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="hashtags">Hashtags:</label>
                <input
                  type="text"
                  id="hashtags"
                  value={hashtags}
                  onChange={(e) => setHashtags(e.target.value)}
                  placeholder="#example #hashtag"
                />
              </div>
              <div>
                <label htmlFor="scheduledTime">Scheduled Time (optional):</label>
                <input
                  type="datetime-local"
                  id="scheduledTime"
                  value={scheduledTime}
                  onChange={(e) => setScheduledTime(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="media">Media File:</label>
                <input
                  type="file"
                  id="media"
                  ref={mediaInputRef}
                  onChange={handleFileChange}
                />
                {fileError && <p style={{ color: "red" }}>{fileError}</p>} {/* Display error message */}
              </div>
              <button type="submit" disabled={!!fileError}>Upload Post</button>
            </form>

            {message && <p>{message}</p>}
            
            <Link to="scheduled_posts" className="button"> View Scheduled Posts</Link>
            
            </div>
          } 
          />
          <Route path="/scheduled_posts" element={<ScheduledPosts />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;