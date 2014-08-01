import sys

from count_score import Score

if __name__ == '__main__':

    args = sys.argv[1:]
    score = Score()
    score.deserialize(args)
    score.calculate()
    score.full_write()
