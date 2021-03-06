"""NOTAS DO QUE HAI QUE FACER E ACLARACIONS
1)Seguir cambiando o Controlar.py ata que solo quede o while true(casi)
2)Implementar threads?
"""




#ESTE CODIGO "LIMITA" OS SENSORES XA QUE SOLLO COLLEMOS 10 MOSTRAS DOS JSONS(todas as que da coa configuracion actual)
import constant
import time
import numpy as np
import matplotlib.pyplot as plt
import warnings
import math
from copy import copy
from sklearn.svm import LinearSVC
from warnings import simplefilter
from sklearn.svm import SVC
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectFromModel

"""import pandas as pd
import seaborn as sn
import plotly.plotly as py
from sklearn.manifold import t_sne
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import cython
"""



#Simple method to log in
def iniciosesion():
        resposta=input("Escriba o seu nome de Usuario")
        try:
            with open (constant.PATH+str(resposta)+".json","r") as file:
                print("Cargando o seu perfil...")
        except:
            print("Non existe ningun usuario con ese nome,xerando un perfil...")
            with open (constant.PATH+str(resposta)+".json","w") as file:
                 file.write("#Benvido "+str(resposta)+",os seus datos non estan ordeados porque realmente non deberia entrar no .json\n")
        return resposta


#Prepare all the arquives we will need.Thanks to this method we will be able to use 'a' all time
def iniciar(clf_database):
    i=0
    while i < len(constant.GOLPES):
        if i is 0:
            clf_database[i]=[abreviatura(constant.GOLPES[i]),'NULL','NULL']
        else:
            clf_database.append([abreviatura(constant.GOLPES[i]),'NULL','NULL'])
        i=i+1

    resposta=eleccion("Desexa iniciar sesion?\n\t\t1)Si\n\t\t2)No",2,False)
    if int(resposta) is 1:
        resposta=iniciosesion()
    else:
        print("Continuara en modo anonimo")
        resposta=False
    try:
        with open (constant.PATH+"historial.json","w") as file_historial:
            #Timezone by defect is 2 hours less than out timezone,so we use "+2" and we dont need to install "os" library
            file_historial.write(str(time.gmtime(time.time())[0])+"-"+str(time.gmtime(time.time())[1])+"-"+str(time.gmtime(time.time())[2])+": {\n")
        with open(constant.PATH+"temporal.json",'w') as file_temporal:
            file_temporal.write("{\n")
    except Exception as e:
        print("ESTO NON DEBERIA SALTAR NUNCA",str(e))
    return resposta


#Prints the menu,this code could have been in the main .py
def menu(sesion):
    if sesion is False:#No log in
        try:
            resposta=int(input("\nQue desexa facer?\n\t1)Modo entrenamento\n\t2)Modo practica\n\t3)Ver historial da sesion\n\t4)Probar lectura dos JSONS\n\t5)Iniciar Sesion\n\t6)Pintar vectores\n\t7)Probar cousas random \n\t0)Sair"))
            if resposta is 5:
                resposta = 15
        except:
            resposta=int(31239)
    else:
        try:
            resposta=int(input("\nQue desexa facer?\n\t1)Modo entrenamento\n\t2)Modo practica\n\t3)Ver historial da sesion\n\t4)Probar lectura dos JSONS\n\t5)Probar Clasificadores\n\t6)Pintar vectores\n\t7)Probar cousas random \n\t0)Sair"))
        except:
            resposta=int(31239)
    return resposta


#Simple method to show the historial of the sesion
def verhistorial():
     try:
       with open(constant.PATH+"historial.json","r") as file:
         contido=file.read()
         indexini=0
         indexfin=0
         vacio = True
         indexini=contido.find("{",indexfin)
         while contido.find("Value",indexini) is not -1:
            if vacio is True:#that means we are in the first interaction
                print("Hora\t\tNombre\t\tPotencia\tEtiqueta")
                print("--------------------------------------------------------")
            vacio = False
            indexini=contido.find("-",indexini)
            aux=str(contido[int(indexini)-2:indexini+3])
            indexini=contido.find("Value",indexfin)+len("Value")
            indexfin=contido.find("]",indexini)
            imprimir=aux+contido[int(indexini)+5:int(indexfin)]
            imprimir=imprimir.replace("\t\t","\t").replace("\n","").replace("\"","").replace("Potencia:","").replace("Calificacion:","").replace("Nombre:","").replace("-",":")
            print(imprimir)
         if vacio is True:
            print("Non hai rexistro de ningun golpe para clasificar na sesion")
     except Exception as e:
         print("eeeeeeeeeee",e)


#Show all the hits we have in constant.py
def mostrar_golpes():#Ensenha os golpes nada mais
    print("Escolla un dos seguintes golpes")
    j=0
    while j < len(constant.GOLPES):
        print("\t"+str(j+1)+")"+constant.GOLPES[j])
        j=j+1


#Show all the directions we have in constant.py
def mostrar_direccions():
    print("\nComo foi o golpe?")
    j=0
    while j < len(constant.DIRECCIONS):
        print("\t"+str(j+1)+")"+constant.DIRECCIONS[j])
        j=j+1


#Changes format and return the label predicted
def getresultado(forza,clf):
    etiquetar=[[]]
    i=0
    aux=np.array(forza)
    while i < len(forza):
        etiquetar[0].append(int(aux[i]))
        i=i+1
    return str(clf.predict(etiquetar))


def getfromhits_database(BD,hitname,nombre):
    if str(nombre) == "clf":
        j=1
    elif str(nombre) == "sel_atrib":
        j=2
    else:
        j=0
    i=0
    while i < len(constant.GOLPES): #we have all hits in BD so...
        if str(BD[i][0]) == str(hitname):
             return  BD[i][j]
        i=i+1
    return str(NULL)



#Get the power of the vector
#NOTE:We wont use "sqrt" in order not to import "math"
#ESTA MAL FEITA A POTENCIA,ESTAMOS FACENDO A SUMA DOS MODULOS E NON O MODULO DA SUMA.ESTAMOS CALCULANDO MAL ESO
def potencia(vector):
    nsba=int(len(vector)/3)#Number of samples by axis
    pacelerometro=[0]*9#we have 9 accelerometer
    i=0
    pot=0
    interaccion=0
    while i < len(vector):
        tosqrt=0
        while tosqrt < nsba:
            pacelerometro[interaccion]=float(pacelerometro[interaccion])+float(vector[i+tosqrt])**2
            tosqrt=tosqrt+1
        pacelerometro[interaccion]=pacelerometro[interaccion]**0.5
        interaccion=interaccion+1
        i=i+nsba#we got now the index fo the first value of the accelerometer

    #now we have all the pot of the accelerometers,so lets calculate the global
    i=0
    while i < len(pacelerometro) :
        pot=pot+pacelerometro[i]
        i=i+1
    return pot


