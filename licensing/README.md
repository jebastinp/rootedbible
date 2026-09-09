# Restricted-by-default edition inventory

`translations.json` records requirements and unknowns. **Every record is pending.**
The named legacy IDs do not establish the exact requested Indic editions or their
rights holders. Do not replace unknown values with guesses.

The current backend uses this registry for catalog and direct Bible lookup. It
supports only reviewed worldwide, unlimited-user, stored-text web grants; other
delivery scopes stay unavailable until matching controls are implemented. Native
and public release remain blocked. A malformed, missing or duplicate registry
fails closed. Configure an external reviewed copy with `ROOTED_LICENSE_REGISTRY`
(absolute path) in deployments where this folder is not mounted.

No agreement is included or signed by these files. A code review cannot grant
rights. Exact attribution, approved source binding to an immutable deployed
dataset, scoped API/native adapters and independent content QA are still release
requirements. The initial guard is defense in depth, not a complete publishing
system.

Private grant evidence belongs in restricted storage; `evidence/` is ignored by
Git. Source packages belong outside the repo or in ignored `content-sources/`.
Do not put provider credentials, contracts or full licensed text in public JSON.

See [workflow and rights research](../docs/rooted/07-bible-licensing.md).
