import subprocess , os, time
import pickle
from wol import send_magic_packet

time_sleep = 80


try:
    f = open('res2.txt', 'rb')
    nom_pc = pickle.load(f)
    nom_dns_nas = pickle.load(f)
    lettre_lecteur_nas = pickle.load(f)
    ip_nas = pickle.load(f)
    mac_nas = pickle.load(f)
    autostart_emplacement = pickle.load(f)
    emplacement_a_copie= pickle.load(f)
    f.close()
    reglage_nas_ok = nom_pc and nom_dns_nas and lettre_lecteur_nas and ip_nas and mac_nas and autostart_emplacement and emplacement_a_copie != ""
except:
    reglage_nas_ok = False



"""wol nas"""
if reglage_nas_ok== True:
 send_magic_packet(mac_nas)
 time.sleep(time_sleep)

"""lettre lecteur"""
if reglage_nas_ok== True:
 cmd_supr_lecteur_reseau_nas="net use "+ lettre_lecteur_nas + ": /delete /y"
 cmd_ajout_lecteur_reseau_nas="net use " + lettre_lecteur_nas + ": \\\\" + ip_nas +"\\nas /USER:nas /persistent:yes"
 print (cmd_ajout_lecteur_reseau_nas)
 subprocess.run((cmd_supr_lecteur_reseau_nas))
 subprocess.run((cmd_ajout_lecteur_reseau_nas))


"""copie sur nas du repertoire utilisateu"""
if reglage_nas_ok== True:
 rep_utilpc_nas= emplacement_a_copie
 rep_utilpc_nas =rep_utilpc_nas.split(":")[0] + rep_utilpc_nas.split(":")[1]
 emplacement_destination = lettre_lecteur_nas + ":\\" + nom_pc + "\\" + rep_utilpc_nas

 emplacement_destination_remp = emplacement_destination.replace("/", "\\")
 copy_sur_nas = "mkdir \"" + emplacement_destination_remp + "\""
 os.system((copy_sur_nas))
 copy_sur_nas2 = "cop.exe -s " + "\"" + emplacement_a_copie + "\"" + " -d " + "\"" + emplacement_destination_remp + "\""
 os.system((copy_sur_nas2))

try:
    del autostart
except:
    print ("pas de module")