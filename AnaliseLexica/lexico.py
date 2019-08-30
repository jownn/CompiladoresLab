import json

# separo em grupos e marco com um array como inicia o grupo e como ele termina
grupos = {
    'comentario': {'inicial' : ['--'], 'final' : ['\n']},
    'identificador': {'inicial' : ['lower'], 'final' : ['not lower && not upper']},
    'texto': {'inicial' : ["'"], 'final' : ["'"]},
    'numero': {'inicial' : ['number'], 'final' : ['not number']},
    'logico': {'inicial' : ['upper'], 'final' : ['not lower && not upper']},
    'atribuicao': {'inicial' : ['::'], 'final' : ['not :']},
    'dois-pontos': {'inicial' : [':'], 'final' : ['inicial']},
    'virgula': {'inicial' : [','], 'final' : ['inicial']},
    'quebra-linha': {'inicial' : ['\n'], 'final' : ['inicial']},
    'abre-parenteses': {'inicial' : ['('], 'final' : ['inicial']},
    'fecha-parenteses': {'inicial' : [')'], 'final' : ['inicial']},
    'abre-chaves': {'inicial' : ['{'], 'final' : ['inicial']},
    'fecha-chaves': {'inicial' : ['}'], 'final' : ['inicial']},
    'operador-igual': {'inicial' : ['='], 'final' : ['inicial']},
    'operador-diferente': {'inicial' : ['!'], 'final' : ['=']},
    'operador-menor': {'inicial' : ['<'], 'final' : ['inicial']},
    'operador-maior': {'inicial' : ['>'], 'final' : ['inicial']},
    'operador-mais': {'inicial' : ['+'], 'final' : ['inicial']},
    'operador-menos': {'inicial' : ['-'], 'final' : ['inicial']},
    'reservado': {'inicial' : [''], 'final' : ['']},
    'desconhecido': {'inicial' : [''], 'final' : ['']},
}
#guardo todas as palavras reservadas para verificacao
reservadas = {
    'Funcao',
    'Logico',
    'Logica',
    'Texto',
    'Numero',
    'se',
    'se nao',
    'se nao se',
    'enquanto',
    'retorna'
}
#crio as variaveis que serao usadas nas funcoes
guardando = False
tokens = []
erros = []
linhaGrupo = 1
indiceGrupo = 0
lexema = ''
adicionar = True

def analisadorLexico(programa):
    # chamo as variaveis globais e inicio o contador das linhas e indices
    global lexema
    global adicionar
    linha = 1
    indice = 0
    global guardando
    global linhaGrupo
    global indiceGrupo
    #na primeira vez do for nao faco nada o que torna o ultimo caracter inutil por isso adiciono um espaco
    programa += " "
    #ando em cada caracter do programa para verificar, sendo que a primeira vez nao faco nada
    for c in programa:
        adicionar = True
        
        # caso nao saiba o grupo e o lexema nao seja vazio verifico em qual grupo se encaixa o lexema
        if not guardando and lexema:
            verificaLexema()

        # caso ja saiba o grupo, verifico se o caracter que estou olhando eh final do meu grupo para adicionar o lexema 
        if guardando:
            verificaFim(c)

        #caso o lexema seja vazio (que pode ocorrer após eu adicionar o lexema no metodo anterior) eu anoto a linha e indice atual
        if lexema == '':
            linhaGrupo = linha
            indiceGrupo = indice

        #se o caracter que estou olhando for em branco e o lexema esta vazio, nao adiciono o espaco em branco no lexema
        if c == " " and lexema == '':
            adicionar = False
            
        # caso esteja liberado para adicionar o caracter no lexema ele adiciona
        if adicionar:
            lexema += c
        
        # incremento o indice e quando for quebra de linha somo a linha e zero o indice
        indice += 1
        if c == '\n':
            linha += 1
            indice = 0

    return {"tokens": tokens, "erros": erros}


# funcao que verifica em qual grupo esta o lexema
def verificaLexema():
    # pego as variaveis globais
    global guardando
    global lexema
    global erros
    # ando em cada um dos grupos tentando identificar em qual o lexema faz parte utilizando o "inicial" que salvei em cada variavel
    for grupo in grupos:
        for inicio in grupos[grupo]['inicial']:
            if comparar(lexema,inicio):
                guardando = grupo
    # caso eu verifique e ele nao se encaixe em nenhum tipo ele gera o erro e marca ele no grupo de desconhecido
    if not guardando:
        errorTokens()
        guardando = 'desconhecido'


