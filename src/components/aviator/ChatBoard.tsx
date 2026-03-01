import { useRef, useState } from "react"

const ChatBoardItem = ({ msg }: { msg?: string }) => {
    return (
        < div className='flex gap-2 w-full' >
            <div className='w-6 h-6'>
                <img alt="avatar" width={24} height={24} src="/aviator/avatar.png" />
            </div>
            <div className='w-full'>
                k***2 {msg || "GRUPO FREE COM 98% DE ACERTO ⬜⬜⬛⬜⬜⬛⬜⬜⬛ ⬛⬛⬛⬛⬛⬛⬛⬛⬛ ⬛⬛⬛⬛⬛⬛⬛⬛⬛ ⬜⬛⬜⬜⬛⬜⬜⬛⬜ ⬛⬜⬜⬛⬜⬜⬜⬜⬛ ⬛⬛⬛⬛⬛⬛⬛⬛⬛ ⬛⬛⬛⬛⬛⬛⬛⬛⬛ ⬜⬜⬛⬜⬜⬜⬛⬜⬜ ⬛⬜⬜⬛⬜⬜⬜⬜⬛ ✅✅✅✅✅✅PESǪUISA NO TELEGRAM👉@VIPJLAVIATOR"}
            </div>
        </div >
    )
}
const ChatBoard = ({ className }: { className?: string }) => {
    const [msg, setMsg] = useState<string>("")
    const [chatData, setChatData] = useState<string[]>([])
    const ref = useRef<HTMLDivElement>(null)
    return (
        <div className={`flex-col w-[400px] bg-black text-[13px] ${className}`}>
            <div ref={ref} className='flex flex-col gap-1 overflow-auto text-white py-2' style={{ height: "calc(100% - 40px)" }}>
                <ChatBoardItem />
                <ChatBoardItem />
                <ChatBoardItem />
                <ChatBoardItem />
                <ChatBoardItem />
                <ChatBoardItem />
                {chatData.map((item, i) => <ChatBoardItem key={i} msg={item} />)}
            </div>
            <div className="w-full h-10 border-t border-white/20 px-4 py-1">
                <input value={msg} onChange={(e) => setMsg(e.target.value)} onKeyDown={(e) => {
                    if (e.key === "Enter") {
                        setChatData(prev => ([...prev, msg]))
                        setMsg("")
                        setTimeout(() => ref.current?.scrollTo(0, ref.current?.scrollHeight), 500);
                    }
                }} type="text" className="outline-none border-none bg-transparent text-white" placeholder="Reply" />
            </div>
        </div>
    )
}
export default ChatBoard