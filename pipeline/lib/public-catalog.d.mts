export type PublicEntry = {
  id: string;
  title: {fr: string; en: string};
  description: {fr: string; en: string};
  category: string;
  subcategory: string;
  status: 'published';
  publicationValidated: true;
  gameVersion: string;
  version: number;
  updatedAt: string;
  sources: {url: string; accessedAt: string; license: string; title?: string; gameVersion?: string}[];
  relations: string[];
  history: {at: string; note: string; version?: number}[];
  steps?: {fr: string; en: string}[];
  tags?: {fr: string; en: string}[];
  eventDate?: string;
};
export function selectPublicEntries(records: unknown): PublicEntry[];
