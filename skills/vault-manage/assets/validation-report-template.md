VALIDATION_REPORT
status: PASS|FAIL
target: <module-or-note-path>
checks:
  - dead-links: PASS|FAIL|N/A - <reason>
  - metadata-required-fields: PASS|FAIL|N/A - <reason>
  - attachments-boundary: PASS|FAIL|N/A - <reason>
  - reference-note-location: PASS|FAIL|N/A - <reason>
  - last-updated-git-modified: PASS|FAIL|N/A - <reason>
issues:
  - <path>: <issue> -> <required fix>
summary:
  accepted: <count>
  rejected: <count>
  n_a: <count>
next_action:
  - <single explicit next step>
