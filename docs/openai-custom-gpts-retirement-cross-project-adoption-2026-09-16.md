# Cross-project adoption — Custom GPT retirement → Plugins

Date: 2026-09-16

Source assessment:
`docs/openai-custom-gpts-retirement-to-plugins-2026-09-16.md`

## Adoption status

The retirement/migration assessment has been applied to the projects coordinated through Sentinel Remote.

| Project | Adoption result |
|---|---|
| K_Research_Critic | Plugin-first strategic rebase; R3 package retained as migration source; design-only Plugin migration skeleton already prepared in PR #22 |
| K-Trader | Draft migration PR #59 created; existing `custom_gpt/` retained as legacy/migration source package |
| K-Geopolitical-Monitor | Draft migration/publication-boundary PR #109 created; future ChatGPT publication/integration is Plugin-first |
| K_AI-Trading-System | No Custom GPT deployment surface identified; no architecture/runtime change |
| K_Supervisor | No legacy Custom GPT deployment package identified; no architecture/runtime change |
| Sentinel-Remote | Cross-project control-plane policy updated: Builder is transitional, Plugins are the strategic ChatGPT product surface |

## Shared policy

```text
CUSTOM_GPT = LEGACY_TRANSITION_SURFACE
PLUGIN = STRATEGIC_CHATGPT_PRODUCT_SURFACE
CUSTOM_ACTIONS = MIGRATION_INPUT, NOT AUTOMATICALLY PORTABLE
PLUGIN_PUBLICATION = OWNER_GATED
```

No project publication, merge, migration, production deployment, paid-provider activation or runtime mutation is authorized merely by this adoption record.
