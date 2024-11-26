#! /usr/bin/python3
#! coding: utf-8


import sys
import dns.resolver
import requests
import concurrent.futures
import time
import colorama


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

    -v          --> active le mode verbeux.

    """)

def custom_parse_args():

    args_lst = ["-w", "-v", "-u", "--url", "-sub", "-dir"]

    if len(sys.argv) > 5:

        print("err: trop d'arguments."); exit(0)

    for args in sys.argv:
        
        if args[0] == "-":

            if args not in args_lst:

                print(f"Argument '{args}' inconnu"); help_display()
                exit(0)


def subdomain_req(file_path):

    custom_parse_args()

    valid_url_tab = []
    valid_subdomain_tab = []

    with open(file_path, "r") as wordlist:

        url = sys.argv[2]

        print("_" * 65)
        print(f"{' ' * 5} Status {' ' * 5} | {' ' * 5} Subdomain {' ' * 10} | {' ' * 5} Url")
        print("_" * 65)


        for line in wordlist:

            current_subdomain = f"{line[:-1]}.{url}"        # domaine complet en cours de test (sous-domaine.domaine.xx)

            try:

                answer = dns.resolver.resolve(current_subdomain, "A")

                for rdata in answer:

                    if current_subdomain not in valid_url_tab:

                        valid_url_tab.append(current_subdomain)
                        valid_subdomain_tab.append(line)

                        if "-v" in sys.argv:

                            print(f"{' ' * 5}{green} 200 {reset}{ ' ':<8} | {' ' * 5} {green}{line[:-1]:<10}{reset} {' ' * 19} | {' ' * 5} {current_subdomain}")


            except dns.resolver.NoAnswer:

                if "-v" in sys.argv:
                    print(f"{' ' * 5}{yellow} 204 {reset}{ ' ':<8} | {' ' * 5} {line[:-1]:<10} {' ' * 19} | {' ' * 5} {current_subdomain}")

            except dns.resolver.NXDOMAIN:

                if "-v" in sys.argv:
                    print(f"{' ' * 5}{red} 404 {reset}{ ' ':<8} | {' ' * 5} {line[:-1]:<10} {' ' * 19} | {' ' * 5} {current_subdomain}")


            except dns.exception.DNSException as e:

                #print(f"Err : {e}")
                
                continue

    j = 0

    if valid_url_tab == 0:

        print("0 subdomain available")

    else:

        for i in valid_url_tab:

            print(f"{' ' * 5}{green} 200 {reset}{ ' ':<8} | {' ' * 5} {valid_subdomain_tab[j][:-1]:<10} {' ' * 10} | {' ' * 5} {i}")

            j += 1
    
    return 0

def directories_req(file_path):

    custom_parse_args()

    valid_url_tab = []
    valid_dir_tab = []

    with open(file_path, "r") as wordlist:

        url = sys.argv[2]

        print("_" * 65)
        print(f"{' ' * 5} Status {' ' * 5} | {' ' * 5} Directory {' ' * 10} | {' ' * 5} Url")
        print("_" * 65)


        for line in wordlist:

            current_dir = f"{url}/{line[:-1]}"     # domaine complet en cours de test (sous-domaine.domaine.xx)

            #try:

            answer = requests.get(current_dir)

            if answer.status_code == 200:

                if current_dir not in valid_url_tab:

                    valid_url_tab.append(current_dir)
                    valid_dir_tab.append(line)

                    #print(f"{' ' * 5}{green} 200 {reset}{ ' ':<8} | {' ' * 5} {green}{line[:-1]:<10}{reset} {' ' * 9} | {' ' * 5} {current_dir}")

            else:

                if "-v" in sys.argv:

                    print(f"{' ' * 5}{yellow} {answer.status_code} {reset}{ ' ':<8} | {' ' * 5} {green}{line[:-1]:<10}{reset} {' ' * 9} | {' ' * 5} {current_dir}")


            # except:

            #     if "-v" in sys.argv:
            #         print(f"{' ' * 5}{yellow} ??? {reset}{ ' ':<8} | {' ' * 5} {line[:-1]:<10} {' ' * 9} | {' ' * 5} {current_dir}")

    j = 0

    if len(valid_url_tab) == 0:

        print("0 directory available")

    else:

        for i in valid_url_tab:

            print(f"{' ' * 5}{green} 200 {reset}{ ' ':<8} | {' ' * 5} {green}{valid_dir_tab[j][:-1]:<10} {reset}{' ' * 10} | {' ' * 5} {i}")

            j += 1
    
    return 0

if __name__ == "__main__":
    
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
