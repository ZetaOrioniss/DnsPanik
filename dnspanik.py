#! /usr/bin/python3
#! coding: utf-8


import sys
import os
import sqlite3
import dns.resolver
import requests
import concurrent.futures
import time
import colorama
from prettytable import PrettyTable

green = colorama.Fore.GREEN
red = colorama.Fore.RED
yellow = colorama.Fore.YELLOW
reset = colorama.Fore.RESET


db_file = "default.db"



def db_exists(database):

    if os.path.exists(database):

        print("[+] Database founded !")

    else:

        print("[!] Absent database. Creating one...\n")

        #try:

        with sqlite3.connect(database) as db:

            cursor = db.cursor()

            create_tables = [
                
                """CREATE TABLE domain (

                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    domain_url VARCHAR(50) UNIQUE, 
                    d_state VARCHAR(5), 
                    scan_type VARCHAR(3));""",

                """CREATE TABLE subdomain (

                    id_domain INTEGER, 
                    id_subdomain INTEGER PRIMARY KEY AUTOINCREMENT, 
                    subdomain VARCHAR(20) UNIQUE, 
                    subdomain_state VARCHAR(5), 
                    FOREIGN KEY (id_domain) REFERENCES domain(id));""",

                """CREATE TABLE directory (
                
                    id_domain INTEGER,
                    id_directory INTEGER PRIMARY KEY AUTOINCREMENT,
                    directory VARCHAR(15) UNIQUE,
                    dir_state VARCHAR(5),
                    FOREIGN KEY (id_domain) REFERENCES domain(id));"""
            
                ]

            for sql_request in create_tables:

                cursor.execute(sql_request)

        # except:

        #     print("Err: an error occured when creating database\n"); exit(0)

def table_reading(database, table, id_domain):

    with sqlite3.connect(database) as db:

        cursor = db.cursor()

        if table == "dir":

            cursor.execute(f"SELECT directory FROM directory WHERE id_domain='{id_domain}';").fetchall()

            input("")

        if table == "sub":

            req = cursor.execute(f"SELECT subdomain FROM subdomain WHERE id_domain='{id_domain}';")

            print(req.fetchall())

            input("")



def unicity_verif(database, domain, table, id_domain):

    with sqlite3.connect(database) as db:

        cursor = db.cursor()

        sql_req = f"SELECT domain_url FROM domain WHERE domain_url = '{domain}';"

        req_rslt = cursor.execute(sql_req)

        if req_rslt.fetchone():

            print("[!] Data found for the same domain.\nReading table...\n")

            table_reading(db_file, table, id_domain)

            enum_continue = input("\nContinue enumeration with current wordlist ? y/n: ")

            if enum_continue == "y":
                
                pass

            elif enum_continue == "n":

                exit(0)

            else:

                print("Err: unknown choice '{}'".format(enum_continue))
                exit(0)
        else:
            pass

def insert_domain(database, url_domain, domain_state, scan_type):

    try:

        with sqlite3.connect(database) as db:

            cursor = db.cursor()

            data = [

                (url_domain, domain_state, scan_type)

            ]

            cursor.executemany("INSERT INTO domain (domain_url, d_state, scan_type) VALUES (?, ?, ?)", data)

    except sqlite3.IntegrityError:

        #domaine deja existant dans la table. On ne l'ajoute pas.
        pass


def insert_subdomain(database, sub_state, subdomain, url):

    try:

        with sqlite3.connect(database) as db:

            cursor = db.cursor()

            sql_id_domain = f"SELECT id from domain WHERE domain_url='{url}';"

            result_sql_id = cursor.execute(sql_id_domain).fetchone()[0]

            data = [

                (result_sql_id, subdomain, sub_state)

            ]

            cursor.executemany("INSERT INTO subdomain (id_domain, subdomain, subdomain_state)  VALUES (?, ?, ?)", data)

    except sqlite3.IntegrityError:

        pass

def insert_directories(database, url, directory, dir_state):

    try:

        with sqlite3.connect(database) as db:

            cursor = db.cursor()

            sql_id_domain = f"SELECT id from domain WHERE domain_url='{url}';"

            result_sql_id = cursor.execute(sql_id_domain).fetchone()[0]

            data = [

                (result_sql_id, directory, dir_state)

            ]

            cursor.executemany("INSERT INTO directory (id_domain, directory, dir_state )  VALUES (?, ?, ?)", data)

    except sqlite3.IntegrityError:

        pass



