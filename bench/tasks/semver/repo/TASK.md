# Latest version

Our release script asks `latest` in versions.py for the newest release, but it compares the versions as text, so 1.9.0 beats 1.10.0. Make it compare versions properly.
