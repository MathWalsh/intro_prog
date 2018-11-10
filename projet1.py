""" Extraire des valeurs historiques pour des symboles boursiers données"""
import json
import argparse
from datetime import date as dt
from datetime import timedelta
import requests


def main():
    """Fonction permettant de créer les arguments et de output les valeurs désirées"""

    parser = argparse.ArgumentParser(
        description="Extraction de valeurs historiques pour un symbole boursier"
    )
    parser.add_argument('symboles',
                        metavar='symbole',
                        nargs='+',
                        help="Nom du symbole boursier désiré"
                       )
    parser.add_argument('-d', '--debut',
                        metavar='DATE',
                        dest='debut',
                        default=None,
                        help="Date recherchée la plus ancienne (format: AAAA-MM-JJ)"
                       )
    parser.add_argument('-f', '--fin',
                        metavar='DATE',
                        dest='fin',
                        default=str(dt.today()),
                        help="Date recherchée la plus récente (format: AAAA-MM-JJ)"
                       )
    parser.add_argument('-v', '--valeur',
                        metavar='{fermeture,ouverture,min,max,volume}',
                        dest='valeur',
                        default='fermeture',
                        choices=['fermeture', 'ouverture', 'min', 'max', 'volume'],
                        help="La valeur désirée (par défaut: fermeture)"
                       )
    return parser.parse_args()

class Data:
    """Classe contenant les méthodes reliées aux dates et aux valeurs."""

    def __init__(self, argument):
        """Assigne l'argument à self.data"""

        self.data = argument

    def __str__(self):
        """Retourne self sous-forme de string"""

        return self

    def verif_valeurs(self):
        """ Modification de la valeur pour pouvoir l'utiliser plus tard."""

        if self.data == 'fermeture':
            self.data = '4. close'
        elif self.data == 'ouverture':
            self.data = '1. open'
        elif self == 'min':
            self.data = '3. low'
        elif self.data == 'max':
            self.data = '2. high'
        elif self.data == 'volume':
            self.data = '5. volume'
        return self.data

    def changer_type_date(self):
        """Changer du type string au type date."""

        if self.data is None:
            self.data = main().fin
        datesplit = self.data.split('-')
        return dt(int(datesplit[0]), int(datesplit[1]), int(datesplit[2]))

    def outputsize_verif(self):
        """Déterminer le outpusize : 'compact' ou 'full'."""

        diff_jours = int((dt.today() - self.data).total_seconds() // 86400)
        if diff_jours > 100:
            output_size = 'full'
        else:
            output_size = 'compact'
        return output_size

    def appelle_alphavantage(self, out):
        """Aller chercher le dictionnaire contenant les valeurs recherchées."""

        url = 'https://www.alphavantage.co/query'
        fonction = 'TIME_SERIES_DAILY'
        apikey = 'Z34X48086NTLRLKF'
        params = {'function': fonction,
                  'symbol': self.data,
                  'apikey': apikey,
                  'outputsize': out
                 }
        reponse = requests.get(url=url, params=params)
        reponse = json.loads(reponse.content)
        return reponse

def obtenir_valeur(date1, date2, rep, val):
    """Mettre les valeurs demandées dans une liste de tuples."""
    liste_des_tuples = []
    while date1 <= date2:
        try:
            couple_tuple = (str(date1), rep['Time Series (Daily)'][str(date1)][val])
            liste_des_tuples.append(couple_tuple)
        except KeyError:
            pass
        finally:
            date1 += timedelta(days=1)
    if not liste_des_tuples:
        print("Il n'y a aucune valeur pour cet intervalle de dates")
    else:
        print(liste_des_tuples)

def output():
    """Output les valeurs désirées"""
    valeur = Data(main().valeur).verif_valeurs()
    datedebut = Data(main().debut).changer_type_date()
    datefin = Data(main().fin).changer_type_date()
    outputsize = Data(datefin).outputsize_verif()
    for i in main().symboles:
        response = Data(i.lower()).appelle_alphavantage(outputsize)
        print(i.lower() + '({}, {}, {})'.format(main().valeur, str(datedebut), str(datefin)))
        obtenir_valeur(datedebut, datefin, response, valeur)

if __name__ == '__main__':
    output()
