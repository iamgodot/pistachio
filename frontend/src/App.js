import "./App.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Login from "./components/Login";
import Home from "./components/Home";
import ErrorPage from "./Error-page";
import Newsfeed from "./components/PdfView";

function App() {
  const router = createBrowserRouter([
    { path: "/", element: <Home />, errorElement: <ErrorPage /> },
    { path: "/login", element: <Login /> },
    { path: "/feed", element: <Newsfeed /> },
  ]);
  return <RouterProvider router={router} />;
}

export default App;
