# Claude Code plugin load

Consumer: `claude plugin marketplace add` and `claude plugin install` users.
Drive: `verify.sh claude`.
Pass: `Validation passed` with no warnings. A `version` warning means `plugin.source.json` lost its version.
Not covered: the install-time "conflicting manifests" rejection. The validator passes on it; the unit tests guard it.
