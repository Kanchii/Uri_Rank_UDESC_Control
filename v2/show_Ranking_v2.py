import pandas as pd
from copy import deepcopy
import requests
from tabulate import tabulate
import time
from datetime import datetime, timedelta
import sys
import os.path
import asyncio
import concurrent.futures

'''
	Autor: Felipe Weiss
	Funcionalidade:
		Este programa pega o rank (até a sexta página) da UDESC no UriOnlineJudge do dia atual e compara com o 
		rank da UDESC no dia anterior e então mostra quais foram as mudanças ocorridas de um dia para o outro
'''

columns = ['Ranking', 'Usuário', 'Resolvido']
first, last = 1, 6
#urls = ['https://www.urionlinejudge.com.br/judge/pt/users/university/udesc?page=' + str(i) for i in range(first, last + 1)]

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
	print(tabulate(aux[columns], headers = "keys", tablefmt = 'fancy_grid', showindex = "never", numalign = "left"))

async def getRanking():	
	global columns, first, last

	with concurrent.futures.ThreadPoolExecutor(max_workers = (last - first) + 1) as executor:
		loop = asyncio.get_event_loop()
		futures = [
			loop.run_in_executor(
			executor, requests.get, 'https://www.urionlinejudge.com.br/judge/pt/users/university/udesc?page=' + str(i)
			)
			for i in range(first, last + 1)
		]
		ff = True
		rankAtual = []
		for r in await asyncio.gather(*futures):
			aux = pd.read_html(r.content)[-1]
			if(ff):
				ff = False
				rankAtual = aux
			else:
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
	loop = asyncio.get_event_loop()
	newT = loop.run_until_complete(getRanking()).reset_index().astype(str)
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