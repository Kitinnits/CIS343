import sys

args = sys.argv[1:]

print(f"{len(args)} arguments provided: {args}")

if len(args) < 1:
    try:
        print("Entering REPL mode. Press Ctrl+C to exit.")
        while True:
            user_input = input(">>> ")
            print(user_input)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if len(args) == 1:
    file_path = args[0]
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            print(content)
            print("Error: Scanner Not Implemented")
            sys.exit(0)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)

else:
    print("Error: Too many arguments provided. Correct usage:\nopen in repl mode: python language.py\nopen a file: python language.py <file_path>")
    sys.exit(1)