#This method will return the power average.The first one(when we log in) is calculated with the 10 last samples
#of your profile.JSON. Then,we will use the sesion hits to recalculate the average,but we will only use the samples
# which value is higher than the minimum value we are using to calculate the media.
#We are doing this trying not to be affected by the tiredness
def mediapot(profilevector,sesionvector):
     profilevector.extend(sesionvector)
     while len(profilevector) > constant.NSA_PW:
         indice=profilevector.index(min(profilevector))
         del profilevector[indice]
     #Agora temos o vector cas mostras que queremos,vamos facer a media 
     i=0
     media=0
     while i < len(profilevector):
        media=media+profilevector[i]
        i=i+1
     media=media/constant.NSA_PW
     return media

#Este metodo devolve a potencia dos 10 ultimos golpes,se pasas etiqueta dos 10 ultimos con esa etiqueta
def ultimosgolpes(sesion,hitname,etiqueta=''):
    if ".json" not in sesion:
        sesion=sesion+".json"

    auxvect=valueandlabels(sesion,hitname)[0]
    values=auxvect[0:int(len(auxvect)/2)]
    labels=auxvect[int(len(auxvect)/2):int(len(auxvect))]
    mediapot=0
    vectortotalfinal=[0]*constant.NSA_PW #Este vai ser para calcular a potencia en base todas as patadas
    vectorparcialfinal=[0]*constant.NSA_PW #Este vai ser para calcular a potencia en base patadas da etiqueta X
    j=0
    k=-1
    i = -constant.NSA_PW
    while i < 0 :
        vectortotalfinal[j]=potencia(values[k])
        k=k-1
        i=i+1
        j=j+1
    j=0
    k=-1
    i= -constant.NSA_PW

    if etiqueta:
        while i < 0:
            if labels[k] == etiqueta:
               vectorparcialfinal[j]=potencia(values[k])
               i=i+1
               j=j+1
            k=k-1
        return vectorparcialfinal
    #Este e o vector das ultimas 10 mostras
    return vectortotalfinal



#Give us one abreviature we will use in archives(more confortable)
def abreviatura(golpe):
    if " " in golpe:
        index=golpe.find(" ")
        abrev=golpe[0:3]+golpe[index+1:index+4]+"_clf"
    else:
        abrev=str(golpe[0:3])+"_clf"
    return abrev


#Repeats the message until a valid number number is chosen,last parameter indicate if "0" is a valid number
def eleccion(mensaxe,nparametros,haicero):
    valido=0
    while valido is 0:
        try:
            devolver=input(mensaxe)
            if(haicero is True):
                if(int(devolver) <=nparametros):
                    valido =1
            else:
                if(int(devolver) <= nparametros and int(devolver)!= 0):
                    valido=1
        except:
            valido = 0
    return devolver


#Interactive menu to choose the hit+direction
def seleccion_golpe():
    print("Escolla un golpe:")
    invalido = True
    while invalido:
        invalido = False
        mostrar_golpes()
        golpe=input()
        try:
            golpe=constant.GOLPES[int(golpe)-1]
        except:
            print("Ha seleccionado un numero invalido")
            invalido = True
    print("Has seleccionado "+str(golpe))
    devolver=abreviatura(golpe)
    return devolver


#Return all the hits we have clasifies, 0 if the list is empty and False if an invalid number has been chosen
def elexir_golpes_clasificados(GolpesClasificados,Ceromessage):
    tamano=0
    print("-----------------------------------------")
    interaccion = 0
    while interaccion < len(GolpesClasificados):
        j=0
        while j < len(constant.GOLPES):
            i=0
            if abreviatura(constant.GOLPES[j]) == GolpesClasificados[interaccion]: #this is True if the hit is in GolpesClasificados(has been clasified)
                print("\t"+str(tamano+1)+")"+constant.GOLPES[j])
                tamano = tamano+1
            j=j+1
        interaccion=interaccion+1
    if tamano is 0:
        print("No hay registros de golpes clasificados,no puede entrenar asi")
        return -1
    else:
        print("\t0)"+Ceromessage)
        try:
            golpe=int(input("Escolla o golpe que desexa entrenar:"))
        except:
            golpe=0
        if golpe > tamano:
            print("Operacion invalida")
            return False
    return golpe


#Return all the abrevs are present in the sesion.json
def cargarperfil(sesion):
    with open(constant.PATH+str(sesion)+".json","r") as file:
        index_palabra=0
        index_finpalabra=0
        indexaux=0
        todosvalores=[]
        contido=file.read()
        while contido.find("_",index_finpalabra) is not -1:
            if int(index_palabra) is not 0:#if index is 0, that means we are in the first interaction
                indexaux=contido.find("}",index_finpalabra)
            index_palabra=contido.find("\"",indexaux)
            index_finpalabra=contido.find("\"",index_palabra+3)#u can choose any number [1,6]
            todosvalores.append(contido[index_palabra+1:index_finpalabra])
        #Now we have all values, but some of them can be duplicated because we have no order in the json.
        #So, we will eliminate the duplicated values(its not neccesary but it can create confusion if someone un len(abrevs))
        i = 0
        while i < len(todosvalores):
            if todosvalores[i] in todosvalores[i+1:]:#we will eliminate the first values instead of the last ones
                del todosvalores[i]
            else:#If we delete something in position X, position X+1 will be the new X.So,we cant add 1 to the loop
                i=i+1
    return todosvalores


#Writes something in JSON format in the archive given."Abreviatura" is the "dad" of string,forza and calidade.
#If u give "forza and calidade", then the "string"parameter does nothing.Forza and calidade are lists
def escribirJSON(abreviatura,archivo,tempos='',forza='',calidade='',string=''):
#NOTE:We differenciate de abreviatures in all json by "_"so, dont write something with "_"
    if archivo is False:
        archivo="temporal.json"
    else:
        archivo=str(archivo)+".json"
    with open(constant.PATH+str(archivo),'a') as file:
             i=0
             file.write("\t\""+str(abreviatura)+"\":{\n")
             file.write("\t\t\"Value\": [\n")
             if forza and calidade:
                 while i < len(forza) :
                     file.write("\t\t\t"+str(forza[i])+"\n")
                     i=i+1
                 file.write("\t\t\t]\n")
                 i= 0
                 file.write("\t\t\"Label\": [\n")
                 while i < len(calidade) :
                     file.write("\t\t\t"+str(calidade[i])+"\n")
                     i=i+1
                 file.write("\t\t\t]\n")

                 if tempos:
                     i=0
                     file.write("\t\t\"Times\": [\n")
                     while i < len(tempos):
                         file.write("\t\t\t"+str(tempos[i])+"\n")
                         i=i+1
                     file.write("\t\t\t]\n")
                     file.write("\t}\n")
                 else:
                     file.write("\t}\n")
             else:
                 file.write("\t\t\t"+str(string)+"\n")
                 file.write("\t\t\t]\n")
                 file.write("\t\t}\n")
    file.close()



#Simple loop which introduce the clf in the hits_database
def insertinBD(BD,hitname,nombre,clf):

    if nombre == "clf":
        j=1
    if nombre == "sel_atrib":
       j=2
    i=0
    while i < len(constant.GOLPES):
        if str(BD[i][0]) == str(hitname):
            BD[i][j]=clf
        i=i+1