#Verifico se chegou no fim do lexema pelo grupo guardado
def verificaFim(c):
    # pego as variaveis globais
    global guardando
    global lexema
    global adicionar
    # busco todos os possiveis finais do grupo
    for fim in grupos[guardando]['final']:
        # comeco iniciando a variavel para ele comparar no final
        compara = True
        # ser for o grupo desconhecido, adiciono o token e nao comparo mais o texto
        if guardando == 'desconhecido':
            adicionarTokens()
            compara = False
        # caso o lexema seja : e o caracter que esta vindo seja tambem : e estou guardando ja o grupo dois-pontos, entao troco de dois-pontos para atribuicao e nao comparo mais
        elif lexema == ':' and c == ':' and guardando == 'dois-pontos':
            guardando = 'atribuicao'
            compara = False
        # caso o lexema seja - e o caracter que esta vindo seja tambem - e estou guardando ja o grupo operador-menos, entao troco de operador-menos para comentario e nao comparo mais        
        elif lexema == '-' and c == '-' and guardando == 'operador-menos':
            guardando = 'comentario'
            compara = False
        # caso o caracter que esta vindo seja ' e estou guardando um texto faco um contador para saber se faz parte do texto ou nao
        elif c == "'" and guardando == 'texto':
            #inicio o contador
            contar = 0
            #ando pelo lexema invertido
            for ch in lexema[::-1]:
                #verifico se eh diferente de # caso seja acabo a contagem
                if ch != '#':
                    break
                # caso nao seja incremento o contador
                else:
                    contar += 1
            # vejo se a contagem deu impar, caso tenha dado impar sei que o ' faz parte do texto e nao compara mais 
            if contar%2 != 0:
                compara = False
            # caso tenha dado par adiciono no lexema, nao deixo adicionar na proxima vez e deixo comparar
            else:
                lexema += c
                adicionar = False
        # verifico se o lexema eh 'se' e esta vindo um espaco em branco caso seja nao comparo mais
        elif lexema == 'se' and c == ' ':
            compara = False
        # verifico se o lexema eh 'se ' e nao esta vindo um 'n' caso seja verdade retiro o espaco do final
        elif lexema == 'se ' and c != 'n':
            compara = False
        # verifico se o lexema eh 'se nao' e esta vindo um espaco em branco caso seja nao comparo mais
        elif lexema == 'se nao' and c == ' ':
            compara = False
        # verifico se o lexema eh 'se nao ' e nao esta vindo um 's' caso seja verdade retiro o espaco do final
        elif lexema == 'se nao ' and c != 's':
            lexema = lexema[:-1]
        # verifico se o lexema eh '!' e se o que esta vindo eh um '=' caso seja adiciono no lexema, nao deixo adicionar na proxima vez e deixo comparar
        elif lexema == '!' and c == '=':
            lexema += c
            adicionar = False
        #aqui comparo se o caracter que esta vindo, bate com o final do grupo
        if compara:
            if comparar(c,fim):
                #caso seja final verifico se faz parte das palavras reservadas, caso seja mudo o grupo para reservado
                if lexema in reservadas:
                    guardando = 'reservado' 
                #adiciono o token
                adicionarTokens()

    return False


# aqui comparo o inicial ou o fim com o caracter que esta vindo
def comparar(c, comp):
    if comp == 'lower':
        return c.islower()
    elif comp == 'upper':
        return c.isupper()
    elif comp == 'not lower':      
        return not c.islower()
    elif comp == 'not upper':      
        return not c.isupper()
    elif comp == 'not lower && not upper':
        return not c.isupper() and not c.islower()
    elif comp == 'number':      
        return c.isnumeric()
    elif comp == 'not number':      
        return not c.isnumeric()
    elif comp == 'not :':
        return c != '::'
    elif comp == 'inicial':
            for grupo in grupos:
                for inicio in grupos[grupo]['inicial']:
                    return c != inicio
    else:
        return c == comp

#aqui adiciono o token
def adicionarTokens():
    global lexema
    global guardando
    tokens.append({
        "grupo": guardando, "texto": lexema,
        "local": {"linha": linhaGrupo, "indice": indiceGrupo}
    })
    guardando = False
    lexema = ''

#aqui adiciono os erros
def errorTokens():
    global lexema
    global guardando
    erros.append({
        "texto": "simbolo, " + lexema + ", desconhecido",
        "local": {"linha": linhaGrupo, "indice": indiceGrupo}
    })
    guardando = False

