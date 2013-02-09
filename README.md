autotest
========

Ultra slim CI for git

* Runs with python2.7 and python3.2 (others not tested).
* Runs a test-command, on failure it sends a notification to all users that have
  contributed to the branch since the last sucessful test.
* The test-command should return 0 on success.

Usage
-----

1. Start it once
2. Edit settings.json
3. Run it again

Tip: Use multiple directories for multiple tests
