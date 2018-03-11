#! python3
# -*- coding: utf-8 -*-

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
from tqdm import tqdm

'''
	Autor: Felipe Weiss
	Funcionalidade:
		Este programa pega o rank (até a sexta página) da UDESC no UriOnlineJudge do dia atual e compara com o 
		rank da UDESC no dia anterior e então mostra quais foram as mudanças ocorridas de um dia para o outro
'''

columns = ['Ranking', 'Usuário', 'Resolvido']
first, last = 1, 16
#urls = ['https://www.urionlinejudge.com.br/judge/pt/users/university/udesc?page=' + str(i) for i in range(first, last + 1)]

vis = [False] * 2000

def print_ast(n):
	print("*" * n)

def searchUser(user, table):
	global vis
	for idx, name in enumerate(table['Usuário']):
		if(name == user and not vis[idx]):
			vis[idx] = True
			return idx
	return -1

def ajuste(x):
	return (x.replace('.', '') if not x.endswith('.0') else x.replace('.0', ''))

def getComp(newT, oldT, idx):
	posO = searchUser(newT.at[idx, 'Usuário'], oldT)
	retorno = [0, 0, 0]
	if(posO == -1):
		retorno[2] = 1
	else:
		retorno[2] = 0
	
	dataARe = int(newT.at[idx, "Resolvido"])
	dataARa = int(newT.at[idx, "Ranking"])
	if(posO == -1):
		return (retorno[0], retorno[1], retorno[2])
	dataBRe = int(oldT.at[posO, "Resolvido"])
	dataBRa = int(oldT.at[posO, "Ranking"])
	retorno[1] = -(dataARa - dataBRa)
	retorno[0] = (dataARe - dataBRe)
	return (retorno[0], retorno[1], retorno[2])
	'''
	if(column == 'Ranking'):
		return -(dataA - dataB)
	return (dataA - dataB)
	'''

def printTable(newT, oldT):
	global columns, vis
	if(False):
		print(newT[columns])
	else:
		aux = deepcopy(newT)
		vis = [False] * 2000
		for i in range(len(newT['Usuário'])):
			v1, v2, v3 = getComp(newT, oldT, i)
			if(v1 != 0):
				aux.at[i, 'Resolvido'] = aux.at[i, 'Resolvido'] + ' (+' + str(v1) + ')'
			if(v2 != 0):
				aux.at[i, 'Ranking'] = aux.at[i, 'Ranking'] + ' (' + ('' if int(v2) < 0 else '+') + str(v2) + ')'
			if(v3 == 1):
				aux.at[i, 'Usuário'] = aux.at[i, 'Usuário'] + ' (NOVO)'
	print(tabulate(aux[columns], headers = "keys", tablefmt = 'fancy_grid', showindex = "never", numalign = "left"))

async def getRanking():	
	global columns, first, last
	
	with concurrent.futures.ThreadPoolExecutor(max_workers = 10) as executor:
		loop = asyncio.get_event_loop()
		print("Capturando os HTMLs das páginas do ranking...")
		print_ast(80)
		futures = [
			loop.run_in_executor(
			executor, requests.get, 'https://www.urionlinejudge.com.br/judge/pt/users/university/udesc?page=' + str(i)
			)
			for i in range(first, last + 1)
		]
		ff = True
		rankAtual = []
		print("Salvando as tabelas que foram capturadas...")
		print_ast(80)
		for r in tqdm(await asyncio.gather(*futures)):
			aux = pd.read_html(r.content)[-1]
			if(ff):
				ff = False
				rankAtual = aux
			else:
				rankAtual = rankAtual.append(aux)
	print_ast(80)
	print("Ajustando a coluna \'Resolvido\' da tabela...")
	print_ast(80)
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
	print("Iniciando coleta de dados do ranking atual da UDESC no Uri...")
	print_ast(80)
	newT = loop.run_until_complete(getRanking()).reset_index().astype(str)
	filename = '../Saves/rankUDESC_' + getDate(qtd) + '.csv'
	print("Verificando se existe os dados salvos de " + str(qtd) + " dia atrás")
	print_ast(80)
	if(os.path.exists(filename)):
		oldT = pd.read_csv(filename).astype(str)
	else:
		print("Não existe uma arquivo salvo de " + str(qtd) + " dias atrás...")
		print("Buscando dados de menos que " + str(qtd) + " dias atrás...")
		print_ast(80) 
		while(qtd > 0 and not os.path.exists(filename)):
			qtd -= 1
			filename = '../Saves/rankUDESC_' + getDate(qtd) + '.csv'
		oldT = pd.read_csv(filename).astype(str)
	printTable(newT, oldT)
	print("\n")
	print("Tempo: {0:.4f}s".format(time.time() - ss))
	input("Press enter to exit")


if __name__ == "__main__":
	main()
