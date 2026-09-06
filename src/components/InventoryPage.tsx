import {useEffect,useMemo,useState,type DragEvent} from 'react';
import {Backpack,ChevronRight,Coins,Flame,Heart,ScrollText,Swords,Weight} from 'lucide-react';
import {buyShopItem,getInventory,getShop,me} from '../api';
import type {InventoryItem,ShopItem} from '../api';
import './inventory.css';

type ItemMeta={category:string;rarity:string;effect:string;healing?:string;damage?:string;range?:string;weight?:string;description:string};
const itemMeta:Record<string,ItemMeta>={
 potion:{category:'Расходуемое',rarity:'Обычное',effect:'Восстанавливает здоровье',healing:'+20 HP',weight:'0.5 кг',description:'Небольшой флакон с алой жидкостью. Пахнет травами и чем-то подозрительно сладким.'},
 torch:{category:'Снаряжение',rarity:'Обычное',effect:'Освещает тёмные места',damage:'1d4 огнём',weight:'0.5 кг',description:'Простой факел. Горит около часа и позволяет видеть в темноте.'},
 dagger:{category:'Оружие',rarity:'Обычное',effect:'Ближний колющий удар',damage:'1d4 колющего',range:'5 фт',weight:'1 кг',description:'Лёгкий кинжал с узким лезвием. Удобен для скрытных атак и ближнего боя.'},
 shortsword:{category:'Оружие',rarity:'Обычное',effect:'Ближний рубящий удар',damage:'1d6 колющего',range:'5 фт',weight:'1 кг',description:'Короткий универсальный меч для ближнего боя.'},
 leather_armor:{category:'Броня',rarity:'Обычное',effect:'Увеличивает защиту',weight:'5 кг',description:'Лёгкая кожаная броня, не сковывающая движения.'},
 mana_scroll:{category:'Магия',rarity:'Необычное',effect:'Одноразовое заклинание',weight:'0.1 кг',description:'Свиток с магической формулой. Бумага слегка мерцает.'},
 antidote:{category:'Расходуемое',rarity:'Обычное',effect:'Снимает отравление',healing:'Снимает яд',weight:'0.3 кг',description:'Густая зелёная жидкость с резким травяным запахом.'},
 rope:{category:'Снаряжение',rarity:'Обычное',effect:'Верёвка 10 м',weight:'2 кг',description:'Крепкая пеньковая верёвка для подъёма, связывания и других приключенческих задач.'}
};
function metaFor(item:{item_key:string;description?:string|null}):ItemMeta{return itemMeta[item.item_key]??{category:'Предмет',rarity:'Обычное',effect:'Без специального эффекта',description:item.description||'Описание предмета пока не добавлено.'};}

