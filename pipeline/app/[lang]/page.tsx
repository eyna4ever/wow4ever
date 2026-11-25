import {notFound} from 'next/navigation';
import Wiki from '../wiki';
import {siteMarkup} from '../../lib/site.mjs';
export const dynamic='force-dynamic';
export default async function Page({params}:{params:Promise<{lang:string}>}){const {lang}=await params;if(lang!=='fr'&&lang!=='en')notFound();return <Wiki lang={lang} markup={await siteMarkup({lang})}/>}
