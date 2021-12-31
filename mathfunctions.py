import math

def solve_quadratic(a, b, c, round_down=True):
    '''Applies the quadratic formula to an equation and returns the answer.'''
    raw_ans = ((-b + math.sqrt(b**2 - 4*a*c)) / (2*a),
               (-b - math.sqrt(b**2 - 4*a*c)) / (2*a))
    ans = []
    for a in raw_ans:
        if a == abs(a):
            if round_down:
                ans.append(int(a))
            else:
                ans.append(a)
    return ans


def solve_stack(n):
    '''Arranges n amount of items into a perfect triangle with r items left over to place on one side.'''
    rows = int(solve_quadratic(1, 1, -2*n)[0])
    remainders = n - (rows/2+0.5)*rows
    return rows, remainders