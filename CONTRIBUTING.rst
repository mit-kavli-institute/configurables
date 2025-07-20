.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/WilliamCFong/configurables/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Configurables could always use more documentation, whether as part of the
official Configurables docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/WilliamCFong/configurables/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `configurables` for local development.

1. Fork the `configurables` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/configurables.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv configurables
    $ cd configurables/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ flake8 configurables tests
    $ python setup.py test or pytest
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes using conventional commits and push your branch to GitHub::

    $ git add .
    $ git commit  # This will open your editor with the commit template
    $ git push origin name-of-your-bugfix-or-feature

   See the "Commit Message Guidelines" section below for proper commit formatting.

7. Submit a pull request through the GitHub website.

Commit Message Guidelines
-------------------------

This project uses `Conventional Commits <https://www.conventionalcommits.org/>`_ for automatic versioning and changelog generation. Please follow these guidelines:

**Format**::

    <type>(<scope>): <subject>
    
    <body>
    
    <footer>

**Types**:

* ``feat``: A new feature (triggers minor version bump)
* ``fix``: A bug fix (triggers patch version bump)
* ``docs``: Documentation only changes
* ``style``: Changes that don't affect code meaning (formatting, missing semi-colons, etc)
* ``refactor``: Code change that neither fixes a bug nor adds a feature
* ``perf``: Code change that improves performance
* ``test``: Adding missing tests or correcting existing tests
* ``build``: Changes that affect the build system or external dependencies
* ``ci``: Changes to CI configuration files and scripts
* ``chore``: Other changes that don't modify src or test files

**Scope** (optional): Anything specifying the place of the commit change (e.g., ``core``, ``parse``, ``configurable``)

**Subject**: Use imperative mood ("add" not "added"), don't capitalize first letter, no period at the end

**Breaking Changes**: Add ``BREAKING CHANGE:`` in the footer (triggers major version bump)

**Examples**::

    feat(parse): add support for yaml configuration files
    
    fix: handle missing configuration file gracefully
    
    docs: update installation instructions
    
    feat(api)!: change parameter order in configurable decorator
    
    BREAKING CHANGE: The order of parameters in @configurable has changed

To use the commit template locally::

    $ git config --local commit.template .gitmessage

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.9, 3.10, 3.11, 3.12, and 3.13. Check
   the GitHub Actions results and make sure that the tests pass for all 
   supported Python versions.
4. Follow the commit message guidelines above for all commits in your PR.

Tips
----

To run a subset of tests::

$ pytest tests.test_configurables


Deploying
---------

A reminder for the maintainers on how to deploy:

Deployment is now automated! When you merge a PR to the master branch:

1. The GitHub Actions workflow analyzes commit messages
2. Automatically determines the version bump (major/minor/patch)
3. Updates version files and creates a CHANGELOG.md
4. Creates a git tag and GitHub release
5. Optionally publishes to PyPI (if enabled)

To trigger a release manually, ensure your commits follow the conventional commit format:

* ``fix:`` commits trigger a patch release (1.0.0 → 1.0.1)
* ``feat:`` commits trigger a minor release (1.0.0 → 1.1.0)
* ``BREAKING CHANGE:`` triggers a major release (1.0.0 → 2.0.0)

The old manual process is no longer needed!
