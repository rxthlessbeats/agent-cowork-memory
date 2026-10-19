Let's do TASK.md in two steps.

Step 1: write `parse(version)` in versions.py. It turns `"1.10.2"` into the tuple `(1, 10, 2)`. Plain X.Y.Z only for now, and leave `latest` alone.

Step 2, for later: make `latest` compare properly, with our odd tags in mind. Hotfix builds are tagged like `1.10.0-hotfix`, and a hotfix ranks above the same version without the suffix (but still below `1.10.1`). Some old releases use the two-part calendar scheme, like `2023.4`; those always rank below every three-part version. And `latest` returns the winner with a `v` in front (`v1.10.0`), because the release script passes it straight to git; the inputs never have one.

Do step 1 only for now, then stop. I'll come back for step 2.