#Change format to use in SVM
def reshapecasero(vector):
      aux=[]
      i=0
      while i < len(vector):
          if type(vector[i]) is "string":
              vector[i]=vector[i].strip()
          aux.append(list(map(float,vector[i])))
          i=i+1
      return aux

def copiar2Darray(vector):
    i=0
    aux=[[]]
    while i < len(vector):
        if i is 0:
            aux[i]=vector[i][:]
        else:
            aux.append(vector[i][:])
        i=i+1
    return aux


#Convert 2D [][] from list to string
def string2int2D(vector):
    i=0
    k=0
    while i < len(vector):
        k=0
        while k < len(vector[i]):
            vector[i][k]=int(vector[i][k].strip())
            k=k+1
        i=i+1
    return vector

#Convert 2D [][] from list to float
def string2float2D(vector):
    i=0
    k=0
    while i < len(vector):
        k=0
        while k < len(vector[i]):
            vector[i][k]=float(vector[i][k].strip())
            k=k+1
        i=i+1
    return vector

#AQUI MAIS FUNCIONS DE CALIBRAR PORQUE QUEREMOS CHEGAR Ó 90%
def calibrar(sesion,hitname,verresult):
      warnings.filterwarnings("ignore", category=DeprecationWarning)
      if sesion is False:
                sesion="temporal"
      simplefilter(action='ignore', category=FutureWarning)
      scoring = ['precision_macro', 'recall_macro', 'precision_micro', 'recall_micro', "f1_micro", "f1_macro", "accuracy"]
      auxvect=valueandlabels(sesion+".json",hitname)[0]
      #We will get now a list of randomindex to prove each tolerance(20% of samples)
      values=auxvect[0:int(len(auxvect)/2)]
      labels=auxvect[int(len(auxvect)/2):int(len(auxvect))]
      linear = LinearSVC(max_iter=constant.MAXITER)
      clf1 = SelectFromModel(linear.fit(values, labels), prefit=True)#O de prefit e para que nos deixe usar o SelectFromModel
      new_values_linear = clf1.transform(values)
      #ESTO PARA NON TRANSFORMAR NADAnew_values_linear=values
      linear = LinearSVC(max_iter=constant.MAXITER)
      #vale,agora temos en new_values todas as mostras de todos os golpes
      #len(values)=60 porque temos 60 golpes almacenados
      #LEN(VALUES[I]) e 135,pero o novo valor(que almacenaremos en new_values_linear por exemplo)estara reducido e sera 60(mas menos)
      i=0
      #10 years later i know how to do change the format
      """k=[]
      while i < len(new_values_linear):
          k.append(list(map(float,new_values_linear[i])))
          i=i+1
      new_values_linear=k
      """
      new_values_linear=reshapecasero(new_values_linear)
      #y_predict = cross_val_predict(linear, new_values, labels, cv=10)
      scores = cross_validate(linear, new_values_linear, labels, scoring=scoring, cv=10, return_train_score=False)
      i=0
      acerto=0
      if verresult is True:
          print("--------------------------CROSSVALIDATE--------------------------")
          print("Datos de LinearSVC + SelectFromModel")
          print("Fit time: " + str(sum(scores["fit_time"]) / 10))
          print("Score time " + str(sum(scores["score_time"]) / 10))
          print("precision_micro"+ str(sum(scores["test_precision_micro"]) / 10)+" Importante se as mostras non estan balanceadas")
          print("Accuracy: " + str(sum(scores["test_accuracy"]) / 10))
      i=0
      k=[]
      new_values_logistic=auxvect[0:int(len(auxvect)/2)]
      while i < len(new_values_logistic):
          k.append(list(map(float,new_values_linear[i])))
          i=i+1
      new_values_logistic=k
      #ESTO ESTA BEN PERO PROBA TODO CON TODO,TEMOS QUE FACER(IGUAL COS CORCHETES) QUE NON PROBE TODOS OS VALORES CON TODOS PARA PODER USAR O SOLVER E MULTINOMIAL EN MULTICLASS
      tuned_parameters=[{'C':[0.01,0.02,0.03,0.04,0.05,0.75,0.9,1.0],'penalty':["l1"],'multi_class':["ovr"]}]
      logistic=GridSearchCV(LogisticRegression(),tuned_parameters)
      scores = cross_validate(logistic, new_values_logistic, labels, scoring=scoring, cv=10, return_train_score=False)
      if verresult is True:
          print("--------------------------CROSSVALIDATE--------------------------")
          print("Datos de LogisticRegression + Grid Search")
          print("Fit time: " + str(sum(scores["fit_time"]) / 10))
          print("Score time " + str(sum(scores["score_time"]) / 10))
          print("precision_micro"+ str(sum(scores["test_precision_micro"]) / 10)+" Importante se as mostras non estan balanceadas")
          print("Accuracy: " + str(sum(scores["test_accuracy"]) / 10))
          print("----------------------------------------------------------------")

      resposta=int(eleccion("Elixa un clasificador dos que se ensinaron por pantalla\n\t\t1)LinearSVC + SelectFromModel\n\t\t2)LogisticRegression + Grid Search",3,False))
      if verresult is True:
          resp2=int(eleccion("Desexa probar empiricamente a precisión do clasificador?\n\t\t1)Si\n\t\t2)No",2,False))
          overfit=int(eleccion("Desexa probar con ou sin overfittin?\n\t\t1)Sin overfitting\n\t\t2)Con overfitting",2,False))
      else:
          resp2=2
          overfit=1
      #1-->Without overfit
      if resposta is 1:
           if overfit is 1:
               if verresult is True:
                   print("--------------Sin overfitting os resultados seran mellores--------------")
               linear.fit(new_values_linear,labels)
               if resp2 is 1:
                   probarclf(new_values_linear,labels,linear)
               return [linear,clf1] 
           else:
               if verresult is True:
                   print("--------------Con overfitting esperanse peores resultados--------------")
               linear.fit(values,labels)
               if resp2 is 1:
                   probarclf(values,labels,linear)
               return [linear,"null"]
      elif resposta is 2:
          if overfit is 1:
              if verresult is True:
                  print("--------------Sin overfitting os resultados seran mellores--------------")
              logistic.fit(new_values_logistic,labels)
              if resp2 is 1:
                  probarclf(new_values_logistic,labels,logistic)
              return [logistic,tuned_parameters]
          else:
               if verresult is True:
                   print("--------------Con overfitting esperanse peores resultados--------------")
               logistic.fit(values,labels)
               if resp2 is 1:
                   probarclf(values,labels,logistic)
               return [logistic,"null"]


      #THIS CODE PLOTS THE RESULTS,ITS NOT USEFULL BECAUSE THE SAMPLES ARE OVERLAPPING EACH OTHER
      #fig, ax = plt.subplots()
      #ax.scatter(labels, y_predict, edgecolors=(0, 0, 0))
      #ax.plot([min(labels), max(labels)], [min(labels), max(labels)], 'k--', lw=4)
      #ax.set_xlabel('Measured')
      #ax.set_ylabel('Predicted')
      #fig.show()

      #print(y_predict.scores())

      #return clfdatacerts

