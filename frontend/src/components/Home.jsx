import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import PdfView from "./PdfView";

const Home = () => {
  const accessToken = localStorage.getItem("accessToken");
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const headers = {
    Accept: "application/json",
    Authorization: "Bearer " + accessToken,
  };
  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
    }
    axios
      .get("/api/v1/user", { headers })
      .then((response) => {
        setUser(response.data);
      })
      .catch((error) => {
        console.error(error);
      });

    axios
      .get("/api/v1/posts", { headers })
      .then((response) => {
        setPosts(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  }, [accessToken]);
  const logout = () => {
    localStorage.removeItem("accessToken");
    setUser(null);
  };
  const [file, setFile] = useState(null);
  const [loaded, setLoaded] = useState(0);
  const [description, setDescription] = useState("");
  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData();
    data.append("file", file);
    data.append("description", description);
    data.append("user_id", user.id);
    axios
      .post("/api/v1/posts", data, {
        headers: { ...headers, "Content-Type": "multipart/form-data" },
        onUploadProgress: (ProgressEvent) => {
          const progress = (ProgressEvent.loaded / ProgressEvent.total) * 100;
          setLoaded(Math.ceil(progress));
        },
      })
      .then((response) => {
        //setPosts([...posts, response.data]);
        //setFile(null);
        //setDescription("");
      })
      .catch((error) => {
        console.error(error);
      });
  };

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setLoaded(0);
  };

  const handleDescriptionChange = (event) => {
    setDescription(event.target.value);
  };
  return (
    <div className="container mx-auto px-4">
      <div className="flex mb-5">
        {user && <h3 className="inline mr-12">Welcome, {user.name}</h3>}
        <button
          type="button"
          className="rounded-lg cursor-pointer"
          onClick={logout}
        >
          Log out
        </button>
      </div>
      <h1 className="text-3xl font-bold mb-4">Newsfeed</h1>
      <form onSubmit={handleSubmit} className="mb-4">
        <div className="mb-4">
          <label htmlFor="file" className="block text-gray-700 font-bold mb-2">
            File:
          </label>
          <input
            type="file"
            id="file"
            onChange={handleFileChange}
            className="border shadow-md rounded w-1/2 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>
        <div class="mb-4">
          <div class="bg-white relative h-4 w-1/2 rounded-2xl">
            <div
              class="bg-emerald-600 absolute top-0 left-0 flex h-full items-center justify-center rounded-2xl text-xs font-semibold text-white"
              style={{ width: `${loaded}%` }}
            >
              {loaded}%
            </div>
          </div>
        </div>
        <div className="mb-4">
          <label
            htmlFor="description"
            className="block text-gray-700 font-bold mb-2"
          >
            Description:
          </label>
          <textarea
            id="description"
            value={description}
            onChange={handleDescriptionChange}
            className="border shadow-md w-1/2 h-32 rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          />
        </div>
        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          Submit
        </button>
      </form>
      <div>
        {posts.map((post, index) => (
          <div key={index} className="bg-white rounded-lg shadow-lg mb-4 p-4">
            <div className="flex items-center mb-2">
              <div className="flex-shrink-0">
                <img
                  src={`https://i.pravatar.cc/50?u=1`}
                  alt="Avatar"
                  className="rounded-full w-10 h-10"
                />
              </div>
              <div className="ml-4">
                <p className="text-gray-900 font-bold">{post.filename}</p>
                <p className="text-gray-700">{post.description}</p>
              </div>
            </div>
            <PdfView file="./pdf/read.pdf" />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Home;
