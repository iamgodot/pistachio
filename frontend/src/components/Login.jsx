import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import shareVideo from "../assets/share.mp4";
import axios from "axios";

const CLIENT_ID = "35ed38dbee5282f1b162";

const Login = () => {
  const navigate = useNavigate();
  const accessToken = localStorage.getItem("accessToken");
  useEffect(() => {
    if (accessToken) {
      navigate("/");
    }
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const codeParam = urlParams.get("code");
    if (codeParam) {
      axios
        .post("/api/v1/login", { type: "github", github_code: codeParam })
        .then((response) => {
          const data = response.data;
          if (data && data.access_token) {
            localStorage.setItem("accessToken", data.access_token);
            navigate("/");
          }
        });
    }
  }, [accessToken]);
  function loginWithGithub() {
    window.location.assign(
      "https://github.com/login/oauth/authorize?client_id=" + CLIENT_ID,
      "_blank"
    );
  }
  return (
    <div className="flex justify-start items-center flex-col h-screen">
      <div className=" relative w-full h-full">
        <video
          src={shareVideo}
          type="video/mp4"
          loop
          controls={false}
          muted
          autoPlay
          className="w-full h-full object-cover"
        />
        <div className="absolute flex flex-col justify-center items-center top-0 right-0 left-0 bottom-0">
          <div className="m-8 font-mono text-xl text-gray-900 ">
            Welcome to Pistachio!
          </div>
          <button
            type="button"
            onClick={loginWithGithub}
            //className="bg-gray-100 w-1/5 mx-1 px-1 py-1 flex justify-center items-center rounded-lg cursor-pointer outline-none"
            className="bg-gray-700 opacity-75 w-1/5 p-2 rounded-full font-mono text-sm text-gray-100 cursor-pointer"
          >
            Sign in with GitHub
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
