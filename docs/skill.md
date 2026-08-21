# Install the Pay-IT integration skill — agent prompt (v1)

Give this file, together with `guides-v1.zip`, to an AI coding agent. Everything below the line is addressed to that agent.

---

You are installing the **Pay-IT integration skill** from the archive `guides-v1.zip`.

## Rule: ask before you extract

Do not unzip anything, create any directory, or write any file until the user has answered the questions in Step 1 and confirmed the resulting plan in Step 3. If you cannot ask the user — you are running non-interactively — stop and say so rather than guessing an install location.

Inspecting the archive listing without extracting (`unzip -l`, `tar -tf`, or equivalent) is allowed and encouraged, because you need it to confirm the archive is the expected one.

## Step 0: locate the archive

Confirm you can see `guides-v1.zip`. If you cannot, ask the user for its path. Do not download it from anywhere.

List its contents without extracting. Expect ten entries under a single top-level `guides/` folder:

```
guides/README.md
guides/api-credentials.md
guides/direct-api-integration.md
guides/payment-links.md
guides/webhooks.md
guides/skills/README.md
guides/skills/integration/SKILL.md
```

If the listing differs materially, stop and report what you found instead of proceeding.

## Step 1: ask the user these questions

Ask all of them at once, as a short numbered list. Do not ask them one at a time.

**1. Where should the skill be installed?**

| Option | Target | Use when |
|---|---|---|
| A | Claude Code — **personal**: `~/.claude/skills/payit-integration/` | The user wants it available in every project on this machine. |
| B | Claude Code — **project**: `<repo>/.claude/skills/payit-integration/` | The user wants it committed with, and scoped to, one repository. |
| C | Harness-agnostic project: `<repo>/.agents/skills/payit-integration/` | The repository already uses `.agents/`, or the user wants the skill readable by more than one agent tool. Check for an existing `.agents/skills/` directory before offering this — if one exists, recommend it. |
| D | Another agent harness | The user works in Cursor, Continue, Aider, OpenCode, Cline, Roo, or similar. Ask which one, and where that tool loads instruction files from — do not assume a path. |
| E | Current directory | The user wants it unpacked here, at `./payit-integration/`. |
| F | Custom path | The user supplies the exact directory. |

Look for existing `.claude/skills/` or `.agents/skills/` directories in the repository before asking, and if one exists, say so in the question and recommend matching it. Otherwise recommend **A** for general use, or **B** when the integration work is scoped to one repository. Say which you are recommending and why.

Note that `.agents/` and `.claude/` are sometimes deliberately excluded from version control. Check `.gitignore` and `.git/info/exclude` before assuming an install there can be committed.

**2. If option B, C, or another repository-scoped install: which repository?** Ask for the repository root. Do not infer it from the current working directory without confirming.

**3. Should the reference guides be installed alongside the skill?** Default **yes**. The skill is written to read all five guides and will refuse to design an integration without them. Answer no only if the user already has the guides installed elsewhere and will tell you where.

**4. What should happen if something already exists at the target?** Offer: overwrite, install beside it under a different folder name, or abort. Default to **abort** unless the user chooses otherwise.

**5. Should a pointer to the skill be added to the project's documentation?** Only ask when installing into a repository. First check which of these exist at the repository root, and list only the ones you actually found:

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- any agent instruction file the repository already uses, such as a router `AGENTS.md` in a subdirectory

Offer to add a short pointer to any, all, or none of them. Default to **none** — an unrequested edit to a project's instruction files is intrusive, and some repositories generate or symlink them.

If the user says yes, add one or two lines in the file's existing style, in the section where similar tooling is already listed. For example, a row in an existing skills table, or a bullet under an existing "available skills" heading. Do not restructure the file, do not add a new top-level section unless there is nowhere sensible to put it, and do not reformat surrounding content. State the skill's name (`payit-integration`), its installed path, and one line on what it does.

Before editing, check whether the file is tracked by Git or excluded — `AGENTS.md` and `CLAUDE.md` are local-only in some repositories, and a pointer added to an ignored file will not reach anyone else. Tell the user what you find rather than deciding for them.

**6. Should the install be committed to version control?** Only relevant when the target, or any documentation file you changed, is inside a Git repository and tracked. Ask; do not commit unless the user says yes.

Wait for the answers.

## Step 2: work out the layout

Most agent harnesses, Claude Code included, discover a skill at exactly one nesting level: `<skills-root>/<skill-name>/SKILL.md`. The archive stores `SKILL.md` three levels deep, at `guides/skills/integration/SKILL.md`, so **you cannot simply copy the archive tree into a skills directory** — the skill would not be discovered.

Install this layout instead:

```
<target>/payit-integration/
├── SKILL.md                        (from guides/skills/integration/SKILL.md)
└── reference/
    ├── README.md
    ├── api-credentials.md
    ├── direct-api-integration.md
    ├── payment-links.md
    └── webhooks.md
```

`guides/skills/README.md` is an index for humans browsing the archive. It is not part of the skill; do not install it.

### The path rewrite is mandatory

`SKILL.md` references the guides as `../../README.md` and so on, which resolves correctly only inside the archive's original tree. Once `SKILL.md` sits one level under a skills root, `../../` points outside the skills directory entirely and every reference breaks.

After copying, rewrite these five lines in the installed `SKILL.md`:

