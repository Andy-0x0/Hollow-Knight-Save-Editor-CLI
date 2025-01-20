import argparse
from pathlib import Path

from .utils import Interpreter, Handler, Menu, Modifier

def parseArguments():
    """
    Parse the CLI arguments using argparse.
    """
    # Initializae the parser
    parser = argparse.ArgumentParser(
        description="Hollow Knight Save Modifier CLI",
    )

    # Required for locating the save file --auto | --path
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-a', '--auto',
        type=int,
        help='Automatically search for the save file.'
    )
    group.add_argument(
        '-p', '--path',
        type=str,
        help='Spesify the path of the save file.'
    )

    # Optional modifications
    parser.add_argument(
        '-g', '--geo',
        type=int,
        default=None,
        help='Set the Geo amount.'
    )
    parser.add_argument(
        '--slots',
        type=int,
        default=None,
        help='Set the number of charm slots.'
    )
    parser.add_argument(
        '--whitehealth',
        type=int,
        default=None,
        help='Set the number of white health.'
    )
    parser.add_argument(
        '--bluehealth',
        type=int,
        default=None,
        help='Set the number blue healt.'
    )
    parser.add_argument(
        '--resurrect',
        action='store_true',
        help='Resurrect the non-battle ghosts.'
    )

    # Backup/restore
    parser.add_argument(
        '-r', '--reset',
        metavar='SUORCE_PATH',
        help='Path to the backup file to restore from.'
    )
    parser.add_argument(
        '-b', '--backup',
        metavar='BACKUP_PATH',
        type=str,
        default=None,
        help='Path of the backup file.'
    )

    return parser.parse_args()

def main():
    """
    Main entry point when you run via 'python cli.py' or from an installed console script.
    """
    args = parseArguments()
    interpreter = Interpreter()

    # Locate the original save file
    if args.auto is not None:
        if not 1 <= int(args.auto) <= 4:
            raise argparse.ArgumentTypeError(f"--auto must be an integer between 1 and 4 (got {int(args.auto)})")
        else:
            save = f'user{args.auto}.dat'
            handler = Handler(save)

        try:
            generator = handler.search(mode='default')
            save = next(generator)
            default_save = save
            found = False

            if save:
                print(f"Is {Menu.ask(default_save)} the save? (Y/n)")
                found = Menu.boolCheckbox()

            if not found:
                generator = handler.search(mode='auto')

                while True:
                    save = next(generator)
                    if save is None:
                        print(Menu.warn('> Iterated all potential files.'))
                        return
                    elif save == default_save:
                        continue

                    print(f"Is {Menu.ask(save)} the save? (Y/n)")
                    if Menu.boolCheckbox(): break
                    else: continue

        except FileNotFoundError:
            print(Menu.warn("> Such file does not exist."))
            return

    else:
        save = args.path
        handler = Handler(save)

        try:
            generator = handler.search(mode='spesify')
            save = next(generator)
            found = False

            if save:
                print(f"Is {Menu.ask(save)} the save? (Y/n)")
                found = Menu.boolCheckbox()

            if not found:
                print(Menu.warn('> Iterated all potential files.'))
                return

        except FileNotFoundError:
            print(Menu.warn("> Such file does not exist."))
            return

    # Decoding and load
    with open(save, 'rb') as f:
        content = f.read()
    ori = interpreter.decode(content)
    modifier = Modifier(ori)

    if args.reset:
        modifier.reset(args.reset)

    # Locate the backup save file
    save = Path(save)
    save_copy = Path(str(save.parent / save.stem) + '_copy.dat')
    while True:
        if Path.exists(save_copy):
            print(f"> File {Menu.ask(save_copy)} already exists, overwrite? (Y/n)")
            if Menu.boolCheckbox():
                break
            else:
                print(f"New backup path:")
                save_copy = Path(str(input("> ")).replace('\\', '/'))
                continue
        else:
            break

    try:
        handler.backup(save, save_copy)
    except FileNotFoundError:
        print(Menu.warn("> Such file does not exist."))
        return

    if args.resurrect:
        modifier.resurrectInnGhost()

    if args.geo is not None:
        modifier.modifyGeo(args.geo)

    if args.slots is not None:
        modifier.modifySlots(args.slots)

    if args.whitehealth is not None:
        modifier.modifyWhiteHealth(args.whitehealth)

    if args.bluehealth is not None:
        modifier.modifyBlueHealth(args.bluehealth)

    # Encoding and replace
    aft_sec = interpreter.encode(modifier.getData())
    with open(save, 'wb') as f:
        f.write(bytes(aft_sec))
    Menu.printReplace(path=save)

if __name__ == '__main__':
    main()
