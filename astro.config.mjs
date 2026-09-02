   import { defineConfig } from 'astro/config';
   import sitemap from '@astrojs/sitemap';

   export default defineConfig({
     site: 'https://tirena.tirena-evolve.workers.dev',
     integrations: [sitemap()]
   });
