import type {PublicEntry} from './public-catalog.mjs';
export type SitePayload={categories:string[][];entries:PublicEntry[]};
export const root:string;
export function scriptJSON(value:unknown):string;
export function sitePayload(options?:{projectRoot?:string}):Promise<SitePayload>;
export function siteMarkup(options?:{projectRoot?:string;payload?:SitePayload;lang?:'fr'|'en';prefix?:string}):Promise<string>;
export function withSiteHeader(template:string,options?:{lang?:'fr'|'en';prefix?:string;payload?:SitePayload}):string;
