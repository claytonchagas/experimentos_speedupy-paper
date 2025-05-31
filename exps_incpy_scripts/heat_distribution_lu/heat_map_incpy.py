# -*- coding: utf-8 -*-

import os
import time
import numpy as np
import matplotlib.pylab as plt
import matplotlib.cm as cm
# Removido: import seaborn as sns
# Removido: import imageio (pode dar problema no Python 2.6.3)

def draw(matrix):
    # Substituir sns.heatmap por matplotlib.pyplot.imshow
    plt.figure(figsize=(8, 6))
    plt.imshow(matrix, cmap='coolwarm', interpolation='nearest')
    plt.colorbar()
    
    if not os.path.exists("images/tmp"):
        os.makedirs("images/tmp")
    plt.savefig("images/tmp/img_" + str(time.time()) + ".png")
    plt.close()
    #plt.show()

def generateGif():
    directory = "images/tmp/"
    if not os.path.exists("images/gif"):
        os.makedirs("images/gif")
    
    # Versão simplificada sem imageio (que pode não funcionar no Python 2.6.3)
    print("Geracao de GIF desabilitada - imageio pode nao ser compativel com Python 2.6.3")
    print("Imagens salvas em: " + directory)
    
    # Se quiser tentar usar imageio mesmo assim, descomente as linhas abaixo:
    # try:
    #     import imageio
    #     with imageio.get_writer('images/gif/movie.gif', mode='I', duration=0.5) as writer:
    #         for filename in sorted(os.listdir(directory)):
    #             image = imageio.imread(directory + filename)
    #             writer.append_data(image)
    #     writer.close()
    #     clearFiles(directory)
    # except ImportError:
    #     print("imageio nao disponivel - imagens mantidas em " + directory)

def clearFiles(directory):
    if os.path.exists(directory):
        files = os.listdir(directory)
        for filename in files:
            os.remove(os.path.join(directory, filename))
