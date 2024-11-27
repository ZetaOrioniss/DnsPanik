#! /usr/bin/python3
#! coding: utf-8


import sys
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

def help_display():

    print("""
    
Affichage de l'aide:\n\n

Sous-domaines:

    Exécution: python3 dnspanik.py -sub <example.com> </path/to/wordlist.txt>\n--> Énumération de sous-domaine du site example.fr\n\n

Répertoires:

    Exécution: python3 dnspanik.py -dir <https://example.com> </path/to/wordlist.txt>\n--> Énumération des répertoires du site example.fr\n\n

Option(s) Supplémentaire(s):

    -v  |  --verbose        --> active le mode verbeux.

    """)

def custom_parse_args():

    args_lst = ["-v", "--verbose", "-sub", "-dir"]

    if len(sys.argv) > 5:

        print("err: trop d'arguments."); exit(0)

    for args in sys.argv:
        
        if args[0] == "-":

            if args not in args_lst:

                print(f"Argument '{args}' inconnu"); help_display()
                exit(0)
    
    return 0


def subdomain_req(file_path):

    custom_parse_args()

    valid_url_tab = []
    valid_subdomain_tab = []
    

    table = PrettyTable()
    table.field_names = ["Status", "Subdomain", "Url"]

    with open(file_path, "r") as wordlist:

        url = sys.argv[2]

        print("[!] Starting subdomain enumeration...\n[+] target url: {}\n[+] wordlist: {}\n".format(url, file_path))

        for line in wordlist:

            current_subdomain = f"{line[:-1]}.{url}"        # domaine complet en cours de test (sous-domaine.domaine.xx)

            try:

                answer = dns.resolver.resolve(current_subdomain, "A")

                for rdata in answer:

                    if current_subdomain not in valid_url_tab:

                        valid_url_tab.append(current_subdomain)
                        valid_subdomain_tab.append(line)

                        if "-v" or "--verbose" in sys.argv:

                            print(f"{' ' * 5}{green} + {reset} - {green}{line[:-1]}.{url}{reset}")

                            #valid_subdomain_tab.add_row(["200", line[:-1], current_subdomain])

                        table.add_row(["+", line[:-1], current_subdomain])

            except dns.resolver.NoAnswer:

                if "-v" or "--verbose" in sys.argv:

                    #table.add_row(["-", line[:-1], current_subdomain])
                    continue
                    #print(f"{' ' * 5}{yellow} 204 {reset}{ ' ':<8} | {' ' * 5} {line[:-1]:<10} {' ' * 19} | {' ' * 5} {current_subdomain}")

            except dns.resolver.NXDOMAIN:

                if "-v" or "--verbose" in sys.argv:

                    #table.add_row(["-", line[:-1], current_subdomain])
                    continue
                    #print(f"{' ' * 5}{red} 404 {reset}{ ' ':<8} | {' ' * 5} {line[:-1]:<10} {' ' * 19} | {' ' * 5} {current_subdomain}")


            except dns.exception.DNSException as e:

                #print(f"Err : {e}")
                
                continue

    print("Recap:\n\n")
    print(table)

    return 0

def directories_req(file_path):

    custom_parse_args()

    valid_url_tab = []
    valid_dir_tab = []

    table = PrettyTable()
    table.field_names = ["Status code", "Available Directory"]

    with open(file_path, "r") as wordlist:

        url = sys.argv[2]

        print("[!] Starting directory enumeration...\n[+] target url: {}\n[+] wordlist: {}\n".format(url, file_path))

        print("\nResults:\n\n")


        for line in wordlist:

            current_dir = f"{url}/{line[:-1]}"     # domaine complet en cours de test (sous-domaine.domaine.xx)

            try:

                answer = requests.get(current_dir)

                if answer.status_code == 200:

                    if current_dir not in valid_url_tab:

                        valid_url_tab.append(current_dir)
                        valid_dir_tab.append(line)

                        if "-v" or "--verbose" in sys.argv:

                            print(f"{' ' * 5}{green} 200 {reset} - {green}/{line[:-1]}{reset}")

                        table.add_row(["200", line[:-1]])

                else:

                    continue


            except:

                if "-v" or "--verbose" in sys.argv:
                    print(f"{' ' * 5}{yellow} ??? {reset}{ ' ':<8} | {' ' * 5} {line[:-1]:<10} {' ' * 9} | {' ' * 5} {current_dir}")
        
        print("\nRecap:\n\n")
        print(table)

    
    return 0

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

    if "-h" in sys.argv:

        help_display();exit(0)
    
    try:

        filename = [f"{sys.argv[3]}"]

        time_s = time.time()

        if sys.argv[1] == "-sub":

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

                for result in executor.map(subdomain_req, filename):

                    print(result)
            
            total_time = time.time() - time_s

            print( f"{total_time:2f}s" )
        
        if sys.argv[1] == "-dir":

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:

                for result in executor.map(directories_req, filename):

                    print(result)
            
            total_time = time.time() - time_s

            print( f"{total_time:2f}s" )
    
    except KeyboardInterrupt:

        exit(0)

    except FileNotFoundError:

        print("Err: fichier non trouvé.\nPressez Entrer pour continuer...")
        input()
        help_display()
        exit(0)