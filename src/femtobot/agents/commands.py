_builtin_commands = {
    '/exit': 'Exit Femtobot CLI.',
    '/model': 'Switch model.',
    '/usage': 'View model token usage.',
}


def check_command(user_prompt) -> bool:
    return user_prompt in _builtin_commands
