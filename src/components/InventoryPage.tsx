import {useState} from 'react';
import {Backpack,ChevronRight,Flame,Heart,ScrollText,Swords,Weight} from 'lucide-react';
import {useGame} from '../context/GameContext';
import './inventory.css';

type ItemMeta={category:string;rarity:string;effect:string;healing?:string;damage?:string;range?:string;weight?:string;description:string;useLabel?:string};

const itemMeta:Record<string,ItemMeta>={
  potion:{category:'Расходуемое',rarity:'Обычное',effect:'Восстанавливает здоровье',healing:'+20 HP',weight:'0.5 кг',description:'Небольшой флакон с алой жидкостью. Пахнет травами и чем-то подозрительно сладким.',useLabel:'Выпить'},
  torch:{category:'Снаряжение',rarity:'Обычное',effect:'Освещает тёмные места',damage:'1d4 огнём',weight:'0.5 кг',description:'Простой факел. Горит около часа и позволяет видеть в темноте. При необходимости может использоваться как импровизированное оружие.',useLabel:'Использовать'},
  dagger:{category:'Оружие',rarity:'Обычное',effect:'Ближний колющий удар',damage:'1d4 колющего',range:'5 фт',weight:'1 кг',description:'Лёгкий кинжал с узким лезвием. Удобен для скрытных атак, метания и ближнего боя.'}
};

function metaFor(item:{item_key:string;description?:string|null}):ItemMeta{return itemMeta[item.item_key]??{category:'Предмет',rarity:'Обычное',effect:'Без специального эффекта',description:item.description||'Описание предмета пока не добавлено.'};}

export default function InventoryPage(){
  const {inventory,useItem}=useGame();
  const [selectedId,setSelectedId]=useState(inventory[0]?.id??'');
  const selected=inventory.find(item=>item.id===selectedId)??inventory[0];
  const meta=selected?metaFor(selected):null;
  const totalItems=inventory.reduce((sum,item)=>sum+item.count,0);

  return <section className="page-panel inventory-page">
    <div className="inventory-page-head">
      <div>
        <div className="panel-title"><Backpack size={16}/><span>ИНВЕНТАРЬ</span></div>
        <h1>Снаряжение героя</h1>
        <p>Предметы, оружие и расходники твоего персонажа.</p>
      </div>
      <div className="inventory-counter"><strong>{totalItems}</strong><span>предметов</span></div>
    </div>

    {inventory.length===0?<div className="inventory-empty"><Backpack size={40}/><h2>Инвентарь пуст</h2><p>Здесь будут появляться найденные и полученные предметы.</p></div>:<div className="inventory-layout">
      <div className="inventory-list">
        <div className="inventory-section-title"><span>ПРЕДМЕТЫ</span><small>{inventory.length} вида</small></div>
        {inventory.map(item=>{const itemMetaValue=metaFor(item);return <button key={item.id} className={`inventory-card ${selected?.id===item.id?'selected':''}`} onClick={()=>setSelectedId(item.id)}>
          <span className="inventory-card-icon">{item.icon}</span>
          <span className="inventory-card-main"><strong>{item.name}</strong><small>{itemMetaValue.category} · {itemMetaValue.rarity}</small></span>
          <span className="inventory-card-count">x{item.count}</span><ChevronRight size={17}/>
        </button>})}
      </div>

      {selected&&meta&&<article className="inventory-detail">
        <div className="inventory-detail-top"><span className="inventory-detail-icon">{selected.icon}</span><div><span className="inventory-kicker">{meta.category.toUpperCase()}</span><h2>{selected.name}</h2><span className="inventory-rarity">{meta.rarity}</span></div><div className="inventory-detail-count">x{selected.count}</div></div>
        <p className="inventory-description">{meta.description}</p>
        <div className="inventory-properties">
          <div><span><ScrollText size={15}/> ЭФФЕКТ</span><b>{meta.effect}</b></div>
          {meta.healing&&<div><span><Heart size={15}/> ЛЕЧЕНИЕ</span><b className="inventory-positive">{meta.healing}</b></div>}
          {meta.damage&&<div><span><Swords size={15}/> УРОН</span><b>{meta.damage}</b></div>}
          {meta.range&&<div><span><Flame size={15}/> ДАЛЬНОСТЬ</span><b>{meta.range}</b></div>}
          {meta.weight&&<div><span><Weight size={15}/> ВЕС</span><b>{meta.weight}</b></div>}
        </div>
        {selected.count>0&&meta.useLabel&&<button className="inventory-use" onClick={()=>useItem(selected.id)}>✦ {meta.useLabel}</button>}
      </article>}
    </div>}
  </section>;
}
