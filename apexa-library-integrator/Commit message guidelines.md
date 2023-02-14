# Commit message guidelines

This convention dovetails with [SemVer](https://semver.org/), by describing the features, fixes, and breaking
changes made in commit messages.

The commit message should be structured as follows:
```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The `type` and `description` fields are mandatory, all other fields are optional.

## Allowed `<type>` values
1. fix : a commit of the type fix patches a bug in your codebase (this correlates with PATCH in
   Semantic Versioning).
   * Examples:
     * Commit message with fix type, description and breaking change footer
       ```text
       fix: allow provided config object to extend other configs
       BREAKING CHANGE: `extends` key in config file is now used for extending other config
       files
       ```
     * Commit message with fix type, scope and description
       ```text
       fix(plugins): correct minor typos in code
       ```
2. feat : a commit of the type feat introduces a new feature to the codebase this correlates with MINOR in Semantic Versioning).
    * Examples:
      * Commit message with only feat type
         ```text
         feat: allow provided config object to extend other configs
         ```
      * Commit message with feat type and an optional ! to draw attention to breaking change
         ```text
         feat!: drop support for Node 6
         ```
      * Commit message with feat type, scope and description
         ```text
         feat(lang): add polish language
         ```
3. docs: Documentation only changes
    * Examples:
      * Commit message with only docs type
         ```text
         docs: correct spelling of CHANGELOG
         ```
      * Commit message with docs type, scope and description
         ```text
         docs(changelog): update changelog to beta.5
         ```
4. style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
    * Examples:
      * Commit message with only style type
         ```text
         style: convert tabs to spaces
         ```
      * Commit message with style type, scope and description
         ```text
         style(css): convert tabs to spaces
         ```
5. refactor: A code change that neither fixes a bug nor adds a feature
    * Examples:
      * Commit message with only refactor type
         ```text
         refactor: add support for Node 8
         ```
      * Commit message with refactor type, scope and description
         ```text
         refactor(www): use `h1` element for page titles
         ```
6. perf: A code change that improves performance
    * Examples:
      * Commit message with only perf type
         ```text
         perf: remove unused logging
         ```
      * Commit message with perf type, scope and description
         ```text
         perf(www): remove unused logging
         ```
7. test: Adding missing tests or correcting existing tests
    * Examples:
      * Commit message with only test type
         ```text
         test: ensure X is handled
         ```
      * Commit message with test type, scope and description
         ```text
         test(www): ensure X is handled
         ```
8. build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
    * Examples:
      * Commit message with only build type
         ```text
         build: bump gulp-sass to 4.0.0
         ```
      * Commit message with build type, scope and description
         ```text
         build(gulp): bump gulp-sass to 4.0.0
         ```
9. ci: Changes to our CI configuration files and scripts (example scopes: GitLabCI)
    * Examples:
      * Commit message with only ci type
         ```text
         ci: use npm ci
         ```
      * Commit message with ci type, scope and description
         ```text
         ci(GitLabCI): use npm ci
         ```
10. BREAKING CHANGE: a commit that has a footer BREAKING CHANGE:, or appends `!` after the type/scope, introduces a breaking API change (correlating with MAJOR in Semantic Versioning). A BREAKING CHANGE can be part of commits of any type.
    * Examples:
      * Commit message with a breaking change footer
         ```text
         fix: correct minor typos in code
         BREAKING CHANGE: This commit includes a breaking change
         ```
      * Commit message with a breaking change footer and ! to draw attention to breaking change
         ```text
         feat!: drop support for Node 6
         BREAKING CHANGE: This commit includes a breaking change
         ```
      * Commit message with a breaking change footer and ! to draw attention to breaking change
         ```text
         feat!: drop support for Node 6
         BREAKING CHANGE: This commit includes a breaking change
         ```

### Example of Commit message with multi-paragraph body and multiple footers
```text
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Refs: #<issue number>
```

### Handling revert commits

Reverting code can be complicated: are you reverting multiple commits? if you revert a feature, should the next release instead be a patch?

Conventional Commits does not make an explicit effort to define revert behavior. Instead, we leave it to tooling authors to use the flexibility of types and footers to develop their logic for handling reverts.

One recommendation is to use the revert type, and a footer that references the commit SHAs that are being reverted:
```text
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

### Do all commits have to follow the Conventional Commits specification?

No! If you use a squash based workflow on Git lead maintainers can clean up the commit messages as they’re merged—adding no workload to casual committers. A common workflow for this is to have your git system automatically squash commits from a pull request and present a form for the lead maintainer to enter the proper git commit message for the merge.

### What do I do if I accidentally use the wrong commit type?

#### When you used a type that’s of the spec but not the correct type, e.g. fix instead of feat

Prior to merging or releasing the mistake, we recommend using git rebase -i to edit the commit history. After release, the cleanup will be different according to what tools and processes you use.
#### When you used a type not of the spec, e.g. feet instead of feat

In the worst case scenario, it’s not the end of the world if a commit lands that does not meet the Conventional Commits specification. It simply means that commit will be missed by tools that are based on the spec.
