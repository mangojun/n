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
    
    # 양방향 교환 패턴 감지
    # 열 i와 열 j 사이에 양방향 흐름이 있는지 확인
    
    # 누적 합 기반 흐름 계산
    cumsum_A = 0
    cumsum_B = 0
    flow = [0] * C  # flow[c] = 열 c와 c+1 사이를 지나는 순수 흐름
    
    for c in range(C):
        cumsum_A += A[c]
        cumsum_B += B[c]
        if c < C - 1:
            flow[c] = cumsum_A - cumsum_B
    
    # 양방향 교환 패턴 감지
    # 케이스: 열 i에서 모두 오른쪽으로, 열 j에서 모두 왼쪽으로 (i < j)
    exchanges = []  # (left_col, right_col, left_to_right_amt, right_to_left_amt)
    
    # 전송 계획
    transfer = [[0] * C for _ in range(C)]
    remaining_A = A[:]
    remaining_B = B[:]
    
    # 단순 케이스: 열 i와 열 j만 씨앗이 있고, 완전 교환이 가능한 경우
    
    non_zero_A = [c for c in range(C) if A[c] > 0]
    non_zero_B = [c for c in range(C) if B[c] > 0]
    
    # 양방향 교환 감지: 좌측과 우측이 서로 씨앗을 교환해야 하는 경우
    if len(non_zero_A) == 2 and len(non_zero_B) == 2:
        left_A = min(non_zero_A)
        right_A = max(non_zero_A)
        left_B = min(non_zero_B)
        right_B = max(non_zero_B)
        
        # 교환 패턴: A[left] → B[right], A[right] → B[left]
        if left_A == left_B and right_A == right_B:
            left_surplus = A[left_A] - B[left_A]  # 왼쪽에서 오른쪽으로 보내야 할 양
            right_deficit = B[right_A] - A[right_A]  # 오른쪽에서 부족한 양
            
            # 완전 교환 조건: 왼쪽에서 초과, 오른쪽에서 부족, 
            # 그리고 오른쪽 씨앗을 왼쪽 굴로 보낼 수 있음
            if left_surplus > 0 and right_deficit > 0 and A[right_A] > 0 and B[left_A] > 0:
                # A[right] → B[left]로 보내고, A[left] - B[left] + A[right] → B[right]로
                # 완전 교환: A[left] 전부 → 굴[right], A[right] 전부 → 굴[left]
                if A[right_A] <= B[left_A]:  # 오른쪽 씨앗이 왼쪽 굴 요구량 이하
                    exchanges.append((left_A, right_A, A[left_A], A[right_A]))
    
    # 완전 교환 패턴 처리
    if exchanges:
        left_col, right_col, left_to_right, right_to_left = exchanges[0]
        dist = right_col - left_col
        
        # 행 1에서 왼쪽→오른쪽 점프
        # 행 2에서 오른쪽→왼쪽 점프
        
        # 왼쪽 열 경로: D → nR → (R-1)D
        grid[0][left_col] = 'D'
        grid[1][left_col] = f'{dist}R'
        remaining_down = R - 1
        if remaining_down >= 2:
            grid[1][right_col] = f'{remaining_down}D'
        else:
            grid[1][right_col] = 'D'
        
        # 오른쪽 열 경로: 2D → nL → (R-2)D
        if R > 2:
            grid[0][right_col] = '2D'
            grid[2][right_col] = f'{dist}L'
            remaining_down = R - 2
            if remaining_down >= 2:
                grid[2][left_col] = f'{remaining_down}D'
            else:
                grid[2][left_col] = 'D'
        else:
            # R=2인 경우 다른 패턴 필요
            grid[0][right_col] = 'D'
            grid[1][right_col] = f'{dist}L'
            grid[1][left_col] = 'D'
        
        print(R)
        for r in range(R):
            print(' '.join(grid[r]))
        return
    
    # 기본 전송 계획 (단방향)
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
