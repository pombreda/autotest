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

Tips
----

1. Use multiple directories for multiple tests.
2. You don't have to use ssh and port forwardings. We have to use it because of
   reasons and stuff :-(.
3. Use [.mailmap](http://www.kernel.org/pub/software/scm/git/docs/git-shortlog.html)
   if users have inconsistant email addresses.