#clf has a default tolerance, but sometimes its not the correct one.So, we have this method in order to fin the tolerance that minimise the error
def probarclf(valuesparam,labelsparam,clf):
      vtp=[]#values to prove
      ltp=[]#labels to prove
      stp=[]#Samples to proove
      #We will get now a list of randomindex to prove each tolerance(20% of samples)
      #this while generate random index to get prove vector
      repetir=100
      clfdatatolerance=[]#we will store all clf's tol and the number of correct answer
      clfdatacerts=[]
      interaccion=0
      frontalpredecido=0
      dereitapredecido=0
      esquerdapredecido=0
      realizacionesquerda=0
      realizaciondereita=0
      realizacionfrontal=0
      falloesquerda=0
      fallodereita=0
      fallofrontal=0
      prct=0.1
      acierto=0
      print("Vamos separar o "+str(100*prct)+"% das "+ str(len(valuesparam)) +" mostras para comprobar o clasificador variando parametros")
      print("\n\t\t\tErrores\n")
      print("Valor predecido---Valor real")
      while interaccion < repetir:
          values=copy(valuesparam)
          labels=copy(labelsparam)
          del stp[:]
          del vtp[:]
          del ltp[:]
          i=0
          while i < int(prct*len(values)):
              aux=False#this is just to cross always the first [value for value in variable]ine in each interaction
              while aux is False:#we cant have 2 equal numbers.So, if we have one number in the list we take other
                  aux=np.random.randint(0,int(len(values)-1))
                  if aux in stp:
                      aux=False
              stp.append(aux)
              i=i+1
          #Okey now we have the index of the prove samples.We will delete them from the vectors
          stp.sort(reverse=True)#We will delete first the latest index.If we dont do that,out "5" will be "4" if we delete some number from [0,4]
          i=0
          while i < len(stp):
             vtp.append(values[stp[i]])
             ltp.append(labels[stp[i]])
             del values[stp[i]]#stp is a list of index.
             del labels[stp[i]]
             i=i+1
          #Now we have a vector to make the clf(values,labels)and a vector to proove(vtp,stp)
          #Okey,now we are going to make different clf with different "tol" and we are going to choose the best
          clf.fit(values,labels)
          j=0
          #now we have to prove all vector stored in "vtp" and compore with their respective labels.
          while j < len(vtp):
             resultado=getresultado(vtp[j],clf)[2:-2]
             if str(ltp[j]) == "Esquerda":
                 realizacionesquerda=realizacionesquerda+1
             elif str(ltp[j]) == "Dereita":
                 realizaciondereita=realizaciondereita+1
             else:
                 realizacionfrontal=realizacionfrontal+1
             if resultado==ltp[j]:
                 acierto=acierto+1
             else:#AQUI SIGNIFICA QUE FALLAMOS,VAMOS DISTINGUIR PARA SABER SE FALLAMOS TODOS OS S OU E ALEATORIO
                 print(str(resultado)+"\t\t\t"+str(ltp[j]))
                 if str(ltp[j]) == "Esquerda":
                     falloesquerda=falloesquerda+1
                 elif str(ltp[j]) == "Dereita":
                     fallodereita=fallodereita+1
                 else :
                     fallofrontal=fallofrontal+1
                 if str(resultado) == "Esquerda":
                     esquerdapredecido=esquerdapredecido+1
                 elif str(resultado) == "Dereita":
                     dereitapredecido=dereitapredecido+1
                 else:
                     frontalpredecido=frontalpredecido+1
             j=j+1
                #I let this line commented if someone wants to see the comparison
                #print("Tolerancia--"+str(i)+"\t\tValor Predecido--"+str(resultado)+"\t\tValor real"+str(ltp[j]))
          interaccion=interaccion+1
      if realizacionesquerda is 0:
          realizacionesquerda=1
      if realizaciondereita is 0:
          realizaciondereita=1
      if realizacionfrontal is 0:
          realizacionfrontal=1
      print("Deronse "+str(realizaciondereita)+" golpes bos, "+str(realizacionesquerda)+" golpes de esquerda e "+str(realizacionfrontal)+"golpes frontais")
      print("Acertou "+str(acierto)+ " de "+str(realizaciondereita+realizacionesquerda+realizacionfrontal)+"-->"+str(float(100*acierto/(realizaciondereita+realizacionesquerda+realizacionfrontal)))+"%")
      print("Fallaronse o "+str(float(100*falloesquerda/realizacionesquerda))+"% dos golpes de esquerda dados")
      print("Fallaronse o "+str(float(100*fallodereita/realizaciondereita))+"% dos golpes de dereita dados")
      print("Fallaronse o "+str(float(100*fallofrontal/realizacionfrontal))+"% dos golpes frontais dados")
      print("O "+str(float(100*esquerdapredecido/(fallodereita+fallofrontal+falloesquerda)))+"% dos fallos foi por predecir esquerda sin selo")
      print("O "+str(float(100*dereitapredecido/(fallodereita+fallofrontal+falloesquerda)))+"% dos fallos foi por predecir dereita sin selo")
      print("O "+str(float(100*frontalpredecido/(fallodereita+fallofrontal+falloesquerda)))+"% dos fallos foi por predecir frontal sin selo")


#Get all the values and labels from the specific hitname present in sesion.json
def valueandlabels(sesion,hitname,tempo=''):
        with open(constant.PATH+sesion) as temporal_file:
             #We will take the needed vectors(although they will be strings)
                contido=temporal_file.read()#we need to use read instead of readlines in order to use "find" after that
                index_values=0#You will understand this part asignment after reading whole loop
                values=""
                labels=""
                tempos=""
                #This while let us add samples to one clf who has been already created,we are reading from a file and we can have the hitname more than 1 time
                while contido.find(hitname,index_values) is not -1:#we took index_values but we just need something more advanced than the hitname(dont wanna took the same)
                    index_golpe=contido.find(hitname+"\":",index_values)+len(hitname+"\":")
                    index_values=contido.find("\"Value\": [",index_golpe)+len("\"Value\": [")
                    indexfin_values=contido.find("\"Label\": [",index_values)-6#this 6 is jsut to delete the "]" which close the values
                    index_label=contido.find("\"Label\": [",index_values)+len("\"Label\": [")
                    indexfin_label=contido.find("]",index_label)-4#I dont really know why "4" is the correcto number, but it deleted last "\n" and "]"
                    if tempo:
                        index_tempo=contido.find("\"Times\": [",indexfin_label)+len("\"Times\": [")
                        indexfin_tempo=contido.find("]\n\t}",index_tempo)
                    if len(values) is 0:
                        values=contido[index_values:indexfin_values].strip().replace("\t"," ")
                        labels=contido[index_label:indexfin_label].replace("\t"," ")
                        if tempo:
                            tempos=contido[index_tempo:indexfin_tempo].strip().replace("\t"," ")
                    else:
                        values=values+"\n"+str(contido[index_values:indexfin_values].strip().replace("\t"," "))
                        labels=labels+str(contido[index_label:indexfin_label].replace("\t"," "))
                        if tempo:
                            tempos=tempos+"\n"+str(contido[index_tempo:indexfin_tempo].strip().replace("\t"," "))
                values=values.split("\n")
                if tempo:
                    tempos=tempos.split("\n")
                #Now we have all the information in list(string)
                i=0
                while i < len(values):
                    values[i]=values[i].replace("''","").strip()
                    if tempo:
                        tempos[i]=tempos[i].replace("''","").strip()
                    i=i+1
                i=0
                #Okey this method just changes the type of values, we have 1 array of string and we want 1 array 2D of ints
                while i < len(values):
                    values[i]=values[i][1:len(values[i])-1].replace("'","").split(",")
                    if tempo:
                        tempos[i] = tempos[i][1:len(tempos[i]) - 1].replace("'", "").split(",")
                    i=i+1
                labels=labels.strip().split("\n")
                i=0
                while i < len(labels):
                    labels[i]=labels[i].strip()
                    i=i+1
                values.extend(labels)
        if not tempo:
            tempos=[0]
        return [values,tempos]


