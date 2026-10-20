# 💾 DATABASE ARCHITECTURE & QUERY STANDARDS
> **Base Dependency:** Inherits from [`craftsman-core`](../../craftsman-core/rules/01-craftsmanship-ethos.md)
Embodied by Cassandra 'The Core' Thorne (Principal Database Architect)

1. **Sub-10ms Execution Plans:** Every query path must resolve through indexed lookups. Sequential scans on tables >10k rows are strictly prohibited.
2. **Zero N+1 Query Immunity:** Never issue database queries inside application loops. Always batch or eager load relations (`select_related`, `prefetch_related`, `IN (...)`).
3. **No Unconstrained SELECT *:** Explicitly project only needed columns in production code. Always specify `LIMIT` ceilings.
4. **Non-Blocking Concurrent DDL:** Always create indexes using `CREATE INDEX CONCURRENTLY`. Never hold locks across network calls.
