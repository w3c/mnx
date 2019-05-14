# Contributing to the MNX repository

Here's a quick guide to our development process for folks who'd like to
contribute.

## GitHub Pages

The main purpose of this repository is to host the MNX specification(s)
and related documents. We use GitHub Pages for this; the fully rendered
specs live at [https://w3c.github.io/mnx/](https://w3c.github.io/mnx/).

That GitHub Pages site uses the content in our repo's `gh-pages` branch.
But we do not commit directly to the `gh-pages` branch. Instead, we
commit to `master`, and each `master` commit gets automatically
processed and saved on `gh-pages`. Specifically, here's what happens:

1. Somebody commits to `master`.
2. An automated Travis CI job gets notified of the commit and runs the
   continuous integration job as described in
   [.travis.yml](https://github.com/w3c/mnx/blob/master/.travis.yml).
3. That Travis job, in turn, runs a program called bikeshed, which
   converts our spec's `.bs` files into fully rendered `.html` files.
4. Then, the Travis job runs
   [deploy.sh](https://github.com/w3c/mnx/blob/master/deploy.sh), which
   copies these rendered `.html` files into the `gh-pages` branch and
   makes an automated commit under @adrianholovaty's user account.

Effectively this means each commit on `master` has an automatically
generated corresponding commit on `gh-pages`.

Please note that the `gh-pages` branch won't be instantly updated. The
Travis CI job might take 5 or 10 minutes to run.