#Return the value
def leerhistorial(hitname,etiqueta=''):
    final_vector_power=[]
    with open (constant.PATH+"historial.json") as file:
        contido=file.read()
        power=""
        labels=""
        index_potencia=0
        while contido.find(hitname,index_potencia) is not -1:
            index_potencia=contido.find(hitname,index_potencia)+len(hitname)
            index_potencia=contido.find("Potencia:",index_potencia)+len("Potencia:")
            indexfin_potencia=contido.find("Calificacion:",index_potencia)
            index_calificacion=indexfin_potencia+len("Calificacion:")
            index_fincalificacion=contido.find("]",index_calificacion)
            if len(labels) is 0:
                power=contido[index_potencia:indexfin_potencia].strip().replace("\t"," ")
                labels=contido[index_calificacion+1:index_fincalificacion-5].strip().replace("\t"," ")
            else:
                power=power+"\n"+str(contido[index_potencia:indexfin_potencia].strip().replace("\t"," "))
                #This +/-1 are just to delete "
                labels=labels+"\n"+str(contido[index_calificacion+1:index_fincalificacion-5].strip().replace("\t"," "))
        labels=labels.split("\n")
        power=power.split("\n")
        i=0
        if power[0] is "":
            return [0]
        while i < len(power):
            power[i]=float(power[i])
            i=i+1
        if etiqueta:
            i=0
            while i < len(power):
                if labels[i]!=etiqueta:
                    del power[i]
                    del labels[i]
                else:
                    i=i+1
        return power


#Create and return the clasifier about the hitname thanks to the information given by "valuesandlabels"
def createclf(sesion,hitname,tolerance):
     if sesion is False:
            sesion="temporal.json"
     else:
            sesion=str(sesion)+".json"
     #Now we have the vectors que want to have,lets make the clasiffier(less tab cause we dont need the archive anymore)
     aux=valueandlabels(sesion,hitname)[0]
     values=aux[0:int(len(aux)/2)]
     labels=aux[int(len(aux)/2):int(len(aux))]
     clf=LinearSVC(max_iter=constant.MAXITER,random_state=constant.RANDOM_STATE,tol=tolerance)
     clf.fit(values,labels)
     return clf


#Read the JSONS we got from the hit,its a loop that send all arquives to "leer_arquivo".Take all values and return the important ones(reduces by "reduce")
def readJSONS() :
        time_now= time.time()#JSONS will be overwritten al time and we just need the last value
        i=0
        cambio= True
        j=30###########################################################ARCHIVE NAME###########################################################
        #WE HAVE "REPETITIVE" NAMES so we can use a loop to read all the archives
        Time=[]
        Value=[]
        while i < constant.NJSONS:
            name="P8_"+str(j)+".json"
            Archive_data=leer_arquivo(constant.PATH+name,time_now)
            Time.extend(Archive_data[:int((len(Archive_data)/2))])
            Value.extend(Archive_data[int((len(Archive_data)/2)):])
            i=i+1
            if cambio:
                cambio= False
                j=j+1
            else :
                cambio= True
                j=j+3

        if constant.TIPOFILTRO == "normal":
            FinalTimes=reduce(Time,Value)
        elif constant.TIPOFILTRO == "deletevibration":
            FinalTimes=reducedelvibr(Time,Value)
        elif constant.TIPOFILTRO == "reducepot":
            FinalTimes=reducepot(Time,Value)
        elif constant.TIPOFILTRO == "nada":
            return [Time,Value]
        FinalValues=[]
        i=0
        tam=len(FinalTimes)/2#we need to do that cause len changes with pop
        while i < tam :
            FinalValues.append(FinalTimes.pop())
            i=i+1
        FinalValues.reverse()
          #WE HAVE THE TIME VALUES FILTERED HERE, I THINK I DONT REALLY NEED IT SO I WONT RETURN THEM, BUT THEY ARE HERE IF SOMEONE NEEDS IT SOMEDAY

        return [FinalValues,FinalTimes]


#It Reads one json and gets all times/values,then returns the vector chronological nearest(values+times) thanks to "masreciente"
def leer_arquivo(path,time_now):
        result_value=[]
        auxvector=[]
        with open(path) as file_object:
            contents = file_object.read()
    #We are going to isolate the information que really want from the JSON
        X_index=contents.find("\"axis_x\": {")+len("\"axis_x\": {")
        Xtime_index=contents.find("\"times\": [",X_index)+len("\"times\": [")
        Xtime_indexfin=contents.find("]",Xtime_index)
        Xvalue_index=contents.find("\"values\": [",X_index)+len("\"values\": [")
        Xvalue_indexfin=contents.find("]",Xvalue_index)
        Xtime=contents[Xtime_index:Xtime_indexfin].split(",")
        Xvalue=contents[Xvalue_index:Xvalue_indexfin].split(",")

        Y_index=contents.find("\"axis_y\": {")+len("\"axis_y\": {")
        Ytime_index=contents.find("\"times\": [",Y_index)+len("\"times\": [")
        Ytime_indexfin=contents.find("]",Ytime_index)
        Yvalue_index=contents.find("\"values\": [",Y_index)+len("\"values\": [")
        Yvalue_indexfin=contents.find("]",Yvalue_index)
        Ytime=contents[Ytime_index:Ytime_indexfin].split(",")
        Yvalue=contents[Yvalue_index:Yvalue_indexfin].split(",")

        Z_index=contents.find("\"axis_z\": {")+len("\"axis_z\": {")
        Ztime_index=contents.find("\"times\": [",Z_index)+len("\"times\": [")
        Ztime_indexfin=contents.find("]",Ztime_index)
        Zvalue_index=contents.find("\"values\": [",Z_index)+len("\"values\": [")
        Zvalue_indexfin=contents.find("]",Zvalue_index)
        Ztime=contents[Ztime_index:Ztime_indexfin].split(",")
        Zvalue=contents[Zvalue_index:Zvalue_indexfin].split(",")
        #Se se pegan 3 golpes teremos moitos vectores, coas funcions de abaixo collemos o ultimo golpe
        Xvector=masreciente(Xtime,Xvalue,time_now)
        Yvector=masreciente(Ytime,Yvalue,time_now)
        Zvector=masreciente(Ztime,Zvalue,time_now)

        #Aqui o que facemos e concatenar os valores X,Y,Z
        try:
            i=len(Xvector)
        except:
            raise Exception("Non hai ningun valor nos JSONS")
        middle=i/2
        while i > middle: #The values are the just the half part
            auxvector.append(Xvector.pop())
            i=i-1
        auxvector.reverse()
        result_value=result_value+auxvector
        del auxvector[:]

        i=len(Yvector)
        middle=i/2
        while i > middle: #The values are the just the half part
            auxvector.append(Yvector.pop())
            i=i-1
        auxvector.reverse()
        result_value=result_value+auxvector
        del auxvector[:]

        i=len(Zvector)
        middle=i/2
        while i > middle: #The values are the just the half part
            auxvector.append(Zvector.pop())
            i=i-1
        auxvector.reverse()
        result_value=result_value+auxvector
        del auxvector[:]

        result_time=Xvector+Yvector+Zvector#Nos vectores solo se quedou o tempo
        result_total= result_time+result_value
        return result_total


