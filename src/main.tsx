import {useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import Auth from './Auth';
import {logout,me,profile,token} from './api';
import {GameProvider} from './context/GameContext';
import HeroHud from './components/HeroHud';
import InventoryPanel from './components/InventoryPanel';
import CompanionsPanel from './components/CompanionsPanel';
import DmChat from './components/DmChat';
import './styles.css';
type User={id:number;username:string;email:string;xp:number;streak:number;created_at:string;avatar_url?:string|null};
function playClick(){try{const C=window.AudioContext||(window as any).webkitAudioContext;const c=new C();const o=c.createOscillator();const g=c.createGain();o.type='sine';o.frequency.setValueAtTime(520,c.currentTime);o.frequency.exponentialRampToValueAtTime(330,c.currentTime+.045);g.gain.setValueAtTime(.035,c.currentTime);g.gain.exponentialRampToValueAtTime(.001,c.currentTime+.06);o.connect(g);g.connect(c.destination);o.start();o.stop(c.currentTime+.06)}catch{}}
function App(){const[user,setUser]=useState<User|null>(null);const[avatar,setAvatar]=useState<string|null>(null);const[loading,setLoading]=useState(true);useEffect(()=>{const handler=(e:MouseEvent)=>{const target=e.target as HTMLElement|null;const button=target?.closest('button');if(button&&!button.disabled)playClick()};document.addEventListener('click',handler);return()=>document.removeEventListener('click',handler)},[]);useEffect(()=>{if(!token()){setLoading(false);return}me().then(u=>{setUser(u);setAvatar(u.avatar_url??null);return profile()}).then(p=>setAvatar(p.user.avatar_url??null)).catch(()=>logout()).finally(()=>setLoading(false))},[]);if(loading)return <div className="loading">Загрузка хроник…</div>;if(!user)return <Auth onAuth={setUser}/>;return <GameProvider><div className="app"><HeroHud username={user.username} avatar={avatar} onAvatar={setAvatar}/><div className="layout"><InventoryPanel/><main className="center"><DmChat/></main><CompanionsPanel/></div></div></GameProvider>}
createRoot(document.getElementById('root')!).render(<App/>);