export default function InventoryPage(){
 const [inventory,setInventory]=useState<InventoryItem[]>([]);const [shop,setShop]=useState<ShopItem[]>([]);const [gold,setGold]=useState(0);const [selectedId,setSelectedId]=useState<number|null>(null);const [loading,setLoading]=useState(true);const [error,setError]=useState('');const [dragKey,setDragKey]=useState<string|null>(null);const [characterExists,setCharacterExists]=useState(false);
 const load=async()=>{setLoading(true);setError('');try{const [user,items,store]=await Promise.all([me(),getInventory(),getShop()]);setCharacterExists(Boolean(user.character));setGold(user.gold);setInventory(items);setShop(store.items);setSelectedId(items[0]?.id??null)}catch(e){setError(e instanceof Error?e.message:'Не удалось загрузить инвентарь')}finally{setLoading(false)}};
 useEffect(()=>{load()},[]);
 const selected=inventory.find(item=>item.id===selectedId)??inventory[0];const meta=selected?metaFor(selected):null;const totalItems=inventory.reduce((sum,item)=>sum+item.quantity,0);
 const grouped=useMemo(()=>shop.reduce<Record<string,ShopItem[]>>((groups,item)=>{(groups[item.category]??=[]).push(item);return groups},{}),[shop]);
 const buy=async(itemKey:string)=>{setError('');try{const result=await buyShopItem(itemKey);setGold(result.gold);setInventory(result.inventory);setSelectedId(result.inventory.find(x=>x.item_key===itemKey)?.id??result.inventory[0]?.id??null)}catch(e){setError(e instanceof Error?e.message:'Не удалось купить предмет')}};
 const handleDrop=(event:DragEvent)=>{event.preventDefault();if(dragKey)void buy(dragKey);setDragKey(null)};
 return <section className="page-panel inventory-page">
  <div className="inventory-page-head"><div><div className="panel-title"><Backpack size={16}/><span>ИНВЕНТАРЬ</span></div><h1>Снаряжение героя</h1><p>Пустой рюкзак после создания персонажа. Новые предметы покупаются в магазине.</p></div><div className="inventory-counter"><strong>{totalItems}</strong><span>предметов</span></div></div>
  {error&&<div className="inventory-error">{error}</div>}
  {loading?<div className="inventory-loading">Загрузка инвентаря...</div>:<div className="inventory-layout">
   <div className="inventory-column">
    <div className="inventory-section-title"><span>ТВОЙ ИНВЕНТАРЬ</span><small>{characterExists?`${inventory.length} вида`:'Персонаж не создан'}</small></div>
    <div className={`inventory-dropzone ${dragKey?'drag-active':''}`} onDragOver={e=>e.preventDefault()} onDrop={handleDrop}>
     {inventory.length===0?<div className="inventory-empty"><Backpack size={42}/><h2>{characterExists?'Рюкзак пуст':'Сначала создай персонажа'}</h2><p>{characterExists?'Перетащи предмет из магазина сюда, чтобы купить его.':'После создания героя здесь появится его рюкзак.'}</p></div>:<div className="inventory-list">{inventory.map(item=>{const itemMetaValue=metaFor(item);return <button key={item.id} className={`inventory-card ${selected?.id===item.id?'selected':''}`} onClick={()=>setSelectedId(item.id)}><span className="inventory-card-icon">{item.icon}</span><span className="inventory-card-main"><strong>{item.name}</strong><small>{itemMetaValue.category} · {itemMetaValue.rarity}</small></span><span className="inventory-card-count">x{item.quantity}</span><ChevronRight size={17}/></button>})}</div>}
    </div>
    {selected&&meta&&<article className="inventory-detail"><div className="inventory-detail-top"><span className="inventory-detail-icon">{selected.icon}</span><div><span className="inventory-kicker">{meta.category.toUpperCase()}</span><h2>{selected.name}</h2><span className="inventory-rarity">{meta.rarity}</span></div><div className="inventory-detail-count">x{selected.quantity}</div></div><p className="inventory-description">{meta.description}</p><div className="inventory-properties"><div><span><ScrollText size={15}/> ЭФФЕКТ</span><b>{meta.effect}</b></div>{meta.healing&&<div><span><Heart size={15}/> ЛЕЧЕНИЕ</span><b className="inventory-positive">{meta.healing}</b></div>}{meta.damage&&<div><span><Swords size={15}/> УРОН</span><b>{meta.damage}</b></div>}{meta.range&&<div><span><Flame size={15}/> ДАЛЬНОСТЬ</span><b>{meta.range}</b></div>}{meta.weight&&<div><span><Weight size={15}/> ВЕС</span><b>{meta.weight}</b></div>}</div></article>}
   </div>
   <aside className="shop-panel"><div className="shop-head"><div><span className="shop-kicker">ТОРГОВАЯ ЛАВКА</span><h2>Магазин</h2><p>Перетащи предмет в инвентарь, чтобы купить его.</p></div><div className="gold-balance"><Coins size={18}/><strong>{gold}</strong><span>золота</span></div></div><div className="shop-categories">{Object.entries(grouped).map(([category,items])=><div className="shop-category" key={category}><div className="shop-category-title">{category}</div><div className="shop-items">{items.map(item=><div key={item.item_key} className={`shop-item ${gold<item.price||!characterExists?'disabled':''}`} draggable={characterExists&&gold>=item.price} onDragStart={()=>setDragKey(item.item_key)} onDragEnd={()=>setDragKey(null)} onDoubleClick={()=>characterExists&&void buy(item.item_key)} title={characterExists?'Перетащи в инвентарь для покупки':'Сначала создай персонажа'}><span className="shop-item-icon">{item.icon}</span><span className="shop-item-main"><strong>{item.name}</strong><small>{item.description}</small></span><span className="shop-price"><Coins size={13}/>{item.price}</span></div>)}</div></div>)}</div></aside>
  </div>}
 </section>;
}
