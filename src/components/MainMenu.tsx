import {BookOpen,Backpack,House,Settings,Shield,UserRound} from 'lucide-react';
import {useEffect} from 'react';
export type Page='home'|'inventory'|'character'|'campaign'|'settings';
type Props={page:Page;onNavigate:(page:Page)=>void};
const items:[Page,string,typeof House][]=[['home','Главная',House],['inventory','Инвентарь',Backpack],['character','Персонаж',UserRound],['campaign','Кампания',BookOpen],['settings','Настройки',Settings]];
export default function MainMenu({page,onNavigate}:Props){useEffect(()=>{const go=(e:Event)=>{const target=(e as CustomEvent<Page>).detail;if(items.some(([key])=>key===target))onNavigate(target)};window.addEventListener('dnd-navigate',go);return()=>window.removeEventListener('dnd-navigate',go)},[onNavigate]);return <aside className="main-menu"><div className="menu-title"><Shield size={18}/> ХРОНИКИ</div><nav>{items.map(([key,label,Icon])=><button key={key} className={page===key?'active':''} onClick={()=>onNavigate(key)}><Icon size={18}/><span>{label}</span></button>)}</nav></aside>}
