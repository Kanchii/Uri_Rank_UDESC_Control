#! python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import asyncio
from tqdm import tqdm
import concurrent.futures
import sys

'''
	Autor: Felipe Weiss
	Funcionalidade:
		Este programa pega o rank (ate a sexta pagina) da UDESC no UriOnlineJudge e salva os dados em um arquivo csv
'''

first, last = 1, 16

def print_ast(n):
	print("*" * n)

def ajuste(x):
	return (x.replace('.', '') if not x.endswith('.0') else x.replace('.0', ''))

async def getRanking():
	global columns, first, last
	with concurrent.futures.ThreadPoolExecutor(max_workers = (last - first + 1)) as executor:
		loop = asyncio.get_event_loop()
		#print("Capturando os HTMLs das páginas do ranking...")
		#print_ast(80)
		futures = [
			loop.run_in_executor(
			executor, requests.get, 'https://www.urionlinejudge.com.br/judge/pt/users/university/udesc?page=' + str(i)
			)
			for i in range(first, last + 1)
		]
		ff = True
		rankAtual = []
		#print("Salvando as tabelas que foram capturadas...")
		#print_ast(80)
		for r in tqdm(await asyncio.gather(*futures)):
			aux = pd.read_html(r.content)[-1]
			if(ff):
				ff = False
				rankAtual = aux
			else:
				rankAtual = rankAtual.append(aux)
	#print_ast(80)
	#print("Ajustando a coluna \'Resolvido\' da tabela...")
	#print_ast(80)
	rankAtual['Resolvido'] = rankAtual['Resolvido'].astype(str).map(lambda x : ajuste(x))
	return rankAtual

def main():
	loop = asyncio.get_event_loop()
	#print("Iniciando coleta de dados do ranking atual da UDESC no Uri...")
	print_ast(80)
	newT = loop.run_until_complete(getRanking()).reset_index().astype(str)
	data = time.strftime("%Y%m%d")
	newT.to_csv('/home/weiss/Documentos/Github/Uri_Rank_Udesc_Control/Saves/rankUDESC_' + data + '.csv', index = False)

if __name__ == "__main__":
	#ss = time.time()
	main()
	#print("Tempo: {0:.4f}s".format(time.time() - ss))
	#print()
	#input("Press enter to exit")
