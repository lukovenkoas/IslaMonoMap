'use strict';
const image=document.getElementById('map'), viewer=document.getElementById('viewer');
const status=document.getElementById('status'), scale=document.getElementById('scale');
const variants={art:{src:'Isla_Mona_art.png',width:2400,height:2700,name:'художественную',alt:'Художественная карта Исла Моны: три высадки, посёлок, фактория, дороги и пещера'},technical:{src:'Isla_Mona.png',width:2600,height:2100,name:'техническую',alt:'Техническая карта Исла Моны с бухтами, дорогами, посёлком, факторией и схемами развилок'}};
let current='art',factor=1;
function resize(){const w=Math.max(1,viewer.clientWidth-20);image.style.width=`${Math.round(w*factor)}px`;scale.textContent=factor===1?'Вписано':`${Math.round(factor*100)}%`;document.getElementById('less').disabled=factor<=1;document.getElementById('more').disabled=factor>=4;}
function loaded(){status.textContent='Карта загружена.';viewer.setAttribute('aria-busy','false');resize();}
image.addEventListener('load',loaded);
image.addEventListener('error',()=>{status.textContent='Не удалось загрузить карту. Попробуйте открыть оригинал по ссылке ниже или обновить страницу.';viewer.setAttribute('aria-busy','false');});
function select(key){current=key;const v=variants[key];factor=1;viewer.scrollTo(0,0);status.textContent='Загрузка карты…';viewer.setAttribute('aria-busy','true');for(const id of Object.keys(variants))document.getElementById(id).setAttribute('aria-pressed',String(id===key));image.alt=v.alt;image.width=v.width;image.height=v.height;image.src=v.src;const link=document.getElementById('download');link.href=v.src;link.textContent=`Скачать ${v.name} карту · PNG`;document.getElementById('original').href=v.src;resize();if(image.complete&&image.naturalWidth)loaded();}
for(const key of Object.keys(variants))document.getElementById(key).addEventListener('click',()=>select(key));
document.getElementById('more').addEventListener('click',()=>{factor=Math.min(4,factor+.5);resize();});
document.getElementById('less').addEventListener('click',()=>{factor=Math.max(1,factor-.5);resize();});
document.getElementById('fit').addEventListener('click',()=>{factor=1;resize();viewer.scrollTo(0,0);});
window.addEventListener('resize',resize);resize();if(image.complete&&image.naturalWidth)loaded();
