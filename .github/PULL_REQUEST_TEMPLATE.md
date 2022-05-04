<!--
Thank you for opening this pull request (PR)!
-->

## Checklist

Verify that your PR checks all the following items.

- [ ] The pull request (PR) has a clear and explanatory title.
- [ ] The description of this PR links to relevant [GitHub issues](https://github.com/compSPI/ioSPI/issues).
- [ ] Unit tests have been added in the [tests folder](https://github.com/compSPI/ioSPI/tree/master/tests):
  - [ ] in the `test_*.py files` corresponding the files modified by this PR,
  - [ ] for each function added by this PR.
- [ ] The PR passes test and lint workflows. (refer to comment below)
- [ ] The code of this PR is properly documented, with [docstrings following ioSPI conventions](https://github.com/compspi/compspi/blob/master/docs/contributing.rst#the-anatomy-of-a-docstring).
- [ ] The code of this PR follows international guidelines for coding style (refer to comment below).

If some items are not checked, mark your PR as draft (Look for "Still in progress? Convert to Draft" on your PR) . Only mark the PR as "Ready for review" if all the items above are checked.

If you do not know how to address some items, reach out to a maintainer by requesting reviewers.

If some items cannot be addressed, explain the reason in the Description of your PR, and mark the PR ready for review

<!-- Checking that the PR passes the test workflow, i.e. passes the tests added in the tests folder.
First, run the tests related to your changes. For example, if you changed something in ioSPI/particle_metadata.py:
$ pytest tests/test_particle_meta_data.py

and then run the tests of the whole codebase to check that your feature is not breaking any of them:
$ pytest tests/

This way, further modifications on the code base are guaranteed to be consistent with the desired behavior. Merging your PR should not break any existing test.
-->


<!-- Checking that the PR passes the lint
Install dependencies for developers
$ pip3 install -r dev-requirements.txt

Then run the following commands:
$ black . --check
$ isort --profile black --check .
$ flake8 ioSPI tests
-->

## Description

<!-- Include a description of your pull request. If relevant, feel free to use this space to talk about time and space complexity as well scalability of your code-->

## Issue

<!-- Tell us which issue does this PR fix . Why this feature implementation/fix is important in practice ?-->

## Additional context

<!-- Add any extra information -->
