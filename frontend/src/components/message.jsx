export default function Message({role,content}){

    const isUser=role==="user";

    return(

        <div
        className={`flex mb-6 ${
            isUser ? "justify-end" : "justify-start"
        }`}>

            <div
            className={`max-w-3xl px-5 py-4 rounded-2xl whitespace-pre-wrap ${
                isUser
                ? "bg-green-600 text-white"
                : "bg-zinc-800 text-white"
            }`}>

                {content}

            </div>

        </div>

    );

}