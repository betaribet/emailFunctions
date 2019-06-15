# -*- coding: utf-8 -*-
import lqConnectMail

user = "giden0106@gmail.com"
password = "Gitmesigerekenmail"
mailbox = "INBOX"
toaddr = "mailgelen1@gmail.com"
y = lqConnectMail.lqConnectGmail(toaddr, "Gmail123","y.txt")

x = lqConnectMail.lqConnectGmail(user, password, "x.txt")

            #lqConnectMail.lqConnectGmail.connection(x)

lqConnectMail.lqConnectGmail.connection(y)
lqConnectMail.lqConnectGmail.readMail(y)
#lqConnectMail.lqConnectGmail.sendNewMail(x,toaddr,"ofdkglhja","dfgkjflhşnnkp")

            #lqConnectMail.lqConnectGmail.readMail(x)

            #a,b=lqConnectMail.lqConnectGmail.controlAllMessages(x)
            #print (a,b)

#lqConnectMail.lqConnectGmail.deleteMail(y,"1")
#lqConnectMail.lqConnectGmail.forwardMail(y,'3',user,"bu da benim body",["/home/files/1014-en-sevimli-kedi-fotograflari_f.jpg"])
#lqConnectMail.lqConnectGmail.deleteMail(y,'15')
#lqConnectMail.lqConnectGmail.forwardMail(y,'22',user)

            #c=lqConnectMail.lqConnectGmail.search(x,"Subject : merhaba")
            #print (c)
#print lqConnectMail.lqConnectGmail.getMail(x,'133')
             #lqConnectMail.lqConnectGmail.replyMail(x,'145',"tamam oldu bence mis",["/home/files/1014-en-sevimli-kedi-fotograflari_f.jpg","/home/files/15965087_721063588046768_5685996268478186003_n.jpg"])

