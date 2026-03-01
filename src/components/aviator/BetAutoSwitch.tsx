import { betAutoStateType } from "../../@types"

const BetAutoButton = ({ title, onClick }: { title: string, onClick: () => void }) => {
    return (
        <button onClick={onClick} className='flex justify-center items-center w-[56px] lg:w-[70px] h-[18px] lg:h-[20px] rounded-full text-[12px] lg:text-md z-10'>
            {title}
        </button>
    )
}

const BetAutoSwitch = ({ betAuto: { betAutoState, setBetAutoState } }: { betAuto: { betAutoState: betAutoStateType, setBetAutoState: (val: betAutoStateType) => void } }) => {
    const handleBetClick = () => {
        setBetAutoState("bet")
    }
    const handleAutoClick = () => {
        setBetAutoState("auto")
    }
    return (
        <div className='flex gap-1 rounded-full relative bg-black'>
            <div className={`absolute w-[56px] lg:w-[70px] h-[18px] lg:h-[20px] rounded-full bg-[#2c2d30] transition-all ease-in-out ${betAutoState === "bet" ? "" : "translate-x-[60px] lg:translate-x-[74px]"} `}></div>
            <BetAutoButton onClick={handleBetClick} title='Bet' />
            <BetAutoButton onClick={handleAutoClick} title='Auto' />
        </div>
    )
}
export default BetAutoSwitch