def custom_parse_args():

    # Vérifie si les arguments en ligne de commande sont corrects et valides.
    # Affiche un message d'erreur si un argument est inconnu ou s'il y a trop d'arguments.

    args_lst = ["-v", "--verbose", "--sub", "--dir", "-d", "-s", "-h", "--help", "--delete"]

    if len(sys.argv) > 5:           # Le programme attend au maximum 4 arguments. On écrit 5 car le lanceur compte comme 0.

        print("err: too many args."); exit(0)

    for args in sys.argv:
        
        if args[0] == "-":

            if args not in args_lst:

                print(f"Unknown '{args}' args"); help_display()
                exit(0)
    
    return 0


def valid_url_verif(url):

    # Cette fonction valide que le domaine fourni est accessible. Si ce n'est pas le cas, elle affiche un message d'erreur et arrête le script.

    try:

        req = dns.resolver.resolve(url)

        return "alive"

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):

        print("err: invalid url '{}'".format(url))
        exit(0)

def line_counter(file):

    maxlines = 0

    with open(file, "r") as file:

        for line in file:

            maxlines += 1
    
    return maxlines

def subdomain_req(file_path):                           # Fonction d'énumération de sous-domaines


    custom_parse_args()

    url = sys.argv[2]
    domain_state = valid_url_verif(url)
    valid_url_tab = []
    valid_subdomain_tab = []
    

    table = PrettyTable()
    table.field_names = ["Status", "Subdomain", "Url"]

    with open(file_path, "r") as wordlist:              # Ouvre le fichier spécifié par l'utilisateur en mode lecture

        valid_url_verif(url)

        print("[!] Starting subdomain enumeration...\n[+] target url: {}\n[+] wordlist: {}\n".format(url, file_path))

        insert_domain(db_file, url, domain_state, "sub")
        

        for line in wordlist:                           # On effectue un traitement avec chaque ligne du fichier une par une

            current_subdomain = f"{line[:-1]}.{url}"        # domaine complet en cours de test (sous-domaine.domaine.xx)


            try:

                answer = dns.resolver.resolve(current_subdomain, "A")           # si la requette fonctionne on continue

                for rdata in answer:

                    if current_subdomain not in valid_url_tab:                  # si le sous domaine testé n'est pas dans le tableau des sous domaines valides, on l'inscrit.

                        valid_url_tab.append(current_subdomain)
                        valid_subdomain_tab.append(line)
                        insert_subdomain(db_file, "alive", line[:-1], sys.argv[2])
                        if "-v" in sys.argv or "--verbose" in sys.argv:          # si le mode verbeux est voulu, on affiche chaque résultat pertinent

                            print(f"{' ' * 5}{green} + {reset} - {green}{line[:-1]}.{url}{reset}")


                        table.add_row(["+", line[:-1], current_subdomain])        # on inscrit les resultats dans le tableau d'affichage récapitulatif

            except dns.resolver.NoAnswer:                                         # gestion des erreurs
            

                if "-v" or "--verbose" in sys.argv:

                    continue

            except dns.resolver.NXDOMAIN:

                if "-v" or "--verbose" in sys.argv:

                    continue

            except dns.exception.DNSException as e:
                
                continue

            except KeyboardInterrupt:

                break

    print("Recap:\n\n")
    print(table)

    return 0

def directories_req(file_path):                         # Fonction d'énumération des répertoires d'un domaine

    custom_parse_args()
   
    url = sys.argv[2]
    valid_url_tab = []
    valid_dir_tab = []

    table = PrettyTable()
    table.field_names = ["Status code", "Available Directory"]

    with open(file_path, "r") as wordlist:               # Ouverture du fichier spécifié par l'utilisateur en mode lecture

        insert_domain(db_file, url, "alive", "dir")

        print("[!] Starting directory enumeration...\n[+] target url: {}\n[+] wordlist: {}\n".format(url, file_path))

        print("\nResults:\n\n")


        for line in wordlist:                             # Début du traitement ligne par ligne

            current_dir = f"{url}/{line[:-1]}"     # domaine complet en cours de test (sous-domaine.domaine.xx)

            try:

                answer = requests.get(current_dir)          # Envoie de la requete http

                if answer.status_code == 200:               # Si le domaine répond ok, on continue

                    if current_dir not in valid_url_tab:      # Si le répertoire en cours de test est valide et n'est pas dans le tableau des valides, on l'inscrit

                        insert_directories(db_file, url, line[:-1], "alive")

                        valid_url_tab.append(current_dir)
                        valid_dir_tab.append(line)

                        if "-v" or "--verbose" in sys.argv: # gestion du mode verbeux

                            print(f"{' ' * 5}{green} + {reset} - {green}/{line[:-1]}{reset}")

                        table.add_row(["+", line[:-1]])       # inscription dans le tableau récapitulatif

                else:

                    continue
            
            except requests.exceptions.MissingSchema as e:      # gestion des erreurs

                print(f"Err: url missing schema.\nVoulez-vous dire 'http://www.{url}' ?")
                exit(0)

            except (requests.exceptions.ConnectionError):

                print(f"Err: Can't connect to '{url}'\nPlease verify url.\n")
                exit(0)

        
        print("\nRecap:\n\n")
        print(table)

    
    return 0



