_builtin_commands = {
    '/exit': 'Exit Femtobot CLI.',
    '/model': 'Switch model.',
    '/usage': 'View model token usage.',
    '/clear': 'Clear short-term memory. (TODO)',
    '/reset': 'Same as /clear (TODO)',
    '/resume': 'Switch to a historical conversation. (TODO)',
    '/skills': 'Manage skills. (TODO)',
    '/mcp': 'Manage mcp. (TODO)',
}


def check_command(user_prompt) -> bool:
    return user_prompt in _builtin_commands
