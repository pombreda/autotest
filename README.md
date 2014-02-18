autotest
========

Autotest tool - Minimalistic Continuous Integration for git

* Runs with python2.7 and python3.3 (others not tested).
* Runs a test-command, on failure it sends a notification to all users who have
  contributed to the branch since the last sucessful test.
* The test-command should return 0 on success.

Usage
-----

1. autotest -s path/to/settings.json init
2. vi path/to/settings.json
3. autotest -spath/to/settings.json test

Tips
----

1. Use multiple settings files for multiple tests/branches.
2. Use [.mailmap](http://www.kernel.org/pub/software/scm/git/docs/git-shortlog.html)
   if users have inconsistant email addresses.
