URGENT: CognoDB is now provisioned and RUNNING.

Use the CognoDB connection details shown in the latest screenshot I provided.

IMPORTANT:
- Do NOT print the password in terminal output.
- Do NOT hardcode credentials in source code.
- Store credentials only in the root .env file.
- Ensure .env is in .gitignore.
- Do NOT expose the credentials in README, logs, Git history, or results.

Configure:

COGNODB_URI=<CognoDB Bolt URI from screenshot>
COGNODB_USERNAME=<CognoDB username from screenshot>
COGNODB_PASSWORD=<password from screenshot>

The CognoDB endpoint uses the Neo4j-compatible Bolt driver, so use the existing neo4j Python driver and the existing CognoDB adapter.

Then immediately run:

1. Environment validation
2. CognoDB connectivity test
3. Authentication test
4. RETURN 1
5. Create schema/index
6. Load the frozen benchmark dataset:
   - 47,168 nodes
   - 130,000 relationships
7. Validate node count
8. Validate relationship count
9. Validate age property
10. Run one sample traversal
11. Run one point lookup
12. Run one indexed lookup

Use batch UNWIND loading.

Do NOT modify the frozen dataset.

After completion, produce:

results/raw/cognodb.json

containing:
- connection status
- database version if available
- node count
- relationship count
- schema/index status
- loading time
- validation results
- sample workload results

Do not fabricate any values.

STOP after completing CognoDB integration and report the exact result.