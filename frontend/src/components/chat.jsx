import { useState } from "react";
import api from "../services/api";
import Message from "./message.jsx";
import Input from "./input.jsx";

export default function Chat(){

    const [messages,setMessages]=useState([]);
    const [loading,setLoading]=useState(false);

    async function sendMessage(question){

        if(!question.trim()) return;

        const userMessage={
            role:"user",
            content:question
        };

        const updatedMessages=[...messages,userMessage];

        setMessages(updatedMessages);
        setLoading(true);

        try{

            const res=await api.post("/chat",{
                question,
                history:updatedMessages
            });

            setMessages([
                ...updatedMessages,
                {
                    role:"assistant",
                    content:res.data.answer
                }
            ]);

        }

        catch(err){

            console.log(err);

        }

        finally{

            setLoading(false);

        }

    }

    return(

        <div className="flex flex-col flex-1">

            <div className="flex-1 overflow-y-auto p-8">

                {
                    messages.length===0 ?

                    <div className="h-full flex flex-col justify-center items-center">

                        <h1 className="text-5xl font-bold text-white">

                            Hello 👋

                        </h1>

                        <p className="text-zinc-400 mt-3">

                            How can I help you today?

                        </p>

                    </div>

                    :

                    messages.map((msg,index)=>

                        <Message
                            key={index}
                            role={msg.role}
                            content={msg.content}
                        />

                    )

                }

                {
                    loading &&

                    <p className="text-zinc-400 mt-4">

                        🌿 HealthBot is thinking...

                    </p>

                }

            </div>

            <Input sendMessage={sendMessage}/>

        </div>

    );

}
