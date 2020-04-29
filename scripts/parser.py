import argparse

class parser(object):
    """
    Parser for handling the API commands.

    .. note::

        Parser is used as a placeholder for the GUI and will be replaced in a later stage if the project.
    """
    def __init__(self):
        """
        Initialization, builds the parser.

        """
        print('test')

    def construct(self):
        """
        Constructs the parser with several arguments for stdout.
        
        :return:
        """

        # dummy argparser
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('integers', metavar='N', type=int, nargs='+',
                            help='an integer for the accumulator')
        parser.add_argument('--sum', dest='accumulate', action='store_const',
                            const=sum, default=max,
                            help='sum the integers (default: find the max)')

        args = parser.parse_args()
        print(args.accumulate(args.integers))



if __name__ == "__main__":
    parser().construct()
    import doctest
    doctest.testmod()