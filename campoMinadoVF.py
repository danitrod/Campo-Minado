import pygame
import sys
import random
import os
import platform

# por Daniel Rodrigues
#
# versão final: 30/11/2018
#
# fontes das imagens:
#
# http://www.onlygfx.com/6-starburst-explosion-comic-vector-png-transparent-svg/
# https://pt.wikipedia.org/wiki/Ficheiro:Orange_flag_waving.svg
#

pygame.init()

# definindo cores
cinza = (170,170,170)
branco = (220,220,220)
marrom = (112, 1, 1)
vermelho = (255,0,0)
laranja = (247, 131, 7)
amarelo = (255, 243, 15)
verde = (30, 150, 30)
verdeClaro = (144, 255, 168)
preto = (10, 10, 10)

# inicializando as configuracoes da tela.
size = [600,600]
screen = pygame.display.set_mode(size)
screen.fill((50,50,50))
pygame.display.set_caption("Campo Minado")
pygame.display.flip()
explosao = pygame.image.load(os.path.join('img', 'explosao.png'))
bandeira = pygame.image.load(os.path.join('img', 'flag.png'))

#
# criando quadrados para o jogo (a parte visual):
#

nq = 8 # numero de quadrados em cada linha e coluna (alteravel)
esp = 2 # espaco entre quadrados
margem = esp//2 # margem entre o inicio da tela e o primeiro quadrado
lq = round((size[0]-(esp*nq+margem))/nq) # lado do quadrado, preenchendo a tela e contando o espaco entre quadrados e a margem
param = [margem,margem,lq,lq] # tupla para entrar como parametro para fazer o quadrado
for i in range(nq):
    for j in range(nq):    
        pygame.draw.rect(screen,cinza,param)
        param[0] += lq + esp
        pygame.display.flip()
    param[1] += lq + esp
    param[0] = margem

