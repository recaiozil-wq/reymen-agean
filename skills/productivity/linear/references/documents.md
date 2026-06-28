---
skill_id: 21f64da1e579
usage_count: 1
last_used: 2026-06-16
---
## Documents

Linear **Documents** are prose docs (RFCs, specs, notes) stored alongside issues. They have their own `documents` root query and `document(id:)` single-fetch.

### Document URLs and `slugId`

Document URLs look like:
```
https://linear.app/<workspace>/document/<slug>-<hexSlugId>
```

The trailing hex segment is the `slugId`. Example: `https://linear.app/nousresearch/document/rfc-hermes-permission-gateway-discord-38359beef67c` → `slugId` is `38359beef67c`.

**Important schema detail:** the Markdown body is in the `content` field. The ProseMirror JSON is in `contentState` (not `contentData` — that field does not exist and the API returns 400).

### Fetch a document by slugId

`document(id:)` only accepts UUIDs. To fetch by the URL's hex slug, filter the collection:

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "query($s: String!) { documents(filter: { slugId: { eq: $s } }, first: 1) { nodes { id title content contentState slugId url creator { name } project { name } updatedAt } } }", "variables": {"s": "38359beef67c"}}' \
  | python3 -m json.tool
```

Or via the Python helper:
```bash
python3 scripts/linear_api.py get-document 38359beef67c
```

### Fetch a document by UUID

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ document(id: \"11700cff-b514-4db3-afcc-3ed1afacba1c\") { title content url } }"}' \
  | python3 -m json.tool
```

### List recent documents

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ documents(first: 25, orderBy: updatedAt) { nodes { id title slugId url updatedAt project { name } } } }"}' \
  | python3 -m json.tool
```

### Search documents by title

Linear's schema has no `searchDocuments` root. Use a title-substring filter instead:

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ documents(filter: { title: { containsIgnoreCase: \"RFC\" } }, first: 25) { nodes { title slugId url } } }"}' \
  | python3 -m json.tool
```