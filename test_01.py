from fileinput import filename
from backtesting import Strategy, Backtest
from backtesting.lib import crossover
import talib
import yfinance as yf
import seaborn as sns
import warnings
import matplotlib.pyplot as plt
import os
import numpy as np

warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=UserWarning)

#DIVISAS
LISTA_STOCKS = ['EURUSD=X',
                'GBPUSD=X',
                'USDJPY=X',
                'USDCAD=X',
                'NZDUSD=X']

#CRIPTOMONEDAS
LISTA_STOCKS = ['BTC-EUR',
                'ETH-EUR',
                'USDT-EUR',
                'BNB-EUR',
                'SOL-EUR',
                'USDC-EUR',
                'ADA-EUR',
                'DOGE-EUR',
                'AVAX-EUR',
                'TRX-EUR',
                'LINK-EUR',
                'DOT-EUR',
                'MATIC-EUR',
                'LTC-EUR',
                'DAI-USD',
                'BCH-USD',
                'ATOM-USD',
                'UNI7083-USD']

#ACCIONES AMERICANAS
LISTA_STOCKS = ['GOOGL',
                'TSLA',
                'AMZN',
                'NVDA',
                'PFE',
                'AMD',
                'NIO',
                'AAPL',
                'MSFT',
                'META',
                'INTC',
                'PYPL',
                'NFLX',
                'CSCO']

#TODAS MEMOS LAS DIVISAS
LISTA_STOCKS = ['BTC-EUR',
                'ETH-EUR',
                'USDT-EUR',
                'BNB-EUR',
                'SOL-EUR',
                'USDC-EUR',
                'ADA-EUR',
                'DOGE-EUR',
                'AVAX-EUR',
                'TRX-EUR',
                'LINK-EUR',
                'DOT-EUR',
                'MATIC-EUR',
                'LTC-EUR',
                'DAI-USD',
                'BCH-USD',
                'ATOM-USD',
                'UNI7083-USD',
                'GOOGL',
                'TSLA',
                'AMZN',
                'NVDA',
                'PFE',
                'AMD',
                'NIO',
                'AAPL',
                'MSFT',
                'META',
                'INTC',
                'PYPL',
                'NFLX',
                'CSCO']


"""LISTA_STOCKS = ['TEF',
                'SAN',
                'ENG']"""



resultado_return = []
resultado_exposure = []
resultado_win_rate = []
resultado_trades = []

class Oscillator(Strategy):
    upper_bound = 70
    lower_bound = 30

    def init(self):
      self.rsi = self.I(talib.RSI,self.data.Close, 14)#Entrega el triger para abrir posicion
      self.sar = self.I(talib.SAR,self.data.High, self.data.Low,acceleration=0.02, maximum=0.2)#Entrega el triger para cerrar posicion

    def next(self):
      price = self.data.Close[-1]

      if crossover(self.rsi,self.upper_bound) and not self.position.is_long:
        self.buy()
      elif self.position.is_long and self.data.Close < self.sar and self.position.pl > 0:
        self.position.close()

      elif crossover(self.lower_bound,self.rsi) and not self.position.is_short:
        pass#self.sell()  #LOS RESULTADOS SON MEJORES SI SOLO JUGAMOS EN LARGO
      elif self.position.is_short and self.data.Close > self.sar and self.position.pl < 0:
        self.position.close()

def borrar_archivos_en_carpeta(direccion_carpeta):
    try:
        # Obtener la lista de archivos en la carpeta
        archivos_en_carpeta = os.listdir(direccion_carpeta)
        # Iterar sobre la lista y borrar cada archivo
        for archivo in archivos_en_carpeta:
            ruta_archivo = os.path.join(direccion_carpeta, archivo)
            if os.path.isfile(ruta_archivo):
                os.remove(ruta_archivo)
                print(f'Archivo borrado: {archivo}')

        print(f'Todos los archivos en {direccion_carpeta} han sido borrados.')
    except Exception as e:
        print(f'Ocurrió un error: {e}')
      
def analiza_stock(stock_ticker,
                  print_stats=False,
                  optimize=False,
                  print_optimize=False):
    
    stock = yf.download(stock_ticker,start='2010-01-01',end='2024-01-01')#stock = yf.download(stock_ticker,start='2013-01-01',end='2023-01-01')
    #print(stock.tail())

    bt = Backtest(stock, Oscillator, cash=10_000, commission=.002)
    stats = bt.run()
    if print_stats:
      print("RESULTADO DE RUN")
      print(stats)
    print(stock_ticker)
    return_ann = stats['Return (Ann.) [%]']
    exposure = stats['Exposure Time [%]']
    win_rate = stats['Win Rate [%]']
    if np.isnan(win_rate):
      win_rate = 50 
    trades = stats['# Trades']
    print(f"Return (Ann.) [%] \t{return_ann}")
    print(f"Exposure Time [%] \t{exposure}")
    print(f"Win Rate [%] \t\t{win_rate}") 
    print(f"# Trades \t\t{trades}")

    bt.plot(filename=f"/home/ubuntu/backtest/html/{stock_ticker}.html")


    if optimize:
        stats, heatmap = bt.optimize(
                            upper_bound=range(50, 80, 1),
                            lower_bound=range(20, 40, 1),
                            maximize='Return (Ann.) [%]',
                            constraint=lambda param: param.lower_bound < param.upper_bound,
                            return_heatmap=True)
        if(print_optimize):
          print("RESULTADO DE OPTIMIZE")
          print(stats)
        print(stats._strategy)

        hm = heatmap.groupby(['lower_bound', 'upper_bound']).mean().unstack()
        sns.heatmap(hm[::-1], cmap='bwr')
        plt.savefig(f"/home/ubuntu/backtest/img/{stock_ticker}.png")
        plt.clf()
    
    return return_ann, exposure, win_rate, trades

borrar_archivos_en_carpeta("/home/ubuntu/backtest/html")
borrar_archivos_en_carpeta("/home/ubuntu/backtest/img")

for stock_ticker in LISTA_STOCKS:
    return_ann, exposure, win_rate, trades = analiza_stock(stock_ticker)
    resultado_return.append(return_ann)
    resultado_exposure.append(exposure)
    resultado_win_rate.append(win_rate)
    resultado_trades.append(trades)

print("")    
print("RESULTADOS:")
for i,elemento in enumerate(LISTA_STOCKS):
  print(f"{LISTA_STOCKS[i]}:\treturn={resultado_return[i]:.2f}%\texposure={resultado_exposure[i]:.2f}%\twin_rate={resultado_win_rate[i]:.2f}%\tN_trades={resultado_trades[i]:.2f}")

media_return = sum(resultado_return)/len(resultado_return)
media_exposure = sum(resultado_exposure)/len(resultado_exposure)
if len(resultado_win_rate)>0:
  media_win_rate = sum(resultado_win_rate)/len(resultado_win_rate)
else:
  media_win_rate = 0
media_trades = sum(resultado_trades)/len(resultado_trades)

print("")
print(f"PROMEDIO:\treturn={media_return:.2f}%\texposure={media_exposure:.2f}%\twin_rate={media_win_rate:.2f}%\tN_trades={media_trades:.2f}") 