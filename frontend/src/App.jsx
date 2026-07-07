import { useState } from "react";

import Sidebar from "./components/Sidebar";
import Chat from "./components/Chat";

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