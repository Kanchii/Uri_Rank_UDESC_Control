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
	global dates

	if(len(sys.argv) == 2 and sys.argv[1] == '-h'):
		print("Parametros:\n\t1 -> dado_requerido (Default = Exercicios resolvidos)\t2 -> periodo_de_abrangencia_partindo_do_dia_corrente\n\t3 -> nome_do_usuario")
	elif(len(sys.argv) < 3):
		print("Numero de parametros incorreto")
		return
	if(len(sys.argv) == 3):
		campo = "Resolvido"
		time = int(sys.argv[1])
		name = ' '.join(sys.argv[2:])
	else:
		campo = sys.argv[1]
		time = int(sys.argv[2])
		name = ' '.join(sys.argv[3:])
	att = time
	res = []
	while(True):
		filename = "../Saves/rankUDESC_" + getDate(att) + ".csv"
		if(os.path.exists(filename)):
			dates.append(fixDate(getDate(att)))
			temp = pd.read_csv(filename)
			pos = searchUser(name, temp)
			if(pos > -1):
				res.append(temp[campo][pos])
			else:
				res.append(None)
		att -= 1
		if(att == 0):
			dates.append(fixDate(getDate()))
			temp = getRanking(1, 6).reset_index()
			realName = getRealName(name, temp)
			pos = searchUser(name, temp)
			if(pos > -1):
				res.append(int(temp[campo][pos]))
			else:
				res.append(None)
			break
	fig, axes = plt.subplots(ncols=1, figsize=(8, 6))
	ax = axes
	ind = np.arange(len(dates))
	ax.plot(ind, res, 'r')
	ax.set_title(realName)
	ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
	fig.autofmt_xdate()
	plt.xlabel('Data')
	plt.ylabel('Exercicios resolvidos')
	plt.show()

if __name__ == "__main__":
	main()