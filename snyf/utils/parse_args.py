import sys

def parse_args(parsers):
    if len(sys.argv) == 1:
        print('Usage: synf/main.py <npm|maven|test> [target file]')
        exit()
    args = sys.argv[1:]
    mgmt = ''
    deps = {}

    if args[0] == 'test':
        subject = 'template' if len(args) == 1 else args[1]
        if subject == 'template':
            test_template()
        if subject == 'fetch':
            test_fetch()

        exit()

    res = {}

    # NOTE: Dear future me,
    # `parser` means what is called to read the deps declaration file
    # `mgmt` means the "actual" package manager, used in Snyk's url

    # Dep manager
    if args[0] == 'npm':
        parser = parsers['npm']
        mgmt = 'npm'
    elif args[0] == 'pnpm':
        parser = parsers['pnpm']
        mgmt = 'npm' # NOTE: yep
    elif args[0] == 'maven':
        parser = parsers['maven']
        mgmt = 'maven'
    elif args[0] == 'pip':
        parser = parsers['pip']
        mgmt = 'pip'
    else:
        raise Exception('Unsupported dependency manager...')

    tmp = args[1:]

    args = []
    flags = {}

    for arg in tmp:
        if arg.startswith('--'):
            if '=' in arg:
                arg = arg[2:]
                flag, value = arg.split('=')
            else:
                flag = arg[2:]
                value = True

            flags[flag] = value
        else:
            args.append(arg)

    return parser, mgmt, args, flags