#Receive all time/value vector and return the vector that corresponds to the chronological nearest hit
def masreciente(time_vector,value_vector,time_now):
    result=[]
    i=0
    difference=1231231231
    mri=-1#most recent index
    #len(time_hit)=len(value)
    #The following loop will show us the most recent sample while it "cleans" the array
    while i < len(time_vector):
        time_vector[i]=str(time_vector[i]).replace("\n"," ").strip()
        value_vector[i]=str(value_vector[i]).replace("\n"," ").strip()
        try:
            aux=time_now-abs(float(time_vector[i]))
        except:
            raise Exception("Non hai ningun valor reciente nos JSONS")
        if aux < difference :
            diference=aux
            mri=i
        i=i+1
    #NOTE:There are certain number of 0s between each par of individual vectors,but we dont really need to lead with that because the difference
    #between timenow-0 is really big,so we wont start at "0", each individual vector is already ordered so we wont finish at "0" either
    i=constant.NSAMPLES-1
    while i != -1 :
        result.append(time_vector[mri-i])
        i=i-1
    i=constant.NSAMPLES-1
    #We need to return the values too, so we need to join all
    while i != -1 :
        result.append(value_vector[mri-i])
        i=i-1
    return result


#Receive the time/value vector which have all samples from all axis from all json.So we have here(if u didnt change my constnat.py) 10*3*9=270 samples
#We reduce both vectors to 135 samples and return them together as a new 270vector(135time+135value)
def reduce(Time,Value):
    min_index=Time.index(min(Time))
    #There is no order among individual vectors but "inside" each one we have chronological order, so, there is no reason
    #to fin the "start" of the individual vector,because it's "min_index"
    i=0
    max_value=0
    #Value[min_index:min_index+9] is the individual vector
    while i < 10 :
        if abs(int(Value[min_index+i])) > abs(int(max_value)):
            max_value=Value[min_index+i]
        i=i+1
    #Now we have the highest value of the first axis that cross the vibration threshold who, we need to take the time when it happens in order to synchronize all the samples
    index_ref=Value[min_index:].index(max_value)+min_index
    time_ref=Time[index_ref]#we have now the time we wanted(Max_value of the first axis that crossed the vibration threshold)
    pvi=0#Principio do vector individual,non dividiremos o total porque non e necesario
    ResultTime = []
    ResultValue = []
    while pvi < constant.NSAMPLES*constant.NJSONS*3:#well we will have always 3 dimensions
        i=0
        #in the first loop we are going to find the nearest chronological value
        nearest_time=0
        index_nearest=0
        while i < 10:
            if abs(float(time_ref)-float(Time[pvi+i])) < abs(float(time_ref)-float(nearest_time)) :
                 nearest_time=Time[pvi+i]
                 index_nearest=pvi+i#This is the global index(about 270) which we need to do the synchronization
            i=i+1
        #Now, we need to take 5 samples(2 of each side).Problem,if we dont have 2 samples at right(for example) we need to take more on left
        resto_division=float(index_nearest)%10.0
        if resto_division < 2:
                   ResultTime.extend(Time[int(index_nearest-resto_division):int(index_nearest+4+1-resto_division)])#Hard to see, try to think about the samples picture
                   ResultValue.extend(Value[int(index_nearest-resto_division):int(index_nearest+4+1-resto_division)])
        elif resto_division > 7:
                   ResultTime.extend(Time[int(index_nearest-2-(resto_division-7)):int(index_nearest+1+(9-resto_division))])
                   ResultValue.extend(Value[int(index_nearest-2-(resto_division-7)):int(index_nearest+1+(9-resto_division))])
        else:
                   ResultTime.extend(Time[int(index_nearest-2):int(index_nearest+3)])
                   ResultValue.extend(Value[int(index_nearest-2):int(index_nearest+3)])
        pvi=pvi+10
    return ResultTime+ResultValue


#Using TSNE we wanna know if the vectors are distinguishable
def pintarvectoresTSNE(sesion,hitname,sel_atrib=''):
    auxvect=valueandlabels(sesion+".json",hitname)[0]
    values=auxvect[0:int(len(auxvect)/2)]
    labels=auxvect[int(len(auxvect)/2):int(len(auxvect))]
    if str(sel_atrib):
        try:
            values = sel_atrib.transform(values)
            print("Eliminando o overfitting...")
        except:
            print("O selector de atributos que pasou e invalido")
    model=TSNE(learning_rate=100)
    tsne_data=model.fit_transform(values)
    xs=tsne_data[:,0]
    ys=tsne_data[:,1]
    i=0
    aux=[]
    while i < len(labels):
        if labels[i] == "Dereita":
            aux.append("darkred")
        elif labels[i]== "Esquerda":
            aux.append("mediumblue")
        elif labels[i]== "Frontal":
            aux.append("yellow")
        else:
            aux.append("black")
        i=i+1
    plt.scatter(xs,ys,c=aux)
    plt.show()


#This function is not working yet
def pintarvectoresPCA(sesion,hitname):
    auxvect=valueandlabels(sesion+".json",hitname)[0]
    X=auxvect[0:int(len(auxvect)/2)]
    y=auxvect[int(len(auxvect)/2):int(len(auxvect))]


    """x=np.array(values)
    pca=PCA(n_components=15)
    pca.fit(x)
    print(pca.explained_variance_ratio_)
    print(pca.singular_values_)
    """

    data = []

    legend = {0: False, 1: False, 2: False, 3: True}

    colors = {'Iris-setosa': '#0D76BF',
              'Iris-versicolor': '#00cc96',
              'Iris-virginica': '#EF553B'}

    for col in range(4):
        for key in colors:
            trace = dict(
                type='histogram',
                x=list(X[y == key, col]),
                opacity=0.75,
                xaxis='x%s' % (col + 1),
                marker=dict(color=colors[key]),
                name=key,
                showlegend=legend[col]
            )
            data.append(trace)

    layout = dict(
        barmode='overlay',
        xaxis=dict(domain=[0, 0.25], title='sepal length (cm)'),
        xaxis2=dict(domain=[0.3, 0.5], title='sepal width (cm)'),
        xaxis3=dict(domain=[0.55, 0.75], title='petal length (cm)'),
        xaxis4=dict(domain=[0.8, 1], title='petal width (cm)'),
        yaxis=dict(title='count'),
        title='Distribution of the different Iris flower features'
    )

    fig = dict(data=data, layout=layout)
    py.iplot(fig, filename='exploratory-vis-histogram')

