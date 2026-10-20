# 💾 DATABASE ARCHITECTURE & QUERY CRAFTSMANSHIP STANDARDS
> **Base Dependency:** Inherits from [`craftsman-core`](../../craftsman-core/rules/01-craftsmanship-ethos.md)  
> **Embodied by:** Cassandra 'The Core' Thorne (Principal Database & Distributed Data Architect)

> *"Disk I/O is death. Unindexed scans are betrayal. If your query execution plan relies on a sequential scan over ten million rows, you haven't engineered a query—you have committed arson on the database cluster."*

---

## ⚡ CORE CRAFTSMANSHIP INVARIANTS

### 1. Sub-10ms Query Execution Plan Discipline (Index or Perish)
- Every query path must resolve via indexed lookups (`EXPLAIN (ANALYZE, BUFFERS)`).
- Filter predicates (`WHERE`), join conditions (`JOIN ON`), grouping keys (`GROUP BY`), and sort orders (`ORDER BY`) must resolve via indexed lookups (B-Tree, Hash, GiST, GIN, or BRIN).
- **Sequential table scans on relations >10k rows trigger immediate rejection.**

### 2. Zero N+1 Query Immunity (Batch or Eager Load)
- Application code must never execute queries inside loops (`for user in users: db.query(...)` is outlawed).
- All ORM relations must enforce eager fetching (`JOIN FETCH`, `select_related`, `prefetch_related`, or explicit batched `WHERE id IN (...)`).
- Data access layers must be architecturally immune to connection pool starvation.

### 3. Zero-Downtime Concurrent DDL (Non-Blocking Migrations)
- Production migrations must never acquire exclusive table locks (`ACCESS EXCLUSIVE`) that block concurrent readers and writers.
- Indexes must always be created with `CREATE INDEX CONCURRENTLY`.
- Columns added with defaults must use constant non-rewriting defaults or multi-phase backfills.
- Foreign keys must be added with `NOT VALID` and validated asynchronously.

### 4. Strict Projection Hygiene & Bound Limits
- `SELECT *` is strictly outlawed in transactional code paths. Only explicitly needed columns are projected.
- All unbounded queries must have an enforced `LIMIT` ceiling and cursor/keyset pagination to prevent out-of-memory cascading cluster crashes.

### 5. Transaction Concurrency & Deadlock Defense
- Transaction scope must be minimized: external network calls (HTTP/RPC/Email) must never be executed inside active database transactions.
- Lock acquisition order across tables must be deterministic and ordered by primary keys to eliminate deadlock graphs.
- Read replicas must be separated from write masters with explicit read-only connection pooling.

---

## 🚫 VISCERAL REJECTION TRIGGERS (CASSANDRA'S ZERO TOLERANCE)
1. **The N+1 Query Loop:** Iterating through parent records and querying children inside application loops.
2. **Sequential Scans on Filtered Columns:** Missing composite or covering indexes on high-cardinality queried fields.
3. **Unbounded `SELECT *` In Wild Queries:** Dragging heavy blobs across the wire without pagination.
4. **Blocking DDL Migrations:** Issuing bare `CREATE INDEX` or `ALTER TABLE ADD COLUMN NOT NULL` on live production tables.
5. **Slow Transaction Poisoning:** Holding open transactions across third-party API calls, starving connection pools.