# ALERTA: Nao modificar o codigo fonte apos esse aviso

def testaAnalisadorLexico(programa, teste):
  # Caso o resultado nao seja igual ao teste
  # ambos sao mostrados e a execucao termina  
  resultado = json.dumps(analisadorLexico(programa), indent=2)
  teste = json.dumps(teste, indent=2)
  if resultado != teste:
    # Mostra o teste e o resultado lado a lado  
    resultadoLinhas = resultado.split('\n')
    testeLinhas = teste.split('\n')
    if len(resultadoLinhas) > len(testeLinhas):
      testeLinhas.extend(
        [' '] * (len(resultadoLinhas)-len(testeLinhas))
      )
    elif len(resultadoLinhas) < len(testeLinhas):
      resultadoLinhas.extend(
        [' '] * (len(testeLinhas)-len(resultadoLinhas))
      )
    linhasEmPares = enumerate(zip(testeLinhas, resultadoLinhas))
    maiorTextoNaLista = str(len(max(testeLinhas, key=len)))
    maiorIndice = str(len(str(len(testeLinhas))))
    titule = '{:<'+maiorIndice+'} + {:<'+maiorTextoNaLista+'} + {}'
    objeto = '{:<'+maiorIndice+'} | {:<'+maiorTextoNaLista+'} | {}'
    print(titule.format('', 'teste', 'resultado'))
    print(objeto.format('', '', ''))
    for indice, (esquerda, direita) in linhasEmPares:
      print(objeto.format(indice, esquerda, direita))
    # Termina a execucao
    print("\n): falha :(")
    quit()

# Programa que passdo para a funcao analisadorLexico
programa = """-- funcao inicial

inicio:Funcao(valor:Logica,item:Texto):Numero::{
}

tiposDeVariaveis:Funcao::{
  textoVar:Texto::'#'exemplo##'
  numeroVar:Numero::1234
  logicoVar:Logico::Sim
}

tiposDeFluxoDeControle:Funcao:Logico::{
  resultado:Logico::Nao

  se(1 = 2){
    resultado::Nao
  } se nao se('a' != 'a'){
    resultado::Nao
  } se nao @ {
    resultado::Sim
  }

  contador:Numero::0
  enquanto(contador < 10){
    contador::contador + 'a'
  }

  retorna resultado
}"""

