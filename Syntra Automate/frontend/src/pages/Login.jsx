import React, {useState} from "react";
import axios from "axios";

export default function Login({onLogin}){
  const [u,setU] = useState(""); const [p,setP]=useState(""); const [err,setErr]=useState("");
  const submit = async (e)=>{
    e.preventDefault();
    try{
      const form = new URLSearchParams();
      form.append("username", u);
      form.append("password", p);
      form.append("grant_type","password");
      const res = await axios.post((import.meta.env.VITE_API_URL||"/api")+"/auth/token", form);
      onLogin(res.data.access_token);
    }catch(e){
      setErr("Login failed");
    }
  };
  return (<div className="login">
    <h2>Syntra</h2>
    <form onSubmit={submit}>
      <label>Usuário<input value={u} onChange={e=>setU(e.target.value)} /></label>
      <label>Senha<input type="password" value={p} onChange={e=>setP(e.target.value)} /></label>
      <button>Entrar</button>
      {err && <div className="error">{err}</div>}
    </form>
  </div>);
}
