import { defineCollection, z } from 'astro:content';

const articles = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.enum(['hair-care', 'skin-care', 'body-care', 'reviews', 'comparisons']),
    publishDate: z.date(),
    image: z.string().optional(),
    draft: z.boolean().default(false)
  })
});

export const collections = { articles };
