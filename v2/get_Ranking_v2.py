import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import asyncio
import concurrent.futures

'''
	Autor: Felipe Weiss
	Funcionalidade:
		Este programa pega o rank (até a sexta página) da UDESC no UriOnlineJudge e salva os dados em um arquivo csv
'''

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

def main():
	loop = asyncio.get_event_loop()
	newT = loop.run_until_complete(getRanking()).reset_index().astype(str)
	data = time.strftime("%Y%m%d")
	newT.to_csv('../Saves/rankUDESC_' + data + '.csv', index = False)

if __name__ == "__main__":
	main()