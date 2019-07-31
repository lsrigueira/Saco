"""AQUI FALTACOLLER SEMPRE O SEL:ATRIB,SOLO SE COLLIA DENTRO DO IF E PETABA AS VECES POR ESO
"""


from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict
#from sklearn.manifold import TSNE
import constant
import time
aux=time.time()
import function
import numpy as np
from sklearn.model_selection import GridSearchCV
import Controlar
import os
#############################################################PROGRAMA PRINCIPAL#############################################################
Time=[]
Value=[]
GolpesClasificados=[]
resposta=123123
hits_database=[[]]
aux=time.time()-aux
sesion=function.iniciar(hits_database)
aux2=time.time()

Controlador=Controlar.Controller()

if sesion is not False:
    GolpesClasificados.extend(function.cargarperfil(sesion))
aux2=time.time()-aux2
print(aux+aux2)

while resposta!=0:
    resposta=function.menu(sesion)

    if int(resposta) is 1:
        abreviatura=function.seleccion_golpe()
        if abreviatura not in GolpesClasificados:
            GolpesClasificados.append(abreviatura)
        interaccion = 0
        forza=[[]]
        tempos=[[]]
        calidade=[]
        repetir = True
        while repetir:
            Controlador.main()
            auxy=function.readJSONS()
            FinalValues=auxy[1]
            FinalTimes=auxy[0]
            if interaccion is 0:
                forza[0]=FinalValues
                tempos[0]=FinalTimes
            else :
                forza.append(FinalValues)
                tempos.append(FinalTimes)
            valido=function.eleccion(function.mostrar_direccions(),len(constant.DIRECCIONS),False)
            calidade.append(constant.DIRECCIONS[int(valido)-1])
            valido=function.eleccion("Desexa seguir clasificando?\n\t1)Si\n\t2)No",2,False)
            if int(valido) is 2:
                repetir = False
            interaccion=interaccion+1
        function.escribirJSON(abreviatura,sesion,tempos=tempos,forza=forza,calidade=calidade)#opens "temporal.json" if there is no sesion
    #forza and calidade are optional values so we need to indicate what "forza" is.Its confusing in this case cause they have the same name

    elif int(resposta) is 123:

        while int(input("1 para pegar,2 para salir")) is not 2:
            Controlador.main()

    elif int(resposta) is 2:
        index_golpe = False     #One index to get the hit from GolpesClasificados(abrev already)
        while index_golpe is False:#index_golpe
            index_golpe=function.elexir_golpes_clasificados(GolpesClasificados,"Atras")#This function return False if an invalid number has been chosen
            #Atras is the message that appears in position "0"
        if int(index_golpe) is -1 or 0:#Function return -1 if the list is empty,0 if they want to go "atras"
            continue#Its a "break" for the "elif"
        hitname=GolpesClasificados[int(index_golpe)-1]#to get the real hit name,(funcion menu starts at 1)
        repetir = True
        while repetir:
           Controlador.main()
           forza=function.readJSONS()[1]
           print(forza)
           clf_prove=function.getfromhits_database(hits_database,hitname,"clf")
           if str(clf_prove) == "NULL":
               print("Non hai rexistro de clasificador para este golpe.Escolla un")
               aux=function.calibrar(sesion,hitname,False)
               clf_real=aux[0]
               sel_atrib=aux[1]
               function.insertinBD(hits_database,hitname,"clf",clf_real)
               function.insertinBD(hits_database,hitname,"sel_atrib",sel_atrib)
           else:
               clf_real=clf_prove
               sel_atrib=function.getfromhits_database(hits_database,hitname,"sel_atrib")
           auxyy=[[]]
           auxyy[0]=forza
           forza=auxyy
           pot=function.potencia(forza[0]) #We have to do it now,with the 135 values
           if "Linear" in str(clf_real):
              forza=sel_atrib.transform(forza)
              forza=function.reshapecasero(forza)
           else:
              #forza=GridSearchCV(clf_real,aux[1]).transform(forza)
              #forza=clf_real.transform(forza)
              #forza=function.reshapecasero(forza)
              print(clf_real.best_estimator_.transform().predict(forza))
           print(len(forza[0]))
           etiqueta=function.getresultado(forza[0],clf_real)[2:-2] #[2:-2]is jsut to deletede "['" and "']" to print

           vectorhitname=function.ultimosgolpes(sesion,hitname)
           vectoretiqueta=function.ultimosgolpes(sesion,hitname,etiqueta)
           historialhitname=function.leerhistorial(hitname[:-4]) #Hitname e nombre_clf,no historial solo gardamos o nome
           historialetiqueta=function.leerhistorial(hitname[:-4],etiqueta)
           mediahitname=function.mediapot(vectorhitname,historialhitname)
           mediaetiqueta=function.mediapot(vectoretiqueta,historialetiqueta)
           print("\n-------------------------Resultados-------------------------")
           print("O golpe con potencia "+str(pot)+" foi "+str(etiqueta))
           print("\t"+str(100*pot/mediahitname)+"% de "+str(hitname[:-4]))
           print("\t"+str(100*pot/mediaetiqueta)+"% de "+str(hitname[:-4])+" "+str(etiqueta))
           valido=function.eleccion("Desexa seguir clasificando?\n\t1)Si\n\t2)No",2,False)
           if int(valido) is 2:
              repetir=False
           function.escribirJSON(str(time.gmtime(time.time())[3]+2)+"-"+str(time.gmtime(time.time())[4]),"historial",string="Nombre:"+hitname[:-4]+"\n\t\t\tPotencia:"+str(pot)+"\n\t\t\tCalificacion:\""+str(etiqueta)+"\"")

    elif int(resposta) is 3:
        function.verhistorial()

    elif int(resposta) is 4:
         FinalValues=function.readJSONS()[1]
         print(FinalValues)

    elif int(resposta) is 5:
        index_golpe = False#One index to get the hit from GolpesClasificados(abrev already)
        while index_golpe is False:#index_golpe
            index_golpe=function.elexir_golpes_clasificados(GolpesClasificados,"Todos")#This function return False if an invalid number has been chosen
        if int(index_golpe) is -1:#Function return -1 if the list is empty
            continue#Its a "break" for the "elif"
        #NOTA,SE PULSAN 0 HAI QUE CALIBRAR TODOS FALTAN POR IMPLEMENTAR ESAS COUSAS
        hitname=GolpesClasificados[int(index_golpe)-1]#to get the real hit name,(funcion menu starts at 1)
        aux=function.calibrar(sesion,hitname,True)
        clf=aux[0]
        sel_atrib=aux[1]
        function.insertinBD(hits_database,hitname,"clf",clf)
        function.insertinBD(hits_database,hitname,"sel_atrib",sel_atrib)

    elif int(resposta) is 6:
        index_golpe=False
        while index_golpe is False:
           index_golpe=function.elexir_golpes_clasificados(GolpesClasificados,"Atras")#This function return False if an invalid number has been chosen
        if int(index_golpe) is -1 or 0:   #Function return -1 if the list is empty,0 if they want to go "atras"
           continue
        hitname=GolpesClasificados[int(index_golpe)-1]#to get the real hit name,(funcion menu starts at 1)
        #function.pintarvectoresTSNE(sesion,hitname)
        sel_atrib=function.getfromhits_database(hits_database,hitname,"sel_atrib")
        if str(sel_atrib) == "NULL":
            print("Non hai clf con transformador para eliminar overfitting")
            print(hits_database)
        else:
            function.pintarvectoresTSNE(sesion,hitname,sel_atrib)

    elif int(resposta) is 7:
        index_golpe = False     #One index to get the hit from GolpesClasificados(abrev already)
        while index_golpe is False:#index_golpe
            index_golpe=function.elexir_golpes_clasificados(GolpesClasificados,"Atras")#This function return False if an invalid number has been chosen
            #Atras is the message that appears in position "0"
        if int(index_golpe) is -1 or 0:#Function return -1 if the list is empty,0 if they want to go "atras"
            continue#Its a "break" for the "elif"
        hitname=GolpesClasificados[int(index_golpe)-1]#to get the real hit name,(funcion menu starts at 1)
        vectorfinal= function.valueandlabels(sesion+".json",hitname,True)
        aux=vectorfinal[0]
        todosvalues=aux[0:int(len(aux)/2)]
        todoslabels=aux[int(len(aux)/2):]
        todostimes=vectorfinal[1]
        i=0
        finaltimes=[[]]
        finalvalues=[[]]
        while i <len(todosvalues):
            if todoslabels[i]=="Derecha":
                todoslabels[i]="Dereita"
            elif todoslabels[i]=="Izquierda":
                todoslabels[i]="Esquerda"
            finalvector=function.reducepot(todostimes[i],todosvalues[i])
            if i is 0:
                finaltimes[0]=finalvector[0:int(len(finalvector)/2)]
                finalvalues[0]=finalvector[int(len(finalvector)/2):]
            else:
                finaltimes.append(finalvector[0:int(len(finalvector)/2)])
                finalvalues.append(finalvector[int(len(finalvector)/2):])
            i=i+1

        function.escribirJSON(hitname,"prueba3",tempos=finaltimes,forza=finalvalues,calidade=todoslabels)

        """aux=function.valueandlabels("prueba3.json",hitname,True)
        auxvect=aux[0]
        values = auxvect[0:int(len(auxvect) / 2)]
        labels = auxvect[int(len(auxvect) / 2):int(len(auxvect))]
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print(values)
        print(labels)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print(aux[1])
        print(len(aux[1]))
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        """
        """AQUI XA TEÑO TODOS OS DATOS QUE NECESITARIA PARA PROCESAR
        
        """
        """ESTO ERA PARA A PRUEBA DE CAMBIAR O MAXIMO VALOR DO EJE
        index_golpe = False
        while index_golpe is False:
            index_golpe = function.elexir_golpes_clasificados(GolpesClasificados,
                                                              "Atras")  # This function return False if an invalid number has been chosen
        if int(index_golpe) is -1 or 0:  # Function return -1 if the list is empty,0 if they want to go "atras"
            continue
        hitname = GolpesClasificados[int(index_golpe) - 1]  # to get the real hit name,(funcion menu starts at 1)
        function.cambiaramaximo(sesion,hitname,"prueba2")
        """
        """Esto era para a miña prueba de contar o signo
        
        NOTA, E SE FACEMOS O DE AHORA PERO CONTANDO TODOS OS SIGNOS?
        
        index_golpe = False
        while index_golpe is False:
            index_golpe = function.elexir_golpes_clasificados(GolpesClasificados,
                                                              "Atras")  # This function return False if an invalid number has been chosen
        if int(index_golpe) is -1 or 0:  # Function return -1 if the list is empty,0 if they want to go "atras"
            continue
        hitname = GolpesClasificados[int(index_golpe) - 1]  # to get the real hit name,(funcion menu starts at 1)
        print("\t1)Contamos o signo das mostras de cada eixe de cada acelerometro e poñemos a 0 as do signo minoritario")
        print("\t2)Contamos o signo das mostras de cada eixe e poñemos a 0 os eixes completos")
        aux=input()
        if int(aux) is 1:
            print("Elexida opcion 1")
            eleccion="muestrascero"
        else:
            print("Elexida opcion 2")
            eleccion="ejecero"
        function.cambiarjsons(sesion,hitname,"prueba1",eleccion)
        """


    elif int(resposta) is 15:#U wont see 15 in menu, but return 15
           sesion=function.iniciosesion()
           GolpesClasificados.extend(function.cargarperfil(sesion))

    elif int(resposta) is 0:
             with open(constant.PATH+"temporal.json",'a') as temporal_file:
                 temporal_file.write("}")
             with open(constant.PATH+"historial.json",'a') as temporal_file:
                 temporal_file.write("}")
             print("PROGRAMA REMATADO CON EXITO")


    else :
        print("Opcion non valida\n")