#A miña idea basicamente é que o acelerometro vibra dentro,enton non sabemos nunca hacia onde vai
#Para suplir esto, vou ver se hai máis valores positivos que negativos nas 5 mostras que collemos
#Se hai mais do tipo X, poñemos o tipo Y a cero e viceversa,desta forma intentaremos "eliminar a vibracion"
def cambiarjsons(sesion,hitname,novoarquivo,tipo):
    if tipo == "muestrascero":
        acabado = True
    else:
        acabado = False
    auxvect = valueandlabels(sesion + ".json", hitname)[0]
    values = auxvect[0:int(len(auxvect) / 2)]
    labels = auxvect[int(len(auxvect) / 2):int(len(auxvect))]
    #Values ten o numero de golpes(cada patada p.e) e values[X] ten o vector da patada X
    #O formato do vector será:[5 muestras eje X acelerometro 1, 5 muestras eje Y acelerometro 1[...]]

    i=0
    vectorfinal=[[]]
    vectoraux=[]
    k=0
    while k < len(values):
        del vectoraux[:]
        i=0
        while i < len(values[k]):
            j=0
            aux=0
            #Vamos ver se hai mais positivos ou negativos
            while j < 5:
                if int(values[k][i+j]) > 0:
                    aux=aux+1
                else:
                    aux=aux-1
                j=j+1
            if aux > 0:
                #Hai mas valores positivos,vamos a eliminar os negativos
                j = 0
                while j < 5:
                    if int(values[k][i + j]) < 0:
                        values[k][i + j]=0
                    j = j + 1
            else:
                #Hai mas valores negativos,vamos eliminar os positivos
                j = 0
                while j < 5:
                    if int(values[k][i + j]) > 0:
                        values[k][i + j] = 0
                    j = j + 1
            if len(vectoraux) is 0:
                vectoraux=values[k][i:i+5]
            else:
                vectoraux.extend(values[k][i:i+5])
            i=i+5
        #Vectoraux esta correcto
        if len(vectorfinal[0]) is 0:
            vectorfinal[0] = vectoraux[:]
            #O de [:] fai falta para que se cree un novo obxeto e non apunte vectorfinal a aux,asi podemos reiniciar aux
        else:
            vectorfinal.append(vectoraux[:])
        k=k+1
    #AHORA MISMO TEMOS UN VECTOR DE X GOLPES,CADA VECTOR[i] TEN 135(9*3*5) VALORES,TEMOS QUE ESCRIBIESCRIBIR ESTO E VER SE SE PARECE
    #A SEGUINTE IDEA É FACER O MISMO E MIRAR HACIA DONDE VAI A MAIORIA DE EJES E CONTAR SOLO O QUE VAI HACIA ESE LADO.
    #OUTRA IDEA SERIA TRABALLAR CA POTENCIA
    if acabado is True:
        escribirJSON(hitname,novoarquivo,forza=vectorfinal,calidade=labels)
        print("Volvendo a funcion inicial...")
        return
    #Enton vectorfinal ten os golpes, vectorfinal[X] ten as 135 mostras.moitas das cales son 0
    #Para ler todos os datos de todos os ejes X temos que facer [i:i+5](para este eje) e sumarlle a i o necesario para chegar
    #o seguinte eje, é decir 15(5 para pasar a X,5 para Y e 5 para Z)
    print(vectorfinal[0])
    print(eliminarejes(vectorfinal[0],"x"))
    print(eliminarejes(vectorfinal[0],"y"))
    print(eliminarejes(vectorfinal[0],"z"))

def eliminarejes(vectorfinal,eje):
    j=0
    if eje == "x":
        k=0
    elif eje == "y":
        k=5
    elif eje == "z":
        k=10
    else:
        print("FALLO NA DIMENSIOOON")
    contadorpositivo=0
    contadornegativo=0
    cambioforzado=0
    gardarpositivos=[]
    gardarnegativos=[]
    permitir = True
    while j < len(vectorfinal):
        conseguido=False
        if permitir is True:
            if int(vectorfinal[j+k]) > 0:
                contadorpositivo=contadorpositivo+1
                gardarpositivos.append(math.floor(int(j) /  15.0)+k)
                conseguido=True
            elif int(vectorfinal[j+k]) < 0:
                contadornegativo=contadornegativo+1
                gardarnegativos.append(math.floor(int(j) / 15.0)+k)
                conseguido=True
            else:
                j=j+1
                cambioforzado = cambioforzado + 1
                if cambioforzado is 5:
                    conseguido=True
                    contadorpositivo=contadorpositivo+1
            if conseguido:
                j=j+(15-cambioforzado)
                cambioforzado=0
            if int(j)+int(k) >= len(vectorfinal):
                permitir=False
    if contadorpositivo < contadornegativo:
        print("No eje " + str(eje) + " hai mais negativos")
        borrar=gardarpositivos
    else:
        print("No eje " + str(eje) + " hai mais positivos")
        borrar=gardarnegativos
    j=0
    while j < len(borrar):
        este=borrar[0]
        vectorfinal[15*este:15*este+5]=[0]*5
        del borrar[0]
    return vectorfinal

    #Agora temos o que hai que eliminar,solo necesitamos

def cambiaramaximo(sesion,hitname,novoarquivo):
    auxvect = valueandlabels(sesion + ".json", hitname)[0]
    values = auxvect[0:int(len(auxvect) / 2)]
    labels = auxvect[int(len(auxvect) / 2):int(len(auxvect))]
    # Values ten o numero de golpes(cada patada p.e) e values[X] ten o vector da patada X
    # O formato do vector será:[5 muestras eje X acelerometro 1, 5 muestras eje Y acelerometro 1[...]]
    i = 0
    vectoraux = []
    vectormax=[]
    vectormin=[]
    borrar=0
    values=string2int2D(values)
    while i < len(values):
        vectormax.append(max(values[i]))
        vectormin.append(min(values[i]))
        i=i+1
    i=0
    #Agora temos que obter un vector final que teña os valores maximos en valor absoluto
    vectorabsmax=[]
    i=0
    while i < len(vectormax):
        if abs(vectormax[i]) > abs(vectormin[i]):
            vectorabsmax.append(vectormax[i])
        else:
            vectorabsmax.append(vectormin[i])
        i=i+1

    #Agora temos un vector cos valores maximos

    i=0
    k=0
    while i < len(values):
        k=0
        while k < len(values[i]):
            if values[i][k] != vectorabsmax[i]:
                values[i][k] = 0
            k=k+1
        i=i+1
    bucle=0
    vectorfinal=copiar2Darray(values)
    k=0
    while k < len(values):
        i=0
        bucle=0

        while i < len(values[k]):
            if vectorabsmax[k] not in values[k][i:i+5]:
                del vectorfinal[k][bucle:bucle+4]
                bucle=bucle+1#+1 para deixar un 0 e non volver borralo,asi estamos reducindo de cinco 0s a 1 solo
                i=i+5
            else:
                porborrar=4
                avanzado = False
                while porborrar > 0:
                    if vectorabsmax[k] is not values[k][i]:
                        del vectorfinal[k][bucle]
                        porborrar=porborrar-1
                    else:
                        avanzado=True
                        bucle=bucle+1
                    i = i + 1
                if avanzado is False:
                    bucle=bucle+1

                #############################################################################
                #NOTA: AQUI HAI UNHA POSIBLE FONTE DE ERROR:2 VALORES MAXIMOS NO MESMO RANGO#
                #############################################################################
        k=k+1

    escribirJSON(hitname, novoarquivo, forza=vectorfinal, calidade=labels)