def help_display():   
    
    #Une fonction dédiée à afficher un guide pour l'utilisateur, expliquant les options et leur utilisation. Cette fonction est invoquée si l'argument -h est fourni.

    print("""
===== Help for DnsPanik =====
\n
    python3 dnspanik.py [option] <target> </path/to/wordlist.txt>

Main commands:

--sub List of subdomains of a site.
        Example: python3 dnspanik.py --sub example.com /path/to/wordlist.txt
        --> Create subdomain enumeration for "example.com"

--dir Enumeration of a site's directories.
        Example: python3 dnspanik.py --dir https://example.com /path/to/wordlist.txt
        --> Carry out the directory enumeration for "example.com"

Additional option(s):

-v, --verbose Enables verbose mode to display additional details at runtime.

--delete Delete the current database.

Complete example:

    python3 dnspanik.py --sub example.com /path/to/wordlist.txt -v
    --> Perform an enumeration of subdomains with detailed display.


======================================
    """)

if __name__ == "__main__":

    print("""
    
▓█████▄  ███▄    █   ██████  ██▓███   ▄▄▄       ███▄    █  ██▓ ██ ▄█▀
▒██▀ ██▌ ██ ▀█   █ ▒██    ▒ ▓██░  ██▒▒████▄     ██ ▀█   █ ▓██▒ ██▄█▒ 
░██   █▌▓██  ▀█ ██▒░ ▓██▄   ▓██░ ██▓▒▒██  ▀█▄  ▓██  ▀█ ██▒▒██▒▓███▄░ 
░▓█▄   ▌▓██▒  ▐▌██▒  ▒   ██▒▒██▄█▓▒ ▒░██▄▄▄▄██ ▓██▒  ▐▌██▒░██░▓██ █▄ 
░▒████▓ ▒██░   ▓██░▒██████▒▒▒██▒ ░  ░ ▓█   ▓██▒▒██░   ▓██░░██░▒██▒ █▄
 ▒▒▓  ▒ ░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░ ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░▓  ▒ ▒▒ ▓▒
 ░ ▒  ▒ ░ ░░   ░ ▒░░ ░▒  ░ ░░▒ ░       ▒   ▒▒ ░░ ░░   ░ ▒░ ▒ ░░ ░▒ ▒░
 ░ ░  ░    ░   ░ ░ ░  ░  ░  ░░         ░   ▒      ░   ░ ░  ▒ ░░ ░░ ░ 
   ░             ░       ░                 ░  ░         ░  ░  ░  ░   
 ░                                                                   
    
    """)

    try:

    
        if len(sys.argv) < 2:

            help_display();exit(0)

        if "-h" in sys.argv or "--help" in sys.argv:

            help_display();exit(0)

        if "--delete" in sys.argv:

            os.remove(db_file)
            print("[!] Database successfully removed.\n")
            exit(0)

        

        db_exists(db_file)
        
        filename = [f"{sys.argv[3]}"]

        time_s = time.time()

        if sys.argv[1] == "--sub":

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

                for result in executor.map(subdomain_req, filename):

                    print(result)
            
            total_time = time.time() - time_s

            print( f"{total_time:2f}s" )
        
        if sys.argv[1] == "--dir":

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:

                for result in executor.map(directories_req, filename):

                    print(result)
            
            total_time = time.time() - time_s

            print( f"{total_time:2f}s" )
        
    except KeyboardInterrupt:

        exit(0)

    except FileNotFoundError:

        print("Err: File not found.\nPress Enter to continue...")
        input()
        help_display()
        exit(0)
    except IndexError:

        print("Execution command order not respected"); help_display(); exit(0)
