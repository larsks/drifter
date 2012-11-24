Drifter is a cloud provisioning tool inspired by [Cloud Envy][] (which
in turn was inspired by [Vagrant][]).  Drifter has the following
features that (at the time of this writing) were not available in
Cloud Envy:

- Supports multiple instances, each with its own image, flavor,
  security groups, and other metadata.
- Supports multiple security groups in your project.
- Uses [Ansible][] for provisioning rather than trying to implement
  its own provisioning solution.
- Processes configuration files with Jinja2 to help automate more
  complex configurations.

[cloud envy]: https://github.com/cloudenvy/cloudenvy
[vagrant]: http://vagrantup.com/
[ansible]: http://ansible.cc/

Synopsis
========

    usage: drifter [-h] [--user-config-file USER_CONFIG_FILE]
                   [--project-config-file PROJECT_CONFIG_FILE] [--verbose]
                   [--debug]
                   {ansible_hosts,api,down,hosts,provision,sgdown,sgup,status,up}
                   ...

    optional arguments:
      -h, --help            show this help message and exit
      --user-config-file USER_CONFIG_FILE, --config USER_CONFIG_FILE, -f USER_CONFIG_FILE
      --project-config-file PROJECT_CONFIG_FILE
      --verbose, -v
      --debug

Available commands
==================

      ansible_hosts       Generate output suitable for use as an Ansible
                          inventory.
      api                 Start an interactive Python shell with access to the
                          Drifter API.
      down                Shut down all instances.
      hosts               Output a list of hosts in /etc/hosts format.
      provision           Run ansible-playbook against playbook.yml
      sgdown              Delete all security groups.
      sgup                Create all security groups.
      status              Show status of all instances.
      up                  Start all instances.

License
=======

Drifter -- a cloud provisioning tool  
Copyright (C) 2012 Lars Kellogg-Stedman <lars@oddbit.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

