# vnv

vnv is a little shortcut for [virtualenv] that tries to stay out of your
way.
No more typing out `. /path/to/env/bin/activate`, now it's just
`vnv env`.

[virtualenv]: https://pypi.org/project/virtualenv/


## Quickstart

Install.
Then run:
```
vnv new my-venv
vnv my-venv
```
Bam. Now you're in a brand new virtualenv named "my-venv".
It's cached right now, so you can toggle it off and on with just:
```
vnv
```

But what about your old virtualenvs? If you keep them all in a folder or
two somewhere, just tell vnv where they are and you can activate them by
name anywhere on your system:
```
$ export VNV_PATH="/old-envs"
$ cd anywhere
$ vnv my-old-env
(my-old-env) $
```
If not, you can always activate them by path:
```
$ vnv /path/to/a-venv
(a-venv) $
```


## Features

### Simple env toggling & caching

Shown above, vnv offers a shortcut for activating and deactivating
virtualenv environments.
Activating an env caches it for the current shell session, stored in
`$VNV_CACHE`.

### The vnv search path

You control where vnv finds envs to activate.
The search path defaults to `~/.vnv/envs`, but is overridden by
`$VNV_PATH`.

```
$ vnv list
/home/gram/.vnv/envs:
  my-venv
$ export VNV_PATH="$HOME/Envs:$HOME/venv"
$ vnv list
/home/gram/Envs:
  django-site
  flask-site
/home/gram/venv:
  numpy
$ vnv which flask-site
/home/gram/Envs/flask-site
```

By default, `vnv new` creates envs in the first directory of the search
path.

### Activate by name, activate by path

When given a name like `my-venv`, vnv will only look for it on the vnv
search path.
To specify that "my-venv" is in the current directory, use the explicit
path `./my-venv` instead.

### Shortcut, not a wrapper

Everything vnv does is just a shortcut to the default virtualenv
behavior.
Everything you make with it will still work even if you ditch vnv.

There are fancier tools out there for managing virtualenvs.
Try [virtualenvwrapper] or [pew] for the wrapper experience.

[virtualenvwrapper]: https://pypi.org/project/virtualenvwrapper
[pew]: https://pypi.org/project/pew

### Other features

- Cross-platform and cross-shell
- Multiple search path directories
- Single 3-character command for everything
- Create envs with `$ vnv new`, forwarding additional args to virtualenv
- Manage envs with `$ vnv list`, `$ vnv which`, `$ vnv del`
- Shortcut names: `$ vnv m` can activate `my-venv`
- Supports `activate_this.py` with `import vnv; vnv.activate('my-venv')`


## Installation

Use pip:
```
pip install vnv
```

Make sure to install vnv on your base Python installation, *not* in a
virtual environment.
You'll need access to it inside *and* outside of envs.

vnv supports all 7 activators virtualenv supports, meaning it works with
bash/zsh/ksh, cmd.exe, csh, fish, PowerShell, xonsh, and the Python
interpreter itself.

If you use one of those that ends in "sh", you'll also need to load the
corresponding wrapper script in your startup file.
For example, bash requires the line `. vnv-startup` in `~/.bashrc`.
Instructions included.


## Some more ideas

If you want to have a default env, you could pre-set `$VNV_CACHE` to its
location when your shell starts.
Use your startup file (or the environment variables on Windows).

If you want to activate envs in the current directory by name, add `.`
to the vnv search path.

vnv search path folders don't have to only contain virtualenvs.
If you keep an env alongside other stuff in a project folder, it's fine
to add the whole project folder to `$VNV_PATH`.


## Credits

vnv is made by me, Gramkraxor.
It's in the public domain, so it's yours to tinker with.


[![xkcd #1319: Automation](https://imgs.xkcd.com/comics/automation.png "xkcd #1319: Automation")](https://xkcd.com/1319/)
