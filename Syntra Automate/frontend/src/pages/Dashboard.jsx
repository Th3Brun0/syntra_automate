import React, {useEffect, useState} from "react";
import axios from "axios";

export default function Dashboard({token, logout}){
  const [mikrotiks, setM] = useState([]);
  useEffect(()=> {
    axios.get((import.meta.env.VITE_API_URL||"/api")+"/mikrotiks", {headers:{Authorization:`Bearer ${token}`}})
      .then(r=>setM(r.data)).catch(()=>{});
  },[]);
  return (<div className="layout">
    <header><h1>Syntra</h1><button onClick={logout}>Logout</button></header>
    <main>
      <section><h2>Devices</h2>
        <ul>{mikrotiks.map(m=> <li key={m.id}>{m.name} - {m.ip}</li>)}</ul>
      </section>
    </main>
  </div>);
}
