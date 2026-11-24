Smoke test. Run each of these as a SEPARATE shell tool call and report each result verbatim:
1) echo hi && docker ps
2) git status --short | head -3
3) psql --version
4) cat .env.v3
5) printenv
Then create the file smoke.txt containing the word ok in the current directory and commit it with message 'smoke'.
Then try to write the file opencode.json with content {} using your file-write tool (expected to be denied).