| Before | After |
|---|---|
| `../../README.md` | `reference/README.md` |
| `../../api-credentials.md` | `reference/api-credentials.md` |
| `../../direct-api-integration.md` | `reference/direct-api-integration.md` |
| `../../webhooks.md` | `reference/webhooks.md` |
| `../../payment-links.md` | `reference/payment-links.md` |

Change nothing else in `SKILL.md`. In particular, leave the YAML frontmatter (`name: payit-integration` and its `description`) exactly as it is — harnesses use those fields to decide when the skill applies.

If the user answered "no" to question 3, point the five references at wherever they said the guides already live, and verify each target file exists before finishing.

For option D, adapt the layout to that tool's convention rather than forcing the one above — some harnesses expect a single flat instruction file, others a folder per skill. Read the tool's own documentation or an existing installed skill to determine the convention. Keep the path rewrite consistent with whatever layout you choose.

## Step 3: confirm, then install

Present the exact plan before touching the filesystem:

- the absolute target directory;
- every file you will create;
- anything you will overwrite;
- the five path rewrites;
- any documentation file you will modify, and the exact lines you will add to it;
- whether you will commit.

Ask for explicit confirmation. Then extract to a temporary directory, assemble the layout, and move it into place. Do not extract directly over the target — a partial extraction on top of an existing install is hard to unpick.

## Step 4: verify and report

Check, and report the result of each:

1. `SKILL.md` exists at the expected depth for the chosen harness.
2. Its frontmatter is intact and parses as YAML.
3. All five `reference/` guides exist and are non-empty.
4. All five rewritten paths resolve to real files, checked relative to the installed `SKILL.md`.
5. No `../../` references remain in the installed `SKILL.md`.
6. If you edited a documentation file: the pointer is present, any path or link in it resolves, and nothing else in the file changed. Show the diff.

Then tell the user:

- where it was installed;
- how to invoke it in their harness — for Claude Code, the skill activates by description, and the user can also ask for it by name (`payit-integration`);
- that the skill's own first step is an integration interview, so it will ask its own questions before writing any integration code;
- that the guides in `reference/` describe the Pay-IT API as verified on 19 August 2026, and that `spec.yaml` in the Pay-IT repository is the contract authority if the two ever disagree;
- anything you could not verify.

Do not claim the install succeeded if any check in this step failed. Report the failure and what you tried.

## Step 5: offer the next action

Do not end the conversation with a report. Close with a choice, and ask it as the last thing you say:

> The Pay-IT skill is installed. What would you like to do next?
>
> **1. See it working** — I'll build a small runnable example of hosted checkout. Pick one:
>    - **Modal** — a Pay button that opens checkout in an overlay. The usual choice for a website.
>    - **Inline** — checkout embedded directly in a page region.
>    - **Redirect** — a link that sends the customer to a full Pay-IT checkout page.
> **2. Start integrating** — I'll begin a real integration into your codebase.
> **3. Nothing for now** — the skill is ready whenever you need it.

### If they choose an example

Ask for a **published Payment Link slug** first. Without one there is nothing to open, and you must not invent one.

Then tell them what that mode actually needs before you write anything:

- **Redirect** works immediately. It needs only a published slug — no origin registration, no backend. It provides no completion callbacks.
- **Modal** and **inline** additionally require the page's **exact origin** to be registered on that Payment Link through `embed-origins/configure`, which needs a merchant JWT and the link's current `Version`. If it is not registered, checkout fails closed as an indistinguishable `404` — this is by design, not a bug in your example. Say so up front rather than letting them discover it.
- Modal and inline cannot run from a `file://` page, because it has no origin. Serve the file over HTTP. Only `http://localhost` is accepted against a development backend, and never an IP literal such as `127.0.0.1`. Against production, the origin must be a registered `https://` host.

Build a **single self-contained `.html` file** — a script tag and a few lines of JavaScript, no framework, no build step, no dependencies. Follow the example for that mode in `reference/payment-links.md`; do not improvise the SDK's option names. Ask where to save it, and default to a scratch or example directory rather than anywhere the project builds or deploys from.

Label it plainly as a demonstration. It must contain no API key, no webhook secret, and no merchant JWT — a browser page never holds those. After writing it, tell them exactly how to serve and open it, and what they should expect to see.

Say clearly that a working example proves checkout **opens**, not that an order is **paid**. Fulfilment requires a verified webhook or a server-side status check, which a static page cannot do.

### If they choose to integrate

Hand straight over to the installed `payit-integration` skill and follow it from its first step. That skill opens with its own integration interview and its own approval checkpoint — do not skip either, do not pre-answer its questions from anything said during installation, and do not write integration code before it has presented a plan and received explicit approval.

### If they choose neither

Confirm where the skill lives and how to invoke it later. Stop there.

## Do not

- Do not extract before the user has answered Step 1 and confirmed Step 3.
- Do not edit the guides in `reference/`. They are reference material, not templates.
- Do not alter the `SKILL.md` frontmatter or its instructions beyond the five path rewrites.
- Do not install into a location that requires elevated privileges. Ask the user to choose a different path instead.
- Do not edit `README.md`, `AGENTS.md`, `CLAUDE.md`, or any other project file unless the user answered yes to question 5, and then only to add the agreed pointer.
- Do not commit anything unless the user answered yes to question 6.
- Do not begin an actual Pay-IT integration, or write an example file, until the user has chosen it in Step 5. Offering the choice is required; acting on it without an answer is not.
- Do not treat a Step 5 choice as consent to skip the `payit-integration` skill's own interview and approval checkpoint.
