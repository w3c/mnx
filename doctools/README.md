# MNX documentation generator

This code generates the MNX spec and assorted documentation.

The specification itself lives in two hand-edited JSON files in this
directory:

* **`mnx-metaspec.json`** — the type system (every object, attribute and
allowed value in MNX), plus metadata for the documentation website.

* **`mnx-examples.json`** — metadata about the example documents and the
MusicXML comparisons.

The `content` and `media` directory include various other files for the
docs website.

Together these are the source of truth. Everything in the top-level `docs/`
directory (including the JSON Schema, `docs/mnx-schema.json`) is
auto-generated from them, by a Django app that renders the documentation
and can write it out as static HTML.

To edit the docs, edit the JSON. See [METASPEC-FORMAT.md](METASPEC-FORMAT.md)
for a full description of the format.

## Initial setup

Note: All of these commands should be run from within the
same directory that contains this README file.

1. Install Python 3.7 or higher.

2. (Optional but recommended) Create a Python virtual environment.
Here's how to create one called `mnxdocs` in your home directory:

```
python3 -m venv ~/mnxdocs
```

3. Activate the virtual environment:

```
source ~/mnxdocs/bin/activate
```

4. Install the required Python modules:

```
pip install -r requirements.txt
```

5. Get a git checkout of the mnxdocgenerator tool somewhere
on your system:

```
git clone https://github.com/w3c-cg/mnxdocgenerator.git /path/to/local/mnxdocgenerator
```

6. Install that local version of mnxdocgenerator:

```
pip install -e /path/to/local/mnxdocgenerator
```

There's no database to set up.

## Running the site locally

Once that's all set up, you can run a local web server to view
the documentation:

1. Run the Django web server:

```
python manage.py runserver
```

2. Go to http://127.0.0.1:8000/ in your web browser.
You'll be able to browse the MNX documentation.

## Editing the documentation

Edit `mnx-metaspec.json`, `mnx-examples.json` or any of the files in
`content/` in your text editor, then reload the page in your browser.
The local web server reads the files on every request, so your change
should show up immediately; there's no need to restart the server.

After editing, check your work for errors via these two commands:

```
python manage.py validate_metaspec
python manage.py validate_json
```

`validate_metaspec` catches mistakes in the metaspec: misspelled slugs,
duplicate keys, missing example files and various semantic errors.

`validate_json` checks that every example document still validates against
the JSON Schema generated from the metaspec.

## Generating a static HTML version of the docs

To export a static version of the docs (as opposed to the dynamic one
you can browse via the local web server) do the following:

```
python manage.py makesite ../docs/
```

This will create static HTML files for each page of the
docs, using relative links appropriately. It also includes
the media files, such as CSS and example images.

Note that `makesite` only ever writes files; it doesn't delete them. If you
remove a page from `mnx-metaspec.json`, delete its directory under `docs/`
by hand.

The `../docs/` in this command lets you specify the
output location of the static site. For example, this
command will generate them at `/Users/mnx/Desktop`:

```
python manage.py makesite /Users/mnx/Desktop
```

The easiest way to view the static site is to find the
top-level `index.html` file in the directory you
specified in the `makesite` command, and open that
`index.html` file in your web browser.

A nicer way (avoiding the problem of web browsers
displaying directory indexes) is to use Python's built-in
web server, via this command:

```
python -m http.server --directory /path/to/docs/
```

This will make the docs available at `http://127.0.0.1:8000/`
on your local machine.

## Suggested workflow for doc contributions

If you'd like to make an addition or correction to the docs,
here's our suggested workflow:

1. Make sure your Git checkout is using the latest commit
from the `main` branch.

2. Run the local web server and make (and preview) your changes.

3. Run `validate_metaspec` and `validate_json`.

4. Create a pull request with your changed files.

At the moment, don't worry about regenerating the static HTML
in your pull request. This keeps the pull requests focused
on the core changes, as opposed to generated "spam." The MNX
maintainers can generate the HTML updates themselves for now.
(We might change this policy in the future, once we get a feel
for how this system works over time.)
