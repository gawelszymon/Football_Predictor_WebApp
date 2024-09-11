predicted_results = []
real_results = []

def parse_result(result):
    parts = result.split(' : ')
    teams = parts[0].strip()
    score = parts[1].strip()   
    team1, score1 = teams.rsplit(' ', 1)
    team2, score2 = score.split(' ', 1)
    return team1, team2, score1, score2 

with open('predicted_results.txt', 'r') as file:
    predicted_results = [line.strip() for line in file.readlines()]
    
with open('real_results.txt', 'r') as file:
    real_results = [line.strip() for line in file.readlines()]
    
b = 0
    
for i in range(len(predicted_results)):
    if predicted_results[i] == real_results[i]:
        b += 1

correct_scores = 0
correct_results = 0
correct_results_but_incorrect_scores = 0
incorrect_results = 0

for i in range(len(predicted_results)):
    team1_pred, team2_pred, score1_pred, score2_pred = parse_result(predicted_results[i])
    team1_real, team2_real, score1_real, score2_real = parse_result(real_results[i])
    
    if (score1_pred == score1_real and score2_pred == score2_real):
        correct_scores += 1
        
    if (score1_pred >= score2_pred and score1_real >= score2_real) or (score1_pred < score2_pred and score1_real < score2_real):
        correct_results += 1
        
    if ((score1_pred >= score2_pred and score1_real >= score2_real) or (score1_pred < score2_pred and score1_real < score2_real) and (score1_pred != score1_real and score2_pred != score2_real)):
        correct_results_but_incorrect_scores += 1
        
    if (score1_pred >= score2_pred and score1_real < score2_real) or (score1_pred <= score2_pred and score1_real > score2_real):
        incorrect_results += 1
        
        
print(b)
print(len(predicted_results))
print(correct_scores)
print(correct_results)
print(correct_results_but_incorrect_scores)
print(incorrect_results)

