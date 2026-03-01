import * as React from 'react';
import Modal from '@mui/material/Modal';
import SwitchButton from './SwitchButton';
import CloseIcon from '@mui/icons-material/Close';
import { useAviator } from '../store/aviator';
import { aviatorStateType } from '../@types';
const setStopArray = (index: number, value: number, autoPlayingIndex: number) => (prev: aviatorStateType) => {
    const new_state = { ...prev }
    new_state.autoPlayParams[autoPlayingIndex].stopIfarr[index] = value
    return new_state
}
const AutoCashItem = ({ msg, index, autoPlayingIndex }: { msg: string, index: number, autoPlayingIndex: number }) => {
    const { aviatorState, setAviatorState } = useAviator()
    const [stopIfArr, setStopIfArr] = React.useState([10, 10, 10])
    React.useEffect(() => {
        setStopIfArr(aviatorState.autoPlayParams[autoPlayingIndex].stopIfarr)
    }, [aviatorState.autoPlayParams[autoPlayingIndex].stopIfarr])
    return (
        <div className='flex justify-between gap-2 items-center w-full'>
            <div className='flex gap-2 items-center'>
                <SwitchButton disabled={false} checked={stopIfArr[index] > 0} onChange={(event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => {
                    setAviatorState(setStopArray(index, checked ? 10 : 0, autoPlayingIndex))

                }} />
                <span>{msg}</span>
            </div>
            <div className={`flex gap-1 ${stopIfArr[index] > 0 ? "text-white" : "text-[#737373]"}`}>
                <div className={`flex justify-between items-center text-[20px] w-full h-[27px] bg-black rounded-full px-1 border ${stopIfArr[index] > 0 ? "border-white" : "border-[#3E3E3E]"}`} style={{ fontFamily: 'Roboto' }}>
                    <button onClick={() =>
                        setAviatorState(prev => {
                            const new_state = { ...prev }
                            new_state.autoPlayParams[autoPlayingIndex].stopIfarr[index] = Math.max(10, prev.autoPlayParams[autoPlayingIndex].stopIfarr[index] - 10)
                            return new_state
                        })
                    } className={`flex justify-center items-center w-[20px] h-[20px] ${stopIfArr[index] > 0 ? "border-white text-white" : "border-[#3E3E3E] text-[#3E3E3E]"} rounded-full border-2`}>-</button>
                    <input
                        disabled={stopIfArr[index] === 0}
                        value={stopIfArr[index] > 0 ? stopIfArr[index] : "0"}
                        onChange={(e) => {
                            const val = e.target.value.trim() || "0"
                            setAviatorState(setStopArray(index, parseFloat(val), autoPlayingIndex))
                        }}
                        className={`w-[70px] outline-none bg-black text-center text-[15px] ${stopIfArr[index] > 0 ? "text-white" : "text-[#737373]"}`} />
                    <button onClick={() =>
                        setAviatorState(prev => {
                            const new_state = { ...prev }
                            new_state.autoPlayParams[autoPlayingIndex].stopIfarr[index] = Math.min(5000, prev.autoPlayParams[autoPlayingIndex].stopIfarr[index] + 10)
                            return new_state
                        })
                    } className={`flex justify-center items-center w-[20px] h-[20px] rounded-full border-2 ${stopIfArr[index] > 0 ? "border-white text-white" : "border-[#3E3E3E] text-[#3E3E3E]"}`}>+</button>
                </div>
                <span> </span>
            </div>
        </div>
    )
}
export default function AutoBetModal({ modalOpen, modalSetOpen, autoPlayingIndex }: { modalOpen: boolean, modalSetOpen: React.Dispatch<React.SetStateAction<boolean>>, autoPlayingIndex: number }) {

    const handleClose = () => modalSetOpen(false);
    const { aviatorState, setAviatorState } = useAviator()
    const [nOfRounds, setNOfRounds] = React.useState(-1)

    return (
        <div>
            <Modal
                open={modalOpen}
                onClose={handleClose}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
            >
                <div className='mx-auto max-w-[600px] text-white mt-10 p-2'>
                    <div className='border border-[#7C4F00] rounded-[8px] overflow-hidden bg-black/90'>
                        <div className='h-8 bg-[#E59407] text-black text-[16px] font-bold items-center px-4 flex justify-between'>
                            <span>Autoplay Options</span>
                            <button onClick={handleClose} className='cursor-pointer'><CloseIcon /></button>
                        </div>
                        <div className='flex flex-col gap-8 w-full p-6'>
                            <div className='flex flex-col justify-center items-center rounded-[4px] gap-4 p-4 border border-[#2A2B2E]'>
                                <span>Number of Rounds</span>
                                <div className='flex justify-center gap-5 items-center flex-wrap'>
                                    {[10, 50, 100, 500, 1000, 5000].map((item, i) =>
                                        <button key={i} onClick={() => setNOfRounds(item)} className={`rounded-full w-12 px-1 ${item === nOfRounds ? "bg-[#444] border border-white" : "bg-[#222]"}`}>
                                            {item}
                                        </button>
                                    )}
                                </div>
                            </div>
                            <AutoCashItem msg="Stop if cash decreases by" index={0} autoPlayingIndex={autoPlayingIndex} />
                            <AutoCashItem msg="Stop if cash increases by" index={1} autoPlayingIndex={autoPlayingIndex} />
                            {/* <AutoCashItem msg="Stop if single win exceeds" index={2} autoPlayingIndex={autoPlayingIndex} /> */}
                        </div>
                        <div className='flex justify-center items-center gap-8 pb-8'>
                            <button
                                onClick={() => {
                                    setAviatorState(prev => {
                                        const new_auto = prev.RemainedAutoPlayCount
                                        new_auto[autoPlayingIndex] = nOfRounds
                                        return {
                                            ...prev,
                                            RemainedAutoPlayCount: new_auto
                                        }
                                    })
                                    handleClose()
                                }}
                                disabled={nOfRounds < 0 || aviatorState.autoPlayParams[autoPlayingIndex].stopIfarr.every((value) => (value === 0))}
                                className={`w-[70px] h-[26px] rounded-full flex justify-center items-center text-[14px] bg-gradient-to-b from-[#E59407] to-[#412900] uppercase font-bold disabled:opacity-50`}>
                                <span className='drop-shadow-md shadow-black'>Start</span>
                            </button>
                            <button
                                onClick={() => {
                                    setNOfRounds(-1)
                                    setAviatorState(prev => {
                                        const new_val = prev.autoPlayParams
                                        new_val[autoPlayingIndex].stopIfarr = [0, 0, 0]
                                        return {
                                            ...prev, autoPlayParams: new_val
                                        }
                                    })
                                }}
                                className='w-[70px] h-[26px] rounded-full flex justify-center items-center text-[14px] bg-gradient-to-b from-[#E50707] to-[#412900] uppercase font-bold '>
                                <span className='drop-shadow-md shadow-black'>Reset</span>
                            </button>
                        </div>
                    </div>
                </div>
            </Modal>
        </div>
    );
}