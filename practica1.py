#!/usr/bin/python


import webapp
import csv
import urllib
import os


class AcortaUrlsApp (webapp.webApp):
    """Simple web application for managing content.
    Content is stored in a dictionary, which is intialized
    with the web content."""

    # Declare and initialize content
    contador = -1
    urls_reales = {}
    urls_acortadas = {}

    def parse(self, request):
        """Return the resource name (including /)"""

        """ Lo que hace parse es : del chorizo de peticion que tengo, cojo
        solamente las cosas que me interesan"""

        print request

        """ Antes como solo teniamos GET, solo nos importaba el recurso por lo
        que solo devolviamos el recurso; ahora, tenemos GET y tenemos PUT, por
        lo tanto tenemos que tener en cuenta metodo, recurso y cuerpo. Ahora la
        peticion me devolvera una tupla con estos tres campos"""

        metodo = request.split(' ', 2)[0] #me guardo el put o el get
        try:
        		recurso = request.split(' ', 2)[1] #me guardo el /algo
        except IndexError:
            recurso = ""
        try:
            cuerpo = request.split('\r\n\r\n')[1][4:] #me guardo el cuerpo, que en el post sera la qs
        except IndexError:
            cuerpo = ""
        
        print "El metodo es: " + metodo
        print "El recurso es: " + recurso
        print "El cuerpo es: " + cuerpo
        return metodo, recurso, cuerpo

    def process(self, peticion):
        """Process the relevant elements of the request.
        Finds the HTML text corresponding to the resource name,
        ignoring requests for resources not in the dictionary.
        """
        metodo, recurso, cuerpo = peticion
        try:
        		variable = int(recurso[1:])
        except ValueError:
        		variable = ""
        if metodo == "GET":
            if recurso =='/':
            
            	# solo voy al csv si el diccionario esta vacio y si el fichero existe!
            	if len(self.urls_reales) == 0:
            		if os.access("urls.csv", 0):
				      	with open("urls.csv", "r") as fd:
				      		reader = csv.reader(fd)
				      		vacio = True
				      		for row in reader:
				      			vacio = False
				      		if not vacio: #si no esta vacio tengo que pasar el csv al diccionario
				      			self.csvAdicc("urls.csv")
            
                httpCode = "200 OK"
                htmlBody = "<html><body>" \
                            + '<form method="POST" action="">' \
                            + 'URL: <input type="text" name="Url"><br>' \
                            + '<input type="submit" value="Enviar">' \
                            + '</form>' \
                            + "<body></html>"
            elif variable in self.urls_acortadas:
            	url_real = self.urls_acortadas[int(recurso[1:])]
            	url_acortada = self.urls_reales[url_real]
            	#tengo que redirigir
            	httpCode = "302 Found"
            	htmlBody = "<html><head>" + '<meta http-equiv="refresh" content="0;url=' + url_real + '" />' + "</head></html>"
            else:
                httpCode = "404 Not Found"
                htmlBody = "Recurso no disponible"
        
        elif metodo == "POST":
        		if len(cuerpo) == 0:
        			httpCode = "405 Method Not Allowed"
        			htmlBody = "Go Away!"
        		elif len(cuerpo) != 0:
		     		if urllib.unquote(cuerpo[0:13]) == "http://":
		     			url_real = "http://" + cuerpo[13:]
		     		elif urllib.unquote(cuerpo[0:14]) == "https://":
		     			url_real = "https://" + cuerpo[14:]
		     		else:
		     			url_real = "http://" + cuerpo
		     		
		     		if url_real in self.urls_reales: # quiere decir que ya ha sido acortada, busco su valor en el diccionario
		     			print url_real + "SI ESTA EN URLS_REALES!!!"
		     			url_acortada = self.urls_reales[url_real]
		     		else: # si no esta en el diccionario significa que es nueva, la tengo que acortar y meterla al dicc
		     			self.contador = self.contador + 1
		     			url_acortada = self.contador
		     			self.urls_reales[url_real] = url_acortada
		     			self.urls_acortadas[self.contador] = url_real
		     			self.diccAcsv(self.urls_acortadas)
		     			
		     		httpCode = "200 OK"
		     		htmlBody = "<html><body>" + '<p><a href="' + str(url_acortada) + '">Esta es tu url acortada</a></p>' \
		     						+ '<p><a href=' + url_real + '/>' \
		     						+ 'Esta es tu url real</a></p>' \
		     						+ "</body><html>"
        else:
            httpCode = "405 Method Not Allowed"
            htmlBody = "Go Away!"

        return (httpCode, htmlBody)
        
    def diccAcsv(self, diccionario):
			#esta funcion pasa un diccionario a formato CSV
			# esto seria mas facil hacerlo con append, porque no hace falta volcar siempre el diccionario
			# en el CSV, con poner cada nueva entrada vale. Con apend lo que hago es no borrar lo que tengo antes, no reescribo
			with open("urls.csv", "w") as fd:
				escribir = csv.writer(fd)
				for url in diccionario:
					key = url
					valor = diccionario[key]
					escribir.writerow([key] + [valor])
			return None
			
    def csvAdicc(self, fichero):
    		with open(fichero, "r") as fd:
		 		leido = csv.reader(fd)
		 		for row in leido:
		 			key = int(row[0]) # es el numero, la url acortada
		 			if self.contador < key:
		 				self.contador = key
		 			valor = row[1] #es la url real
		 			self.urls_acortadas[key] = valor
		 			self.urls_reales[valor] = key

         	
        	


if __name__ == "__main__":
    testWebApp = AcortaUrlsApp("localhost", 1235)
