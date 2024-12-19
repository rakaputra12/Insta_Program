import React, { useEffect, useState } from "react";
import axios from "axios";
import "./ScheduledPosts.css";

function ScheduledPosts() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const fetchScheduledPosts = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/scheduled_posts");
        setPosts(response.data);
      } catch (error) {
        console.error("Error fetching scheduled posts", error);
      }
    };
    
    fetchScheduledPosts();
  }, []);

  const handleDelete = async (postId) => {
    try {
      const response = await axios.delete(`http://127.0.0.1:5000/delete_scheduled_post/${postId}`);
      if (response.data.status === "success") {
        // Remove the deleted post from the state
        setPosts(posts.filter(post => post.id !== postId));
      }
    } catch (error) {
      console.error("Error deleting the post", error);
    }
  };

  return (
    <div className="scheduled-posts-container">
      <h1>Scheduled Posts</h1>
      <table className="scheduled-posts-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Post Type</th>
            <th>Caption</th>
            <th>Hashtags</th>
            <th>Scheduled Time</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {posts.length > 0 ? (
            posts.map((post) => (
              <tr key={post.id}>
                <td>{post.id}</td>
                <td>{post.post_type}</td>
                <td>{post.caption}</td>
                <td>{post.hashtags}</td>
                <td>{post.scheduled_time}</td>
                <td>
                  <button className="delete-button" onClick={() => handleDelete(post.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6">No scheduled posts found.</td>
            </tr>
          )}
        </tbody>
      </table>
      <a href="/" className="button">Back to Main Page</a>
    </div>
  );
}

export default ScheduledPosts;
