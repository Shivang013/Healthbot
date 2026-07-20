import { useState } from "react";

export default function Input({sendMessage}){

    const [text,setText]=useState("");

    function handleSend(){

        if(!text.trim()) return;

        sendMessage(text);

        setText("");

    }

    return(

        <div className="p-6">

            <div className="bg-zinc-800 rounded-2xl flex items-center">

                <input

                value={text}

                onChange={(e)=>setText(e.target.value)}

                onKeyDown={(e)=>{

                    if(e.key==="Enter"){

                        handleSend();

                    }

                }}

                className="flex-1 bg-transparent p-4 outline-none text-white"

                placeholder="Ask anything..."

                />

                <button

                onClick={handleSend}

                className="bg-green-600 hover:bg-green-500 px-6 py-3 rounded-xl mr-2 text-white">

                    Send

                </button>

            </div>

        </div>

    );

}