# carregando fontes
fonte = pygame.font.SysFont('Times New Roman', lq)
fontePerdeu = pygame.font.SysFont('Times New Roman', size[0]//10)
fonteGanhou = pygame.font.SysFont('Tahoma', size[0]//8)
fonteAcabarBandeiras = pygame.font.SysFont('Times New Roman', size[0]//20)

# atualizando tamanho da imagem
explosao = pygame.transform.scale(explosao, (lq-esp, lq-esp))
bandeira = pygame.transform.scale(bandeira, (lq-esp, lq-esp)) 
    
#
# configurando o funcionamento do jogo (parte modelo):
#

nm = int(nq*nq*0.15) # numero de minas (alteravel)
flags = nm # numero de bandeiras
corretos = 0 # palpites corretos
flagados = {} # dicionario marcando os quadrados que estao com bandeira
abertos = [] # marcar os quadrados abertos para nao poder jogar bandeira neles

# criando a matriz de minas (o modelo para controle interno)
campo = [None]*nq
for i in range(nq):
    campo[i]=[False]*nq # nessa lista de listas (matriz), cada lista representara uma linha de quadrados e sera True apenas se houver mina nesse quadrado.
for i in range(nm):
    # gerando locais aleatorios para as minas
    linRand=random.randrange(0,nq)
    colRand=random.randrange(0,nq)
    while campo[linRand][colRand]:
        linRand=random.randrange(0,nq)
        colRand=random.randrange(0,nq)
    campo[linRand][colRand]=True

#        
# funcoes uteis (controle do jogo e display):
#

def buscarPosMouse():
    # busca em que quadrado o mouse clicou
    posMouse = pygame.mouse.get_pos()
    buscaX = lq + margem # coluna (a primeira vale lado do quadrado + margem)
    col = 0
    while buscaX < posMouse[0]:
        col += 1
        buscaX += lq + esp
    buscaY = lq + margem # linha
    lin = 0
    while buscaY < posMouse[1]:
        lin += 1
        buscaY += lq + esp
    return lin, col

def atualizarNumeros(lin, col, xq, yq, chamados):
    # funcao para atualizar o numero de bombas proximas ao quadrado, se o numero for zero procura o numero das casas adjacentes
    # parametros: linha e coluna do quadrado, posicao do quadrado na tela e
    # lista de posicoes de quadrados que ja foram chamados para evitar loop infinito

    cont = 0
    for i in range(-1,2):
        for j in range(-1,2):
            if lin+i >= 0 and col+j >= 0 and lin+i <= nq-1 and col+j <= nq-1:
                if campo[lin+i][col+j]:
                    cont += 1
    criarTextoNumero(cont, xq, yq, lq)
    abertos.append((lin, col))
    if cont == 0: # se o numero for 0, buscar os numeros dos quadrados adjacentes, nao chama um quadrado que ja foi chamado
        for i in range(-1,2):
            for j in range(-1,2):
                if lin+i >= 0 and col+j >= 0 and lin+i <= nq-1 and col+j <= nq-1:
                    if not((lin+i, col+j) in chamados) and not(campo[lin+i][col+j]):
                        chamados.append((lin+i, col+j))
                        atualizarNumeros(lin+i, col+j, xq + (j*(lq+esp)), yq + (i*(lq+esp)), chamados)
        
def criarTextoNumero(cont, xq, yq, lq):
    # apresentar o numero passado pelo primeiro argumento na tela, na posicao do quadrado
    pygame.draw.rect(screen,branco,(xq,yq,lq,lq))
    if cont == 1:
        cor = verde
    elif cont == 2:
        cor = amarelo
    elif cont == 3:
        cor = laranja
    elif cont == 4:
        cor = vermelho
    elif cont in range(5,8):
        cor = marrom
    elif cont == 8:
        cor = preto
    if cont != 0:
        text = fonte.render(str(cont), True, cor)
        pos=(xq+(lq//2)-((text.get_rect().width)//2),yq+(lq//2)-((text.get_rect().height)//2))
        screen.blit(text, pos)
    pygame.display.update()

def perdeu():
    for i in range(nq):
        for j in range(nq):
            if campo[i][j]:
                # mostra todas as bombas onde não há bandeiras
                if not((i, j) in flagados) or not(flagados[(i, j)]):
                    pygame.draw.rect(screen,cinza,((margem)+(lq*j)+(esp*j),(margem)+(lq*i)+(esp*i),lq,lq))
                    screen.blit(explosao,((margem)+(lq*j)+(esp*j),(margem)+(lq*i)+(esp*i)))
                    pygame.display.update()
                
    text = fontePerdeu.render('Você perdeu! :(', True, vermelho)
    # copiando o texto para a superfície
    screen.blit(text, (size[0]//2-(text.get_rect().width//2),size[1]//2-(text.get_rect().height//2)))
    end()

def ganhou():
    for i in range(nq):
        for j in range(nq):
            if not((i, j) in abertos) and not(campo[i][j]):
                atualizarNumeros(i, j, margem+(j*(lq+esp)), margem+(i*(lq+esp)), [])
    text = fonteGanhou.render('Você ganhou!!! :)', True, verdeClaro)
    # copiando o texto para a superfície
    screen.blit(text, (size[0]//2-(text.get_rect().width//2),size[1]//2-(text.get_rect().height//2)))
    end()

def acabarBandeiras():
    text = fonteAcabarBandeiras.render('Acabaram suas bandeiras! :(', True, vermelho)
    screen.blit(text, (size[0]//2-(text.get_rect().width//2),size[1]//2-(text.get_rect().height//2)))
    end()

def end():
    pygame.display.update()
    if platform.system() == 'Windows':
        exit()
        pygame.quit()
    else:    
        pygame.quit()
        exit()


# eventos do jogo
while True:   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # botao esquerdo apertado
            lin, col = buscarPosMouse() # busca a linha e coluna clicados
            if not((lin, col) in flagados) or flagados[(lin, col)] == False:     
                if not(campo[lin][col]):
                    xq = (margem)+(lq*col)+(esp*col)
                    yq = (margem)+(lq*lin)+(esp*lin)
                    atualizarNumeros(lin, col, xq, yq, [])
                else:
                    perdeu()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            # botao direito apertado
            lin, col = buscarPosMouse()
            if not((lin, col) in abertos): # apenas marca bandeira se o quadrado não estiver aberto
                if (lin, col) in flagados:
                    if flagados[(lin, col)]:
                        flags += 1
                        if campo[lin][col]:
                            corretos -= 1
                        pygame.draw.rect(screen,cinza,((margem)+(lq*col)+(esp*col),(margem)+(lq*lin)+(esp*lin),lq,lq))
                        pygame.display.update()
                        flagados[(lin, col)] = False
                    else:
                        flagados[(lin, col)] = True
                        screen.blit(bandeira,((margem)+(lq*col)+(esp*col),(margem)+(lq*lin)+(esp*lin)))
                        pygame.display.update()
                        if campo[lin][col]:
                            corretos += 1
                        flags -= 1
                else:
                    flagados[(lin, col)] = True
                    screen.blit(bandeira,((margem)+(lq*col)+(esp*col),(margem)+(lq*lin)+(esp*lin)))
                    pygame.display.update()
                    if campo[lin][col]:
                        corretos += 1
                    flags -= 1
                if corretos == nm:
                    ganhou()
                if flags == 0:
                    acabarBandeiras()
                    
                
            
