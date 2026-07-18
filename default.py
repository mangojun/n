import sys
import inspect
import dataclasses
from dataclasses import dataclass

_slots_kw = {"slots": True} if "slots" in inspect.signature(dataclass).parameters else {}

@dataclass(frozen=True, **_slots_kw)
class Cell:
    """칸의 행과 열 번호"""

    r: int = 0
    c: int = 0

    def parse_target_cell(self, num_rows: int, num_cols: int, dir: str, step: int) -> "Cell":
        r, c = self.r, self.c
        if dir == "U":
            res = Cell(r - step, c)
        elif dir == "D":
            res = Cell(r + step, c)
        elif dir == "L":
            res = Cell(r, c - step)
        elif dir == "R":
            res = Cell(r, c + step)
        else:
            raise ValueError(f"Invalid direction: {dir}")
        assert 0 <= res.r <= num_rows and 0 <= res.c < num_cols, f"Invalid target cell {res}"
        return res


@dataclass(**_slots_kw)
class State:
    """각 칸의 상태"""

    # 현재 칸에 있는 씨앗의 수
    num_seed: int = 0
    # 씨앗을 보낼 좌표들
    cells: list[Cell] = dataclasses.field(default_factory=list)
    # 현재 칸이 과부하 상태인지 (씨앗 보내기 단계)
    is_overloaded: bool = False
    # 다음에 씨앗을 보낼 칸의 번호 (씨앗 보내기 단계)
    cursor: int = 0
    # 씨앗 보내기 단계에서 받은 씨앗들의 좌표
    received: list[Cell] = dataclasses.field(default_factory=list)

    @staticmethod
    def new(num_rows: int, num_cols: int, cell: Cell, input: str) -> "State":
        start_char = input[0]
        if input == "X":
            return State()
        elif start_char.isdigit():
            step = int(input[:-1])
            dir = input[-1]
            target_cell = cell.parse_target_cell(num_rows, num_cols, dir, step)
            return State(cells=[target_cell])
        else:
            cells = [cell.parse_target_cell(num_rows, num_cols, dir, 1) for dir in input]
            for i, c in enumerate(cells):
                for other in cells[:i]:
                    if c == other:
                        raise ValueError(f"Duplicate cell found in cells: {cells}")
            return State(cells=cells)


def simulate(a: list[int], t: int, grid: list[list[str]]) -> tuple[int, list[int]]:
    """(마지막으로 씨앗이 굴로 들어간 시간, 각 열에 떨어진 씨앗 수)를 계산함"""
    num_rows = len(grid)
    num_cols = len(a)
    assert num_rows > 0 and num_cols > 0
    assert all(len(row) == num_cols for row in grid)
    m = max(a)
    assert t > m

    # 코드에서 0-index를 사용하고, 꽃의 행을 무시함
    # field[0..num_rows-1]는 빈 칸(다람쥐/햄스터), field[num_rows]는 굴
    field: list[list[State]] = [[State() for _ in range(num_cols)] for _ in range(num_rows + 1)]
    for r in range(num_rows):
        for c in range(num_cols):
            field[r][c] = State.new(num_rows, num_cols, Cell(r, c), grid[r][c])

    # 굴에 떨어지는 씨앗의 수
    b = [0] * num_cols
    # 마지막으로 떨어진 시간
    t_last = 0
    for curT in range(1, t + 1):
        # 1. 씨앗 수확
        for i, ai in enumerate(a):
            if m - ai + 1 <= curT <= m:
                field[0][i].num_seed += 1

        # 2. 씨앗 보내기
        for r in range(num_rows):
            for c in range(num_cols):
                # min(씨앗의 개수, 보낼 칸의 개수)만큼 차례로 씨앗을 보냄
                for _ in range(min(field[r][c].num_seed, len(field[r][c].cells))):
                    target = field[r][c].cells[field[r][c].cursor]
                    field[target.r][target.c].received.append(Cell(r, c))

                    field[r][c].num_seed -= 1
                    field[r][c].cursor += 1
                    if field[r][c].cursor == len(field[r][c].cells):
                        field[r][c].cursor = 0

        # 과부하 판단
        for row in field:
            for cell in row:
                cell.is_overloaded = cell.num_seed > 0

        # 3. 씨앗 받기
        for r in range(num_rows + 1):
            for c in range(num_cols):
                # 받은 씨앗을 원래 칸으로 돌려보내기
                if field[r][c].is_overloaded:
                    for cell in list(field[r][c].received):
                        field[cell.r][cell.c].num_seed += 1
                else:
                    field[r][c].num_seed += len(field[r][c].received)
                field[r][c].received.clear()

        # 4. 씨앗 저장
        for c in range(num_cols):
            if field[num_rows][c].num_seed > 0:
                b[c] += 1
                field[num_rows][c].num_seed -= 1
                t_last = curT

    return t_last, b


@dataclass
class Cost:
    # 오차
    e: int = 0
    # 지연 점수: T * L
    tl: int = 0
    # 지연
    d: int = 0
    # 추가로 사용한 열 개수 (R-C)
    r_c: int = 0

    @staticmethod
    def new(t: int, m: int, b: list[int], b_prime: list[int], r: int, t_last: int) -> "Cost":
        """b는 요구치(목표), b_prime는 실제로 굴에 운반된 씨앗의 수, m은 max(A)."""
        e = sum(abs(bi - bpi) for bi, bpi in zip(b, b_prime))
        l = sum(b) - sum(b_prime)
        d = t if l > 0 else t_last - m
        r_c = r - len(b)
        tl = t * l
        return Cost(e=e, tl=tl, d=d, r_c=r_c)

    def cost(self) -> int:
        return 2**self.r_c + max(self.e, self.d) + self.tl


def main() -> None:
    c, t, m = map(int, input().split())
    a = list(map(int, input().split()))
    b = list(map(int, input().split()))
    assert len(a) == c and len(b) == c
    r = c + 3
    grid: list[list[str]] = []
    for i in range(r):
        row: list[str] = []
        for j in range(c):
            if (i + j) % 3 == 2 and i < r - 2:
                row.append("2D")
            elif i == r - 1:
                row.append("D")
            elif j == 0:
                row.append("DR")
            elif j == c - 1:
                row.append("DL")
            else:
                row.append("DRL")
        grid.append(row)

    print(r)
    for row in grid:
        print(' '.join(row))

    # 채점 환경을 확인해 채점 시스템이 아닌 경우 시뮬레이션을 통해 비용 출력
    if not (len(sys.argv) > 1 and sys.argv[1] == "NYPC"):
        t_last, b_prime = simulate(a, t, grid)
        cost = Cost.new(t, m, b, b_prime, r, t_last).cost()
        sys.stderr.write(f"Cost: {cost}\n")


if __name__ == "__main__":
    main()
