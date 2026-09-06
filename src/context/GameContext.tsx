import {createContext,useContext,useEffect,useMemo,useState} from 'react';
import {saveProgress} from '../api';
import {Companion,InventoryItem,Quest,quests,starterCompanions,starterInventory} from '../game';

type GameContextValue={quest:Quest;questIndex:number;hp:number;xp:number;level:number;dice:number|null;chosen:string[];log:string[];hint:boolean;inventory:InventoryItem[];companions:Companion[];solved:boolean;roll:()=>void;act:(action:string)=>void;wrong:()=>void;next:()=>void;toggleHint:()=>void;useItem:(id:string)=>void};
const GameContext=createContext<GameContextValue|null>(null);
export function GameProvider({children}:{children:React.ReactNode}){
 const [questIndex,setQuestIndex]=useState(0),[hp,setHp]=useState(100),[xp,setXp]=useState(0),[dice,setDice]=useState<number|null>(null),[chosen,setChosen]=useState<string[]>([]),[log,setLog]=useState<string[]>([]),[hint,setHint]=useState(false),[solved,setSolved]=useState(false),[inventory,setInventory]=useState(starterInventory),[companions]=useState(starterCompanions);
 const quest=quests[questIndex]; const level=Math.max(1,Math.floor(xp/250)+1);
 const add=(s:string)=>setLog(x=>[s,...x].slice(0,10));
 const roll=()=>{const n=Math.floor(Math.random()*20)+1;setDice(n);add(`🎲 d20 → ${n}${n===20?' — КРИТИЧЕСКИЙ УСПЕХ!':n===1?' — КРИТИЧЕСКИЙ ПРОВАЛ!':''}`);if(n===1)setHp(h=>Math.max(0,h-8));if(n===20)setXp(x=>x+20)};
 const act=(action:string)=>{if(solved||chosen.includes(action))return;const next=[...chosen,action];setChosen(next);add(`⚔ ${action}`);if(next.length===quest.actions.length){setSolved(true);setXp(x=>x+quest.points);setHp(h=>Math.min(100,h+10));add(`✓ Квест завершён: +${quest.points} XP`);saveProgress(quest.id,true,quest.points).catch(()=>{})}};
 const wrong=()=>{if(!solved){setHp(h=>Math.max(0,h-20));add(`☠ ${quest.wrong}`)}};
 const next=()=>{setQuestIndex(i=>(i+1)%quests.length);setSolved(false);setChosen([]);setHp(100);setHint(false);setDice(null);setLog([])};
 const useItem=(id:string)=>setInventory(items=>items.map(x=>x.id===id&&x.count>0?{...x,count:x.count-1}:x));
 const value=useMemo(()=>({quest,questIndex,hp,xp,level,dice,chosen,log,hint,inventory,companions,solved,roll,act,wrong,next,toggleHint:()=>setHint(v=>!v),useItem}),[quest,questIndex,hp,xp,level,dice,chosen,log,hint,inventory,companions,solved]);
 return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}
export function useGame(){const ctx=useContext(GameContext);if(!ctx)throw new Error('useGame must be used inside GameProvider');return ctx;}
