_builtin_commands = {'/exit', '/model', '/usage'}


def check_command(user_prompt) -> bool:
    return user_prompt in _builtin_commands
