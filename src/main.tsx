import {useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import Auth from './Auth';
import {logout,me,profile,token} from './api';
import {GameProvider,useGame} from './context/GameContext';
import HeroHud from './components/HeroHud';
import InventoryPanel from './components/InventoryPanel';
import CompanionsPanel from './components/CompanionsPanel';
import DmChat from './components/DmChat';
import MainMenu,{Page} from './components/MainMenu';
import './styles.css';
type User={id:number;username:string;email:string;xp:number;streak:number;created_at:string;avatar_url?:string|null};
function playClick(){try{const C=window.AudioContext||(window as any).webkitAudioContext;const c=new C();const o=c.createOscillator();const g=c.createGain();o.type='sine';o.frequency.setValueAtTime(520,c.currentTime);o.frequency.exponentialRampToValueAtTime(330,c.currentTime+.045);g.gain.setValueAtTime(.035,c.currentTime);g.gain.exponentialRampToValueAtTime(.001,c.currentTime+.06);o.connect(g);g.connect(c.destination);o.start();o.stop(c.currentTime+.06)}catch{}}
function PagePlaceholder({page,user}:{page:Exclude<Page,'home'>;user:User}){if(page==='inventory')return <InventoryPanel/>;if(page==='character')return <section className="page-panel"><div className="panel-title"><span>ПЕРСОНАЖ</span></div><div className="character-page"><div className="character-avatar">{user.avatar_url?<img src={user.avatar_url} alt=""/>:'🧙'}</div><h1>{user.username}</h1><p>Герой приключения</p><div className="character-stats"><div><span>XP</span><b>{user.xp}</b></div><div><span>Серия</span><b>{user.streak}</b></div></div></div></section>;if(page==='campaign')return <section className="page-panel"><div className="panel-title"><span>КАМПАНИЯ</span></div><div className="page-copy"><span>ТЁМНЫЙ ПЕРЕВАЛ</span><h1>Хроники Серых Гоблинов</h1><p>Текущая кампания и пройденные приключения будут собраны здесь.</p></div></section>;return <section className="page-panel"><div className="panel-title"><span>НАСТРОЙКИ</span></div><div className="settings-list"><label><span>Звуки интерфейса</span><input type="checkbox" defaultChecked/></label><label><span>Анимации</span><input type="checkbox" defaultChecked/></label></div></section>}
function GamePages({user}:{user:User}){const[page,setPage]=useState<Page>('home');return <><HeroHud username={user.username} avatar={user.avatar_url??null} onAvatar={()=>{}}/><div className="layout"><MainMenu page={page} onNavigate={setPage}/><main className="center">{page==='home'?<DmChat/>:<PagePlaceholder page={page} user={user}/>}</main><CompanionsPanel/></div></>}
function App(){const[user,setUser]=useState<User|null>(null);const[loading,setLoading]=useState(true);useEffect(()=>{const handler=(e:MouseEvent)=>{const target=e.target as HTMLElement|null;const button=target?.closest('button');if(button&&!button.disabled)playClick()};document.addEventListener('click',handler);return()=>document.removeEventListener('click',handler)},[]);useEffect(()=>{if(!token()){setLoading(false);return}me().then(u=>{setUser(u);return profile()}).catch(()=>logout()).finally(()=>setLoading(false))},[]);if(loading)return <div className="loading">Загрузка хроник…</div>;if(!user)return <Auth onAuth={setUser}/>;return <GameProvider><div className="app"><GamePages user={user}/></div></GameProvider>}
createRoot(document.getElementById('root')!).render(<App/>);
