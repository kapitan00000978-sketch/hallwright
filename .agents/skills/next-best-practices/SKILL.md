---
name: next-best-practices
description: Author, optimize, and review Next.js applications (App Router, React Server Components, Server Actions, Partial Prerendering, and caching). Enforces sub-second TTFB, zero hydration mismatches, and pristine component boundaries.
metadata:
  source: vercel-labs/next-skills
  domain: modern-frontend
---

# Next.js Production Best Practices (Vercel Engineering Standards)

Comprehensive guidelines for modern Next.js 14/15+ App Router architectures.

## 1. Component Boundaries & RSC Directives
- **Server by Default:** Keep components as React Server Components (RSC) unless interactivity (useState, useEffect, event listeners) or browser APIs are required.
- **Client Leaf Pattern:** Push `'use client'` to the farthest leaf components in the tree to maximize streaming and server rendering.
- **Data Flow:** Fetch data directly inside Server Components using async/await. Pass serialized data down to Client Components as props.

## 2. Dynamic APIs & Route Handlers
- In Next.js 15, `cookies()`, `headers()`, and route `params` are asynchronous promises. Always `await` them.
- Avoid passing sensitive environment variables or un-sanitized server contexts into Client Component props.

## 3. Server Actions & Mutations
- Always validate inputs in Server Actions using Zod or typed schemas before executing database mutations.
- Revalidate paths precisely with `revalidatePath` or `revalidateTag` to update cache without reloading the whole layout.
- Wrap mutations with `useTransition` / `useActionState` on the client for optimistic UI updates.

## 4. Hydration & Performance
- Never render non-deterministic content (random numbers, current time, localStorage state) on the initial SSR render to prevent hydration mismatch errors.
- Wrap dynamic subtrees with `<Suspense fallback={<Skeleton />}>` to enable immediate streaming responses and progressive page hydration.
- Optimize assets using `next/image` with explicit aspect ratios and `next/font` for zero layout shift (CLS: 0).