# Resultado esperado da execucao da funcao analisadorLexico
# passando paea ela o programa anterior
teste = {
  "tokens":[
    # Comentario    
    {
      "grupo":"comentario", "texto": "-- funcao inicial", 
      "local":{"linha":1,"indice":0}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":1,"indice":17}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":2,"indice":0}
    },
    # Funcao inicio
    {
      "grupo":"identificador", "texto": "inicio", 
      "local":{"linha":3,"indice":0}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":3,"indice":6}
    },
    {
      "grupo":"reservado", "texto": "Funcao", 
      "local":{"linha":3,"indice":7}
    },
    {
      "grupo":"abre-parenteses", "texto": "(", 
      "local":{"linha":3,"indice":13}
    },
    {
      "grupo":"identificador", "texto": "valor", 
      "local":{"linha":3,"indice":14}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":3,"indice":19}
    },
    {
      "grupo":"reservado", "texto": "Logica", 
      "local":{"linha":3,"indice":20}
    },
    {
      "grupo":"virgula", "texto": ",", 
      "local":{"linha":3,"indice":26}
    },
    {
      "grupo":"identificador", "texto": "item", 
      "local":{"linha":3,"indice":27}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":3,"indice":31}
    },
    {
      "grupo":"reservado", "texto": "Texto", 
      "local":{"linha":3,"indice":32}
    },
    {
      "grupo":"fecha-parenteses", "texto": ")", 
      "local":{"linha":3,"indice":37}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":3,"indice":38}
    },
    {
      "grupo":"reservado", "texto": "Numero", 
      "local":{"linha":3,"indice":39}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":3,"indice":45}
    },
    {
      "grupo":"abre-chaves", "texto": "{", 
      "local":{"linha":3,"indice":47}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":3,"indice":48}
    },
    {
      "grupo":"fecha-chaves", "texto": "}", 
      "local":{"linha":4,"indice":0}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":4,"indice":1}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":5,"indice":0}
    },
    # Funcao tiposDeVariaveis
    {
      "grupo":"identificador", "texto": "tiposDeVariaveis", 
      "local":{"linha":6,"indice":0}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":6,"indice":16}
    },
    {
      "grupo":"reservado", "texto": "Funcao", 
      "local":{"linha":6,"indice":17}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":6,"indice":23}
    },
    {
      "grupo":"abre-chaves", "texto": "{", 
      "local":{"linha":6,"indice":25}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":6,"indice":26}
    },
    # textoVar:Texto::'#'exemplo##'
    {
      "grupo":"identificador", "texto": "textoVar", 
      "local":{"linha":7,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":7,"indice":10}
    },
    {
      "grupo":"reservado", "texto": "Texto", 
      "local":{"linha":7,"indice":11}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":7,"indice":16}
    },
    {
      "grupo":"texto", "texto": "'#'exemplo##'", 
      "local":{"linha":7,"indice":18}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":7,"indice":31}
    },
    # numeroVar:Numero::1234
    {
      "grupo":"identificador", "texto": "numeroVar", 
      "local":{"linha":8,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":8,"indice":11}
    },
    {
      "grupo":"reservado", "texto": "Numero", 
      "local":{"linha":8,"indice":12}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":8,"indice":18}
    },
    {
      "grupo":"numero", "texto": "1234", 
      "local":{"linha":8,"indice":20}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":8,"indice":24}
    },
    # logicoVar:Logico::Sim
    {
      "grupo":"identificador", "texto": "logicoVar", 
      "local":{"linha":9,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":9,"indice":11}
    },
    {
      "grupo":"reservado", "texto": "Logico", 
      "local":{"linha":9,"indice":12}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":9,"indice":18}
    },
    {
      "grupo":"logico", "texto": "Sim", 
      "local":{"linha":9,"indice":20}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":9,"indice":23}
    },
    # Fecha Funcao
    {
      "grupo":"fecha-chaves", "texto": "}", 
      "local":{"linha":10,"indice":0}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":10,"indice":1}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":11,"indice":0}
    },
    # Funcao tiposDeFluxoDeControle
    {
      "grupo":"identificador", "texto": "tiposDeFluxoDeControle", 
      "local":{"linha":12,"indice":0}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":12,"indice":22}
    },
    {
      "grupo":"reservado", "texto": "Funcao", 
      "local":{"linha":12,"indice":23}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":12,"indice":29}
    },
    {
      "grupo":"reservado", "texto": "Logico", 
      "local":{"linha":12,"indice":30}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":12,"indice":36}
    },
    {
      "grupo":"abre-chaves", "texto": "{", 
      "local":{"linha":12,"indice":38}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":12,"indice":39}
    },
    # resultado:Logico::Nao
    {
      "grupo":"identificador", "texto": "resultado", 
      "local":{"linha":13,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":13,"indice":11}
    },
    {
      "grupo":"reservado", "texto": "Logico", 
      "local":{"linha":13,"indice":12}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":13,"indice":18}
    },
    {
      "grupo":"logico", "texto": "Nao", 
      "local":{"linha":13,"indice":20}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":13,"indice":23}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":14,"indice":0}
    },
    # se(1 = 2){
    {
      "grupo":"reservado", "texto": "se", 
      "local":{"linha":15,"indice":2}
    },
    {
      "grupo":"abre-parenteses", "texto": "(", 
      "local":{"linha":15,"indice":4}
    },
    {
      "grupo":"numero", "texto": "1", 
      "local":{"linha":15,"indice":5}
    },
    {
      "grupo":"operador-igual", "texto": "=", 
      "local":{"linha":15,"indice":7}
    },
    {
      "grupo":"numero", "texto": "2", 
      "local":{"linha":15,"indice":9}
    },
    {
      "grupo":"fecha-parenteses", "texto": ")", 
      "local":{"linha":15,"indice":10}
    },
    {
      "grupo":"abre-chaves", "texto": "{",
      "local":{"linha":15,"indice":11}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":15,"indice":12}
    },
    {
      "grupo":"identificador", "texto": "resultado", 
      "local":{"linha":16,"indice":4}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":16,"indice":13}
    },
    {
      "grupo":"logico", "texto": "Nao", 
      "local":{"linha":16,"indice":15}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":16,"indice":18}
    },
    # } se nao se('a' != 'a'){
    {
      "grupo":"fecha-chaves", "texto": "}",
      "local":{"linha":17,"indice":2}
    },
    {
      "grupo":"reservado", "texto": "se nao se", 
      "local":{"linha":17,"indice":4}
    },
    {
      "grupo":"abre-parenteses", "texto": "(", 
      "local":{"linha":17,"indice":13}
    },
    {
      "grupo":"texto", "texto": "'a'", 
      "local":{"linha":17,"indice":14}
    },
    {
      "grupo":"operador-diferente", "texto": "!=", 
      "local":{"linha":17,"indice":18}
    },
    {
      "grupo":"texto", "texto": "'a'", 
      "local":{"linha":17,"indice":21}
    },
    {
      "grupo":"fecha-parenteses", "texto": ")", 
      "local":{"linha":17,"indice":24}
    },
    {
      "grupo":"abre-chaves", "texto": "{",
      "local":{"linha":17,"indice":25}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":17,"indice":26}
    },
    {
      "grupo":"identificador", "texto": "resultado", 
      "local":{"linha":18,"indice":4}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":18,"indice":13}
    },
    {
      "grupo":"logico", "texto": "Nao", 
      "local":{"linha":18,"indice":15}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":18,"indice":18}
    },
    # } se nao @ {
    {
      "grupo":"fecha-chaves", "texto": "}",
      "local":{"linha":19,"indice":2}
    },
    {
      "grupo":"reservado", "texto": "se nao", 
      "local":{"linha":19,"indice":4}
    },
    {
      "grupo":"desconhecido", "texto": "@", 
      "local":{"linha":19,"indice":11}
    },
    {
      "grupo":"abre-chaves", "texto": "{",
      "local":{"linha":19,"indice":13}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":19,"indice":14}
    },
    {
      "grupo":"identificador", "texto": "resultado", 
      "local":{"linha":20,"indice":4}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":20,"indice":13}
    },
    {
      "grupo":"logico", "texto": "Sim", 
      "local":{"linha":20,"indice":15}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":20,"indice":18}
    },
    {
      "grupo":"fecha-chaves", "texto": "}", 
      "local":{"linha":21,"indice":2}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":21,"indice":3}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":22,"indice":0}
    },
    # contador:Numero::0
    {
      "grupo":"identificador", "texto": "contador", 
      "local":{"linha":23,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":23,"indice":10}
    },
    {
      "grupo":"reservado", "texto": "Numero", 
      "local":{"linha":23,"indice":11}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":23,"indice":17}
    },
    {
      "grupo":"numero", "texto": "0", 
      "local":{"linha":23,"indice":19}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":23,"indice":20}
    },
    # enquanto(contador < 10){
    {
      "grupo":"reservado", "texto": "enquanto", 
      "local":{"linha":24,"indice":2}
    },
    {
      "grupo":"abre-parenteses", "texto": "(", 
      "local":{"linha":24,"indice":10}
    },
    {
      "grupo":"identificador", "texto": "contador", 
      "local":{"linha":24,"indice":11}
    },
    {
      "grupo":"operador-menor", "texto": "<", 
      "local":{"linha":24,"indice":20}
    },
    {
      "grupo":"numero", "texto": "10", 
      "local":{"linha":24,"indice":22}
    },
    {
      "grupo":"fecha-parenteses", "texto": ")", 
      "local":{"linha":24,"indice":24}
    },
    {
      "grupo":"abre-chaves", "texto": "{",
      "local":{"linha":24,"indice":25}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":24,"indice":26}
    },
    {
      "grupo":"identificador", "texto": "contador", 
      "local":{"linha":25,"indice":4}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":25,"indice":12}
    },
    {
      "grupo":"identificador", "texto": "contador", 
      "local":{"linha":25,"indice":14}
    },
    {
      "grupo":"operador-mais", "texto": "+", 
      "local":{"linha":25,"indice":23}
    },
    {
      "grupo":"texto", "texto": "'a'", 
      "local":{"linha":25,"indice":25}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":25,"indice":28}
    },
    {
      "grupo":"fecha-chaves", "texto": "}", 
      "local":{"linha":26,"indice":2}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":26,"indice":3}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":27,"indice":0}
    },
    # Fecha Funcao
    {
      "grupo":"reservado", "texto": "retorna", 
      "local":{"linha":28,"indice":2}
    },    
    {
      "grupo":"identificador", "texto": "resultado", 
      "local":{"linha":28,"indice":10}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":28,"indice":19}
    },
    {
      "grupo":"fecha-chaves", "texto": "}", 
      "local":{"linha":29,"indice":0}
    }
  ], "erros":[
    {
      "texto":"simbolo, @, desconhecido",
      "local":{"linha":19,"indice":11}
    }
  ]
}

# Execucao do teste que valida a funcao analisadorLexico
testaAnalisadorLexico(programa, teste)

print("(: sucesso :)")