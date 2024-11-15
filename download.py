#!/bin/env python3
"""Download subiquity bug information."""

import sys
from functools import cached_property

from launchpadlib.launchpad import Launchpad

lp = ""

bug_collection = {}


class Bug:

    def __init__(self, bug_task_resource, load_attachments=False):
        self.bug_task_resource = bug_task_resource
        self._attachments = {}
        if load_attachments:
            self.load_attachments()

    @cached_property
    def bug_resource(self):
        return self.bug_task_resource.bug

    @cached_property
    def number(self):
        return self.bug_resource.id

    @cached_property
    def tags(self):
        return self.bug_resource.tags.split()

    @cached_property
    def description(self):
        return self.bug_resource.description

    @cached_property
    def title(self):
        return self.bug_resource.title

    @property
    def attachments(self):
        return self._attachments

    def load_attachments(self, force=False):
        if self._attachments != {} and not force:
            return

        for at in self.bug_resource.attachments:

            title = at.title
            if not title.endswith(".txt"):
                continue

            buffer = at.data.open()
            data = b"".join([line for line in buffer])
            buffer.close()

            try:
                self._attachments[title] = data.decode("utf-8")
            except UnicodeDecodeError as err:
                print(f"error decoding lp: #{self.number} {title!r}: {err}")


def main() -> int:
    global lp, bug_collection

    print("Logging into launchpad...")
    lp = Launchpad.login_with(
        "subiquity-bugs-collection",
        "production",
        version="devel",
    )
    print(f"Logged in with user: {lp.me.name!r}")
    print("Collecting bug information...")
    bugs = lp.projects["subiquity"].searchTasks()
    print(f"Found {len(bugs)} bugs.")
    print("Organizing bugs...")
    bug_collection = [Bug(r) for r in bugs]

    return 0


if __name__ == "__main__":
    sys.exit(main())
