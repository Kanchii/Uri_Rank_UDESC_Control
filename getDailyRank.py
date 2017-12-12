import pandas as pd
import requests
import time
from datetime import datetime, timedelta

'''
	Autor: Felipe Weiss
	Funcionalidade:
		Este programa pega o rank (até a sexta página) da UDESC no UriOnlineJudge e salva os dados em um arquivo csv
'''

def ajuste(x):
	return (x.replace('.', '') if not x.endswith('.0') else x.replace('.0', ''))

def getRanking(first, last):
	df_list = -1
	first = True
	for i in range(first, last + 1):
		url = 'https://www.urionlinejudge.com.br/judge/pt/users/university/udesc?page=' + str(i)
		html = requests.get(url).content
		if(first):
			df_list = pd.read_html(html)[-1]
			first = False
		else:
			aux = pd.read_html(html)[-1]
			df_list = df_list.append(aux)
	df_list['Resolvido'] = df_list['Resolvido'].astype(str).map(lambda x : ajuste(x))
	return df_list

def main():
	newT = getRanking(1, 6).reset_index()
	data = time.strftime("%Y%m%d")
	newT.to_csv('/home/weiss/Documentos/Python/HTML_Scrapping/Saves/rankUDESC_' + data + '.csv', index = False)

if __name__ == "__main__":
	main()