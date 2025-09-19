import React, {useState} from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

export default function App(){
  const [token,setToken] = useState(localStorage.getItem("syntra_token"));
  return token ? <Dashboard token={token} logout={()=>{localStorage.removeItem("syntra_token"); setToken(null)}} /> : <Login onLogin={(t)=>{localStorage.setItem("syntra_token", t); setToken(t)}}/>;
}
