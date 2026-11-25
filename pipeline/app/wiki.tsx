'use client';
import {useEffect,useRef} from 'react';
import Script from 'next/script';
declare global {interface Window {WowForeverWiki?:{initWiki:(root:Element|Document)=>()=>void}}}
export default function Wiki({lang,markup}:{lang:'fr'|'en';markup:string}){
 const element=useRef<HTMLDivElement>(null),cleanup=useRef<(()=>void)|undefined>(undefined);
 function mount(){cleanup.current?.();if(element.current)cleanup.current=window.WowForeverWiki?.initWiki(element.current);}
 useEffect(()=>()=>{cleanup.current?.()},[]);
 return <><div id="wiki-app" data-language={lang} lang={lang} ref={element} dangerouslySetInnerHTML={{__html:markup}}/><Script id="wow-forever-controller" src="/wiki/app.js" type="module" strategy="afterInteractive" onReady={mount}/></>;
}
