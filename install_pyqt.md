## PyQt

Pour installer pyQt, on ne peut pas utiliser `pip`.

On utilise la version 5 de qt.

Il faut se rendre à l'adresse [suivante](https://www.riverbankcomputing.com/software/pyqt/download5).

Télécharger les sources ou essayer le binaire sur windows.

##### Mac :

Sous mac, on a besoin d'installer le package `SIP` séparemment. Encore une fois, il faut le faire à partir des sources [ici](https://www.riverbankcomputing.com/software/sip/download)

Ensuite lors de l'installation de qt préciser l'option

	python configure --sip path/to/sip
	
	
Si jamais vous utiliser `virtualenv`, l'installation de qt se fera sur le système, il faut copier le `site-packages` de qt dans celui de `virtualenv`