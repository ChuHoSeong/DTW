def print_matrix(matrix):
    '''
    행렬을 포맷에 맞게 출력하는 함수
    '''
    for row in matrix:
        print(" ".join(f"{x:6.1f}" for x in row))
    print()

def print_plot():
    # TODO : 구현3 : 발표자료용 그래프 그리기
    pass
    