#Aqui vamos a ler o primeiro valor de cada eje,miramos o signo e colleremos solo as muestras que teñan ese signo.
def reducedelvibr(tempos,values):
    #A lectura dos acelerómetros e circular,primeiro leese unha meustra do eje X,despois Y,despois Z.Despois cambia
    #a outro acelerómetro.Fai este bucle 10 veces.
    #Como temos ordenados os vectores como MuestrasX,Y,Z--MuestrasX,Y,Z...Con coller o indice do menor valor, xa temos
    #automaticamente o indice do menor de cada eje
    tempos=string2float2D([tempos])
    tempos=tempos[0]
    tempref_x=min(tempos)

    indexref_x=tempos.index(tempref_x)
    indexref_y=indexref_x+10
    tempref_y=tempos[indexref_y]
    indexref_z=indexref_y+10
    tempref_z=tempos[indexref_z]

    values=string2float2D([values])
    values=values[0]

    signoX=np.sign(values[indexref_x])
    signoY=np.sign(values[indexref_y])
    signoZ=np.sign(values[indexref_z])

    #Okey,agora temos os signos e os tempos que necesitamos para filtrar,vamos a empezar co filtrado
    i=0
    FinalValuesVector=[]
    FinalTimesVector=[]
    signoaux="null"
    signo=signoX
    while i < len(values):
        #Facemos esto para traballar sempre con "signo",xa que imos facer o mismo en todos os eixes.
        if signoaux is "x":
            signo=signoY
            signoaux="y"
        elif signoaux is "y":
            signo=signoZ
            signoaux="z"
        else:
            signo=signoX
            signoaux="x"
        k=0
        contador=0
        borrar=0
        while k < 10:
            if contador is constant.DIMENSIONVIBRATION:
                i=i+10-k-borrar
                #temos que engadir 10 en total, enton engadimos 10 - os que usamos para incrementar a posicion-relleno
                break
            else:
                if np.sign(values[i]) == signo:
                    if tempos[i]-tempref_x < constant.TIMELIMIT:
                        FinalValuesVector.append(values[i])
                        FinalTimesVector.append(tempos[i])
                        contador=contador+1
                        k=k+1
                        i=i+1
                    else:
                    #Se non e maior que 0,15 non vai selo nunca.Polo tanto,rellenamos o VectorFinal con ceros
                        borrar=0
                        while borrar < constant.DIMENSIONVIBRATION-contador:
                            FinalTimesVector.append(0)
                            FinalValuesVector.append(0)
                            borrar=borrar+1
                            i=i+1
                        contador=constant.DIMENSIONVIBRATION

                else:
                    if k is 9:#Esto executase se non hai 5 valores que coincidan en signo en todo o array
                        borrar=0
                        k=k+1
                        while borrar < constant.DIMENSIONVIBRATION-contador:
                            FinalTimesVector.append(0)
                            FinalValuesVector.append(0)
                            borrar=borrar+1
                        i = i + 1
                    else:
                        k=k+1
                        i=i+1

    return FinalTimesVector+FinalValuesVector


#AQUI SIMPLEMENTE HABERIA QUE FACER UN REDUCEPOT E XA ESTARIA TODO
def reducepot(tempos,values):
    #A lectura dos acelerómetros e circular,primeiro leese unha meustra do eje X,despois Y,despois Z.Despois cambia
    #a outro acelerómetro.Fai este bucle 10 veces.
    #Como temos ordenados os vectores como MuestrasX,Y,Z--MuestrasX,Y,Z...Con coller o indice do menor valor, xa temos
    #automaticamente o indice do menor de cada eje
    tempos=string2float2D([tempos])
    tempos=tempos[0]
    tempref_x=min(tempos)

    indexref_x=tempos.index(tempref_x)
    valueref_x=int(values[indexref_x])
    indexref_y=indexref_x+10
    tempref_y=tempos[indexref_y]
    valueref_y=int(values[indexref_y])
    indexref_z=indexref_y+10
    tempref_z=tempos[indexref_z]
    valueref_z=int(values[indexref_z])

    values=string2float2D([values])
    values=values[0]

    signoX=np.sign(values[indexref_x])
    signoY=np.sign(values[indexref_y])
    signoZ=np.sign(values[indexref_z])

    #Okey,agora temos os signos e os tempos que necesitamos para filtrar,vamos a empezar co filtrado
    i=0
    FinalValuesVector=[]
    FinalTimesVector=[]
    signoaux="null"
    signo=signoX
    while i < len(values):
        #Facemos esto para traballar sempre con "signo",xa que imos facer o mismo en todos os eixes.
        if signoaux is "x":
            signo=signoY
            valor=valueref_y
            signoaux="y"
        elif signoaux is "y":
            signo=signoZ
            valor=valueref_z
            signoaux="z"
        else:
            signo=signoX
            valor=valueref_x
            signoaux="x"
        k=0
        contador=0
        borrar=0
        while k < 10:
            if contador is constant.DIMENSIONVIBRATION:
                i=i+10-k-borrar
                #temos que engadir 10 en total, enton engadimos 10 - os que usamos para incrementar a posicion-relleno
                break
            else:
                if np.sign(values[i]) == signo and abs(values[i]) >= abs(constant.POTLIMIT*valor):
                        FinalValuesVector.append(values[i])
                        FinalTimesVector.append(tempos[i])
                        contador = contador + 1
                        k = k + 1
                        i = i + 1
                        if k is 10:
                            # Se non e maior que 0,15 non vai selo nunca.Polo tanto,rellenamos o VectorFinal con ceros
                            borrar = 0
                            while borrar < constant.DIMENSIONVIBRATION - contador:
                                FinalTimesVector.append(0)
                                FinalValuesVector.append(0)
                                borrar = borrar + 1
                                #Aqui non incluimos i, xa que significa que acabamos de leer todo o eje
                                #Como k xa chegou a 10, non se executa o bucle do contador
                else:
                    if k is 9:#Esto executase se non hai 5 valores que coincidan en signo en todo o array
                        borrar=0
                        k=k+1
                        while borrar < constant.DIMENSIONVIBRATION-contador:
                            FinalTimesVector.append(0)
                            FinalValuesVector.append(0)
                            borrar=borrar+1
                        i = i + 1
                    else:
                        k=k+1
                        i=i+1

    return FinalTimesVector+FinalValuesVector
