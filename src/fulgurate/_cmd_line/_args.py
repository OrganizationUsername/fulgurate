import datetime
import dateutil.parser

def add_now(arg_parser):
    arg_parser.add_argument(
        '-n',
        '--now',
        dest='now',
        type=dateutil.parser.parse,
        default=datetime.datetime.now(),
        help="The time for the operation, if not the system clock time.",
    )
