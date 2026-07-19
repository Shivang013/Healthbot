import { useState } from "react";

import Sidebar from "./components/sidebar.jsx";
import Chat from "./components/chat.jsx";

export default function App(){

    const [collapsed,setCollapsed]=useState(false);

    return(

        <div className="flex h-screen bg-zinc-900">

            <Sidebar
                collapsed={collapsed}
                setCollapsed={setCollapsed}
            />

            <Chat/>

        </div>

    )

}
