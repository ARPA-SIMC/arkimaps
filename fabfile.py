from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from fabric.api import local, run, cd, env, hosts
import git
import re
import os
from six.moves import shlex_quote

env.use_ssh_config = True


def cmd(*args):
    return " ".join(shlex_quote(a) for a in args)


def push(host):
    repo = git.Repo()
    remote = repo.remote(host)
    push_url = remote.config_reader.get("url")
    remote_dir = re.sub(r"^ssh://[^/]+", "", push_url)

    local(cmd("git", "push", host, "HEAD", "--force"))
    with cd(remote_dir):
        run(cmd("git", "reset", "--hard"))
        run(cmd("git", "clean", "-fx"))
        run(cmd("git", "checkout", "-B", "test_" + host, repo.head.commit.hexsha))
        run(cmd("git", "clean", "-fx"))


def run_test(host):
    push(host)

    repo = git.Repo()
    remote = repo.remote(host)
    push_url = remote.config_reader.get("url")
    remote_dir = re.sub(r"^ssh://[^/]+", "", push_url)
    arkimet_run_local = os.path.join(remote_dir, "..", "arkimet", "run-local")
    with cd(remote_dir):
        run(cmd("mkdir", "-p", "testdata"))
        run(cmd("tar", "-C", "testdata", "-axf", "../arkimaps-test-data.tar.xz"))
        run(cmd(arkimet_run_local, "nose2-3.6"))


@hosts("trentuno")
def push_trentuno():
    push("trentuno")


@hosts("trentadue")
def push_trentadue():
    push("trentadue")


@hosts("otto")
def test_otto():
    run_test("otto")


@hosts("trentuno")
def test_trentuno():
    run_test("trentuno")


@hosts("trentadue")
def test_trentadue():
    run_test("trentadue")


def test():
    test_otto()
