# NSC_simulator
model simulator with probabilistic perturbation

사용 방법
config.txt를 수정하여 parameter를 설정한다. 
folder containing models mutation information 는 cell line mutation 정보를 저장하는 폴더명
folder containing network model 는 현재로서는 쓸모 없는 parameter
folder that will save the result 는 결과를 저장할 folder의 이름. main.py가 있는 폴더에 이 이름의 폴더가 새로 만들어진다. 빈칸일 경우 simulation 돌린 시간을 이름으로 하는 폴더를 생성한다.

folder about drug perturbation 는 적용되는 drug의 효과가 기록된 txt를 담아두는 폴더
file about node information 는 아직 적용되지 않는 parameter
file about logic information 도 아직 적용되지 않는 parameter

the number of processes for multiprocessing 는 multiprocessing에서 사용할 process의 수. process 한당 cell line 하나를 전담해서 계산
the number of iteration(trajectories for each cell lines) 는 각 cell line에 대해 연산을 반복하는 횟수. 각 연산의 결과를 평균해서 activation 측정
the time step of each trajectory 는 한 번의 연산에 대해 model의 transition이 일어나는 횟수를 의미
the number of states discarded in result calculation 는 state transition 중 activation 계산에 포함시키지 않을 초반부 state transition의 개수. 이것은 drug 처리 후 어느정도 cell state가 안정화 된 이후만을 고려하기 위해 적용된다.
how many drug perturbation probabilities will be calculated except 0 는 drug의 target node가 perturbation 되는 확률의 가짓수. 10일 경우 0,0.1,,,, 0.8,0.9,1 의 확률로 perturbation 될 때의 activation 값들이 측정된다. 클수록 더 세밀하게 볼 수 있음.
target nodes to observe the results 는 activation을 측정할 nodes 목록. 빈칸으로 놔두면 모든 nodes를 볼 수 있다.

그리고 update_function.py module을 구하여 main.py와 같은 폴더에 넣어준다.

그 후 콘솔창에 python3 main.py 를 입력하면 자동으로 실행된다.

input_nodes에 기록된 node는 input node로 반영된다. 이 경우 매 update step마다 node 값이 1과 0중 하나로 바뀐다.(50%의 확률)

같은 node가 drug_perturbation, input_nodes, model_mutation에 의해 동시에 영향을 받을 경우 셋 중 하나의 영향만을 받게 된다.
input_nodes에 해당 node가 있을 경우 input node로 최우선으로 적용되고, input_nodes에 없을 경우 model_mutation 영향이 더 우선적으로 적용된다.
