import urllib.request
from html_table_parser import HTMLTableParser
from time import gmtime, strftime
from private import domain, target_file
import sys

# requires:
# python3
# html-table-parser-python3 from
# https://github.com/schmijos/html-table-parser-python3


#####################################################################################################################
# Update settings:
target = 'https://ethercalc.org/'+target_file
field_namen = ['schifahren','Email', 'Telefon', 'Adresse', 'Funktion', 'Arbeitskreise', 'Geburtsdatum', 'Schuleintritt', 'Klasse', 'Pinnwand']
klassen_namen = ['hallo', 'kiga']
nur_schule_klassen_namen = ['hallo']
ak_namen = ['haushof', 'finanz', 'kommunikation', 'projekt', 'veranstaltung', 'koordination']
#####################################################################################################################
lehrer_team_emails = []
kindergarten_team_emails = []
pinnwand_emails = []
ak_emails = {}
kids = {}
now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
smiley = " : )"
schifahren_emails = []

# get website content
#print(target)

req = urllib.request.Request(url=target)
f = urllib.request.urlopen(req)
xhtml = f.read().decode('utf-8')

#print(xhtml)

# offline testing
#f=open(target_file)
#xhtml = f.read()
#f.close()


# instantiate the parser and feed it
p = HTMLTableParser()
p.feed(xhtml)

all=p.tables
families=[]
entry=[]
for line in all[0]:
    if(line[0]=='Name'):
        # another entry
        families.append(entry)
        entry=[line]
    else:
        entry.append(line)

people=[]
for family in families[1:]:
    d={}
    for line in family:
        if line[0]!='':
            d[line[0]]=line[1:]

    column=1
    for n in (d['Name'][1:]):
        if n!='':
            person={}
            try:
                person['Familiename']=d['Name'][0]
                # use uniq for same family name of different families (!)
                person['Familienameuniq']=d['Name'][0]+'-'+d['Name'][1]
            except KeyError:
                person['Familiename']=''
            person['Name']=n
            for field in field_namen:
                try:
                    person[field]=(d[field][column])
                except KeyError:
                    person[field]=''
            people.append(person)
        column+=1

###############

ungueltig=0

print("START")
for p in people:
    email=p["Email"]
    email_split=email.split('@')
    if((email != "") and (len(email_split)>1)):
        print(email)
    else:
        print("!!!! Üngültige Email Gefunden = " + email)
        ungueltig+=1

print("Total: "+str(ungueltig))

print("END")


sys.exit(0)

# Lehrer
for p in people:
    if p['Funktion']!='' and p['Funktion'].lower().find('lehrer') >= 0:
        lehrer_team_emails.append(p['Email'])
    if p['Funktion']!='' and p['Funktion'].lower().find('kindergarten') >= 0:
        kindergarten_team_emails.append(p['Email'])
lehrer_team_emails=list(set(lehrer_team_emails))
kindergarten_team_emails=list(set(kindergarten_team_emails))

# kids per class
for klasse in klassen_namen:
    kids[klasse]=[]
    for p in people:
        if not (p['Klasse'].lower() in klassen_namen):
            assert('Wrong class name:'+p['Klasse'])
        if p['Klasse'].lower()==klasse:
            kids[klasse].append(p)

# Pinnwand
for p in people:
    if p['Pinnwand']!='' and p['Pinnwand'].lower()=='ja':
        pinnwand_emails.append(p['Email'])
pinnwand_emails=list(set(pinnwand_emails))

# schifahren
for p in people:
    if p['schifahren']!='' and p['schifahren'].lower()=='ja':
        schifahren_emails.append(p['Email'])
schifahren_emails=list(set(schifahren_emails))


klassen_familiename={}
klassen_familienameset={}
klassen_emails={}
for klasse in klassen_namen:
    klassen_familiename[klasse]=[]
    klassen_emails[klasse]=[]

    # families per class
    for k in kids[klasse]:
        klassen_familiename[klasse].append(k['Familienameuniq'])
    klassen_familienameset[klasse]=set(klassen_familiename[klasse])

    # emails per class
    for p in people:
        if p['Email']!='':
            if klassen_familienameset[klasse].issuperset({p['Familienameuniq']}):
                klassen_emails[klasse].append(p['Email'])

# emails per ak
for ak in ak_namen:
    ak_emails[ak]=[]

    for p in people:
        if p['Email']!= '' and p['Arbeitskreise'].lower().find(ak.lower()) >= 0:
            ak_emails[ak].append(p['Email'])

# emails of parents
eltern_emails=[]
for klasse in nur_schule_klassen_namen:
    for email in klassen_emails[klasse]:
        eltern_emails.append(email)

# special request to add kiga team to kigaeltern list
klassen_emails['kiga']+=kindergarten_team_emails

lehrer_team_emails_set=set(lehrer_team_emails)
gesamtteam_emails_set=set(lehrer_team_emails + kindergarten_team_emails)
eltern_emails_set=set(eltern_emails + lehrer_team_emails + kindergarten_team_emails)
alle_emails_set=set(eltern_emails + klassen_emails['kiga'] + list(gesamtteam_emails_set))

#### print

print('# Kolibri Klassen autogenerated on '+now +smiley)
for klasse in klassen_namen:
    print(klasse.lower()+'eltern@'+domain+' ', end='')
    for e in sorted(set(klassen_emails[klasse])):
        print(e+' ',end='')
    print();print()

print('# Kolibri Eltern autogenerated on '+now +smiley)
print('eltern@'+domain+' ',end='')
for e in sorted(eltern_emails_set):
    print(e+' ',end='')
print();print()

print('# Alle autogenerated on '+now +smiley)
print('alle@'+domain+' ',end='')
for e in sorted(alle_emails_set):
    print(e+' ',end='')
print();print()

print('# Kolibri teams autogenerated on '+now +smiley)
print('team@'+domain+' ',end='')
for e in sorted(lehrer_team_emails_set):
    print(e+' ',end='')
print()
print('gesamtteam@'+domain+' ',end='')
for e in sorted(gesamtteam_emails_set):
    print(e+' ',end='')
print();print()

print('# Kolibri Arbeitskreise autogenerated on '+now +smiley)
for ak in ak_namen:
    print(ak.lower()+'@'+domain+' ', end='')
    for e in sorted(ak_emails[ak]):
        print(e+' ',end='')
    print()
print()

print('# Kolibri Pinnwand autogenerated on '+now +smiley)
print('pinnwand@'+domain+' ', end='')
for e in sorted(pinnwand_emails):
    print(e+' ',end='')
print();print()

print('#ichmagschifahren ' +smiley)
print('schifahren@'+domain+' ', end='')
for e in sorted(schifahren_emails):
    print(e+' ',end='')
print();print()

print('# Kolibri local emails autogenerated on '+now +smiley)
for e in sorted(alle_emails_set):
    email_split=e.split('@')
    if (len(email_split)<2):
        print("TADAM")
    else:
        if email_split[1]=='gmx.at' or email_split[1]=='gmx.net':
            print(email_split[0]+'@'+domain+' '+e)
print()

