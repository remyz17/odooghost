This part of the project documentation focuses on a
**learning-oriented** approach. You'll learn how to
get started with the code in this project.

## Managing Odoo Stacks with CLI
### Check Stack Configuration
Command: check

Description: Use this command to validate the configuration of one or more Stacks. Both JSON and YAML formats are supported.

```bash
$ odooghost stack check /path/to/your/config1.json /path/to/your/config2.yaml
```

### Create a New Stack
Command: create

Description: Use this command to create one or more Stacks from given configuration files. Both JSON and YAML formats are supported.

```bash
$ odooghost stack create /path/to/your/config1.json /path/to/your/config2.yaml
```

### Delete a Stack
Command: drop

Description: Delete an existing Stack along with associated data.

```bash
$ odooghost stack drop my_odoo_stack
```

### Start a Stack
Command: start

Description: Start an existing Stack.

```bash
$ odooghost stack start my_odoo_stack
```

### Stop a Stack
Command: stop

Description: Stop an existing Stack. You can specify a timeout (in seconds) before sending a SIGKILL.

```bash
$ odooghost stack stop my_odoo_stack --timeout 15
```

### Restart a Stack
Command: restart

Description: Restart an existing Stack. Similar to the "stop" command, you can also set a timeout.

```bash
$ odooghost stack restart my_odoo_stack --timeout 15
```

### List Created Stacks
Command: ls

Description: Display a list of all created Stacks.

```bash
$ odooghost stack ls
```

### List Running Stacks
Command: ps

Description: Display a list of all currently running Stacks.

```bash
$ odooghost stack ps
```
