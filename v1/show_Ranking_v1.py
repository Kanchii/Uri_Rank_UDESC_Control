import pandas as pd
from copy import deepcopy
import requests
from tabulate import tabulate
import time
from datetime import datetime, timedelta
import sys
import os.path

'''
	Autor: Felipe Weiss
	Funcionalidade:
		Este programa pega o rank (até a sexta página) da UDESC no UriOnlineJudge do dia atual e compara com o 
		rank da UDESC no dia anterior e então mostra quais foram as mudanças ocorridas de um dia para o outro
'''

columns = ['Ranking', 'Usuário', 'Resolvido']
tabulate.WIDE_CHARS_MODE = True

def searchUser(user, table):
	for idx, name in enumerate(table['Usuário']):
		if(name == user):
			return idx
	return -1

def ajuste(x):
	return (x.replace('.', '') if not x.endswith('.0') else x.replace('.0', ''))

def getComp(newT, oldT, column, idx):
	posO = searchUser(newT.at[idx, 'Usuário'], oldT)
	if(column == 'New'):
		if(posO == -1):
			return 1
		return 0
	
	dataA = int(newT.at[idx, column])
	if(posO == -1):
		return 0
	dataB = int(oldT.at[posO, column])
	if(column == 'Ranking'):
		return -(dataA - dataB)
	return (dataA - dataB)

def printTable(newT, oldT):
	global columns
	if(False):
		print(newT[columns])
	else:
		aux = deepcopy(newT)
		for i in range(len(newT['Usuário'])):
			v1 = getComp(newT, oldT, 'Resolvido', i)
			v2 = getComp(newT, oldT, 'Ranking', i)
			v3 = getComp(newT, oldT, 'New', i)
			if(v1 != 0):
				aux.at[i, 'Resolvido'] = aux.at[i, 'Resolvido'] + ' (+' + str(v1) + ')'
			if(v2 != 0):
				aux.at[i, 'Ranking'] = aux.at[i, 'Ranking'] + ' (' + ('' if int(v2) < 0 else '+') + str(v2) + ')'
			if(v3 == 1):
				aux.at[i, 'Usuário'] = aux.at[i, 'Usuário'] + ' (NOVO)'	
	print(tabulate(aux[columns], headers = "keys", tablefmt = 'fancy_grid', numalign = "left"))

def getRanking(first, last):
	rankAtual = -1
	first = True
	for i in range(first, last + 1):
		url = 'https://www.urionlinejudge.com.br/judge/pt/users/university/udesc?page=' + str(i)
		html = requests.get(url).content
		if(first):
			rankAtual = pd.read_html(html)[-1]
			first = False
		else:
			aux = pd.read_html(html)[-1]
			rankAtual = rankAtual.append(aux)
	rankAtual['Resolvido'] = rankAtual['Resolvido'].astype(str).map(lambda x : ajuste(x))
	return rankAtual

def getDate(num_days):
	date = datetime.now() - timedelta(days=num_days)	
	return date.strftime('%Y%m%d')

def main():
	ss = time.time()
	qtd = 1
	if(len(sys.argv) > 1):
		qtd = int(sys.argv[1])
	newT = getRanking(1, 6).reset_index().astype(str)
	filename = '../Saves/rankUDESC_' + getDate(qtd) + '.csv'
	if(os.path.exists(filename)):
		oldT = pd.read_csv(filename).astype(str)
	else:
		while(qtd > 0 and not os.path.exists(filename)):
			qtd -= 1
			filename = '../Saves/rankUDESC_' + getDate(qtd) + '.csv'
		oldT = pd.read_csv(filename).astype(str)
	printTable(newT, oldT)
	print("Tempo: {0:.4f}s".format(time.time() - ss))

if __name__ == "__main__":
	main()