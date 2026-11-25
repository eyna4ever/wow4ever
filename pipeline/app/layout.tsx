import type {Metadata} from 'next';
export const metadata:Metadata={title:'WoW Forever Wiki — Archives & aventures',description:'Encyclopédie fantasy bilingue indépendante, en construction.',robots:{index:false,follow:false},manifest:'/manifest.webmanifest'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="fr"><head><link rel="stylesheet" href="/wiki/site.css"/></head><body>{children}</body></html>}
