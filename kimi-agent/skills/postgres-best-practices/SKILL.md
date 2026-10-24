---
name: postgres-best-practices
description: Production PostgreSQL engineering for high-concurrency applications. Enforces optimal B-tree and GIN indexing, sub-10ms query execution plans, connection pooling (PgBouncer/Supavisor), and deadlock-free transaction isolation.
metadata:
  source: supabase/skills
  domain: database-architecture
---

# PostgreSQL Production Best Practices (Supabase & Neon Standards)

Engineering guidelines for robust, high-performance PostgreSQL databases.

## 1. Indexing & Query Execution Plans
- **B-tree Indexes:** Always index foreign keys (`REFERENCES`) to avoid full table scans during cascading deletes and JOIN operations.
- **Composite Indexes:** Order composite index columns by equality filters first, then range/sorting operators (`WHERE tenant_id = ? AND created_at > ?` -> `INDEX (tenant_id, created_at)`).
- **EXPLAIN (ANALYZE, BUFFERS):** Verify query plans before shipping. Eliminate sequential scans on tables with >1,000 rows.
- **Partial Indexes:** Use `WHERE active = true` or `WHERE status = 'pending'` for skewed distributions to keep index size minimal and cache-resident.

## 2. Concurrency & Transaction Isolation
- **Lock Escalation Defense:** Avoid long-running transactions. Never hold database locks while performing external network requests (HTTP, email, Stripe calls).
- **Safe Migrations:** Add columns with default values as `DEFAULT ...` (instant in Postgres 11+). Create indexes concurrently with `CREATE INDEX CONCURRENTLY` to avoid table lockouts.
- **Deadlock Prevention:** Always acquire locks on rows in deterministic primary-key order (`SELECT ... FOR UPDATE ORDER BY id`).

## 3. Connection Pooling & Resource Scaling
- Use connection poolers (PgBouncer in transaction mode or Supavisor) to support thousands of concurrent client connections without memory exhaustion.
- Enforce strict query timeouts: `statement_timeout = '5s'` to prevent rogue runaway queries from starving connection pools.
