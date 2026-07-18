import sys

def solve():
    data = sys.stdin.read().split()
    idx = 0
    C = int(data[idx]); idx += 1
    T = int(data[idx]); idx += 1
    M = int(data[idx]); idx += 1
    
    A = [int(data[idx + i]) for i in range(C)]
    idx += C
    B = [int(data[idx + i]) for i in range(C)]
    
    R = C
    grid = [['X'] * C for _ in range(R)]
    
    # 전송 계획
    transfer = [[0] * C for _ in range(C)]
    
    cumsum_A = 0
    cumsum_B = 0
    flow = [0] * C
    
    for c in range(C):
        cumsum_A += A[c]
        cumsum_B += B[c]
        if c < C - 1:
            flow[c] = cumsum_A - cumsum_B
    
    remaining_A = A[:]
    remaining_B = B[:]
    
    # 오른쪽 전송
    for c in range(C - 1):
        if flow[c] > 0:
            send = min(remaining_A[c], flow[c])
            target = c + 1
            while target < C and send > 0:
                need = remaining_B[target]
                xfer = min(send, need)
                if xfer > 0:
                    transfer[c][target] = xfer
                    remaining_A[c] -= xfer
                    remaining_B[target] -= xfer
                    send -= xfer
                target += 1
    
    # 왼쪽 전송
    for c in range(C - 1, 0, -1):
        if flow[c - 1] < 0:
            send = min(remaining_A[c], -flow[c - 1])
            target = c - 1
            while target >= 0 and send > 0:
                need = remaining_B[target]
                xfer = min(send, need)
                if xfer > 0:
                    transfer[c][target] = xfer
                    remaining_A[c] -= xfer
                    remaining_B[target] -= xfer
                    send -= xfer
                target -= 1
    
    # 같은 열 전송
    for c in range(C):
        xfer = min(remaining_A[c], remaining_B[c])
        transfer[c][c] = xfer
    
    # 격자 구성
    cell_dirs = [[set() for _ in range(C)] for _ in range(R)]
    
    # 각 열에서 필요한 전송 분석
    for from_col in range(C):
        has_down = transfer[from_col][from_col] > 0
        right_targets = [to for to in range(from_col + 1, C) if transfer[from_col][to] > 0]
        left_targets = [to for to in range(0, from_col) if transfer[from_col][to] > 0]
        
        has_right = len(right_targets) > 0
        has_left = len(left_targets) > 0
        
        num_dirs = sum([has_down, has_right, has_left])
        
        if num_dirs == 0:
            continue
        
        if num_dirs == 1:
            # 단일 방향: 최적화된 대각선 패턴
            if has_down:
                cell_dirs[0][from_col].add(('H', R))
            
            elif has_right:
                to_col = max(right_targets)
                # 대각선 패턴: 열 번호가 작을수록 더 깊이 점프
                lane_row = max(0, R - from_col - 2)
                
                if lane_row == 0:
                    # 첫 행에서 바로 오른쪽으로
                    cell_dirs[0][from_col].add('R')
                else:
                    # 햄스터로 lane_row까지 점프
                    if lane_row >= 2:
                        cell_dirs[0][from_col].add(('H', lane_row))
                    else:
                        cell_dirs[0][from_col].add('D')
                    
                    # lane_row에서 오른쪽으로
                    cell_dirs[lane_row][from_col].add('R')
                
                # 중간 열들과 목적 열 처리
                for step in range(1, to_col - from_col + 1):
                    c = from_col + step
                    r = lane_row + step - 1 if lane_row > 0 else 0
                    
                    if r >= R:
                        r = R - 1
                    
                    if c < to_col:
                        # 중간 열: 오른쪽으로 계속 이동
                        cell_dirs[r][c].add('R')
                        # 이 열이 목적지인지 확인
                        if c in right_targets:
                            cell_dirs[r][c].add('D')
                            # 아래로 가는 경로
                            if r + 1 < R:
                                remaining = R - r - 1
                                if remaining >= 2:
                                    cell_dirs[r + 1][c].add(('H', remaining))
                                else:
                                    cell_dirs[r + 1][c].add('D')
                    else:
                        # 최종 목적 열: 아래로
                        remaining = R - r
                        if remaining >= 2:
                            cell_dirs[r][c].add(('H', remaining))
                        elif remaining == 1:
                            cell_dirs[r][c].add('D')
            
            else:  # has_left
                to_col = min(left_targets)
                lane_row = max(0, R - (C - 1 - from_col) - 2)
                
                if lane_row == 0:
                    cell_dirs[0][from_col].add('L')
                else:
                    if lane_row >= 2:
                        cell_dirs[0][from_col].add(('H', lane_row))
                    else:
                        cell_dirs[0][from_col].add('D')
                    cell_dirs[lane_row][from_col].add('L')
                
                for step in range(1, from_col - to_col + 1):
                    c = from_col - step
                    r = lane_row + step - 1 if lane_row > 0 else 0
                    
                    if r >= R:
                        r = R - 1
                    
                    if c > to_col:
                        cell_dirs[r][c].add('L')
                        if c in left_targets:
                            cell_dirs[r][c].add('D')
                            if r + 1 < R:
                                remaining = R - r - 1
                                if remaining >= 2:
                                    cell_dirs[r + 1][c].add(('H', remaining))
                                else:
                                    cell_dirs[r + 1][c].add('D')
                    else:
                        remaining = R - r
                        if remaining >= 2:
                            cell_dirs[r][c].add(('H', remaining))
                        elif remaining == 1:
                            cell_dirs[r][c].add('D')
        
        else:
            # 여러 방향: 다람쥐로 분배
            if has_down:
                cell_dirs[0][from_col].add('D')
            if has_right:
                cell_dirs[0][from_col].add('R')
            if has_left:
                cell_dirs[0][from_col].add('L')
            
            # 아래 방향 처리
            if has_down and R > 1:
                remaining = R - 1
                if remaining >= 2:
                    cell_dirs[1][from_col].add(('H', remaining))
                else:
                    cell_dirs[1][from_col].add('D')
            
            # 오른쪽 방향 처리
            if has_right:
                to_col = max(right_targets)
                for c in range(from_col + 1, to_col + 1):
                    if c < to_col:
                        cell_dirs[0][c].add('R')
                        if c in right_targets:
                            cell_dirs[0][c].add('D')
                            if R > 1:
                                remaining = R - 1
                                if remaining >= 2:
                                    cell_dirs[1][c].add(('H', remaining))
                                else:
                                    cell_dirs[1][c].add('D')
                    else:
                        cell_dirs[0][c].add(('H', R))
            
            # 왼쪽 방향 처리
            if has_left:
                to_col = min(left_targets)
                for c in range(from_col - 1, to_col - 1, -1):
                    if c > to_col:
                        cell_dirs[0][c].add('L')
                        if c in left_targets:
                            cell_dirs[0][c].add('D')
                            if R > 1:
                                remaining = R - 1
                                if remaining >= 2:
                                    cell_dirs[1][c].add(('H', remaining))
                                else:
                                    cell_dirs[1][c].add('D')
                    else:
                        cell_dirs[0][c].add(('H', R))
    
    # 격자 문자열 변환
    for r in range(R):
        for c in range(C):
            dirs = cell_dirs[r][c]
            if not dirs:
                grid[r][c] = 'X'
                continue
            
            hamsters = [d for d in dirs if isinstance(d, tuple)]
            squirrel_dirs = [d for d in dirs if isinstance(d, str)]
            
            # 햄스터 거리 1 → 다람쥐
            for h in hamsters[:]:
                if h[1] == 1:
                    squirrel_dirs.append('D')
                    hamsters.remove(h)
            
            if squirrel_dirs:
                result = ''
                if 'L' in squirrel_dirs:
                    result += 'L'
                if 'D' in squirrel_dirs:
                    result += 'D'
                if 'R' in squirrel_dirs:
                    result += 'R'
                if 'U' in squirrel_dirs:
                    result += 'U'
                grid[r][c] = result if result else 'X'
            elif hamsters:
                _, dist = hamsters[0]
                grid[r][c] = f'{dist}D'
    
    print(R)
    for r in range(R):
        print(' '.join(grid[r]))

if __name__ == "__main__":
    solve()
