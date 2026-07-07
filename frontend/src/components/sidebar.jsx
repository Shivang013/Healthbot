import {
    PanelLeftClose,
    PanelLeftOpen,
    FileText
} from "lucide-react";

const sources = [
    " WHO Physical Activity Guidelines",
    "ICMR Dietary Guidelines for Indians",
    "ACSM Exercise Testing Guidelines",
    "WHO Mental Health Resources"
];

export default function Sidebar({ collapsed, setCollapsed }) {

    return (

        <div className={`bg-zinc-950 text-white transition-all duration-300 ${
            collapsed ? "w-20" : "w-72"
        }`}>

            {/* Header */}
            <div className="flex justify-between items-center p-4">

                {!collapsed &&
                    <h1 className="text-2xl font-bold">
                        🌿 HealthBot
                    </h1>
                }

                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="p-2 hover:bg-zinc-800 rounded-lg"
                >
                    {collapsed ? <PanelLeftOpen /> : <PanelLeftClose />}
                </button>

            </div>

            {!collapsed && (

                <div className="px-4">

                    <p className="text-zinc-400 text-sm mb-3">
                        Knowledge Base
                    </p>

                    {sources.map((src) => (

                        <div
                            key={src}
                            className="flex items-center gap-3 p-3 rounded-lg hover:bg-zinc-900 cursor-pointer"
                        >
                            <FileText size={18} />
                            <span>{src}</span>
                        </div>

                    ))}

                    
                </div>

            )}

        </div>

    );

}