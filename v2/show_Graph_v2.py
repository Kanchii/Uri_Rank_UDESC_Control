import pandas as pd
from copy import deepcopy
import requests
from tabulate import tabulate
import time
from datetime import datetime, timedelta
import sys
import os.path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import asyncio
import concurrent.futures

'''
	Autor: Felipe Weiss
	Funcionalidade:
		Este código tem a finalidade de recuperar os dados de um Usuário e então plotar os dados
		em função dos dias
'''

def searchUser(user, table):
	for idx, name in enumerate(table['Usuário']):
		if(user in name):
			return idx
	return -1

def getRealName(user, table):
	for idx, name in enumerate(table['Usuário']):
		if(user in name):
			return name
	return -1

def ajuste(x):
	return (x.replace('.', '') if not x.endswith('.0') else x.replace('.0', ''))

async def getRanking():
	global columns

	with concurrent.futures.ThreadPoolExecutor(max_workers = 20) as executor:
		loop = asyncio.get_event_loop()
		futures = [
			loop.run_in_executor(
			executor, requests.get, 'https://www.urionlinejudge.com.br/judge/pt/users/university/udesc?page=' + str(i)
			)
			for i in range(1, 7)
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

def getDate(num_days = 0):
	date = datetime.now() - timedelta(days=num_days)	
	return date.strftime('%Y%m%d')

def fixDate(date):
	year = date[0:4]
	month = date[4:6]
	day = date[6:]
	res = day + "/" + month + "/" + year
	return res

dates = []

def format_date(x, pos = None):
	global dates
	ind = np.clip(int(x + 0.5), 0, len(dates) - 1)
	return dates[ind]

def main():
	#Global variables
	global dates

	args = sys.argv
	qtd = 10
	campo = 'Resolvido'
	if('-h' in args):
		print("Argumentos aceitos:\n-d: Quantidade de dias a ser considerado a partir do dia atual (Default = 10)\n\
			                        -c: Nome dos usuarios que se quer ver os dados (Se for + que 1 usuario, separar por \'+\'")
		return
	if('-d' in args):
		qtd = int(args[args.index('-d') + 1])
	all_users = args[args.index('-c') + 1:]
	if('-d' in all_users):
		all_users = all_users[:(all_users.index('-d'))]
	all_users = ' '.join(all_users).replace(' +', '+').replace('+ ', '+').split('+')
	att = qtd
	usu_dates = []
	real_names = []
	first = 1
	while(att > 0):
		filename = "../Saves/rankUDESC_" + getDate(att) + ".csv"
		if(os.path.exists(filename)):
			dates.append(fixDate(getDate(att)))
			temp = pd.read_csv(filename)
			for idx, u in enumerate(all_users):
				pos = searchUser(u, temp)
				realName = getRealName(u, temp)
				if(pos > -1):
					if(first):
						usu_dates.append([temp[campo][pos]])
						real_names.append(realName)
					else:
						usu_dates[idx].append(temp[campo][pos])
						real_names[idx] = realName
				else:
					if(first):
						usu_dates.append([None])
						real_names.append('.')
					else:
						usu_dates[idx].append(None)
			if(first):
				first = 0
		att -= 1
		if(att == 0):
			dates.append(fixDate(getDate()))
			loop = asyncio.get_event_loop()
			temp = loop.run_until_complete(getRanking()).reset_index().astype(str)
			for idx, u in enumerate(all_users):
				pos = searchUser(u, temp)
				realName = getRealName(u, temp)
				if(pos > -1):
					if(first):
						usu_dates.append([int(temp[campo][pos])])
						real_names.append(realName)
					else:
						usu_dates[idx].append(int(temp[campo][pos]))
						real_names[idx] = realName
				else:
					if(first):
						usu_dates.append([None])
						real_names.append('.')
					else:
						usu_dates[idx].append(None)
	fig, axes = plt.subplots(ncols=1, figsize=(12, 12))
	ax = axes
	ind = np.arange(len(dates))
	for idx, u in enumerate(real_names):
		ax.plot(ind, usu_dates[idx], label = u)

	ax.legend(loc='best', ncol=1, fancybox = True, shadow = True)
	ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
	fig.autofmt_xdate()
	plt.xlabel('Data')
	plt.ylabel('Exercicios resolvidos')
	plt.show()

if __name__ == "__main__":
	main()