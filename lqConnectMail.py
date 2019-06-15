#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
import re
import email
import smtplib
import imaplib
from email.mime.message import MIMEMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders, header
from email.utils import formatdate


class lqConnectGmail:
    imap_url = 'imap.gmail.com'
    imapper = imaplib.IMAP4_SSL(imap_url)
    # bağlantı oluşturmak için
    # imap-->gelen mailler için
    # smtp-->mail göndermek içim kurduğumuz bağlantı
    smtp_url = "mail.gmail.com"
    smtp_port = 587

    # gmail ve port kısımları değiştirilebilir

    def __init__(self, emailAddress, password, fileName=None):
        """
        kullanıcı mail adresi, parolası ve gelen maillerin tutulduğu
        bir dosya her kullanıcı için oluşturulacak
        :param emailAddress: (string) kullanıcının mail adresi
        :param password: (string) kullanıcının parolası
        :param fileName: (string) kullanıcıya gelen maillerin yazılacağı dosya
        """
        self.emailAddrs = emailAddress
        self.passwd = password
        self.fileName = fileName

    def connection(self):
        """
        eposta adresine parola ile giriş,
        tek sefer kullanıyorum diğer tüm metotları kullanmak için
        """
        self.imapper.login(self.emailAddrs, self.passwd)

    def controlAllMessages(self):
        """
        :return: gelen kutusunda kaç mail var, kaçı okunmamış
        """
        x, y = self.imapper.status('INBOX', '(MESSAGES UNSEEN)')
        allMessages = re.search('MESSAGES\s+(\d+)', y[0]).group(1)
        # tüm maillerin toplam sayısı
        unseenMessages = re.search('UNSEEN\s+(\d+)', y[0]).group(1)
        # okunmamış maillerin toplam sayısı
        return int(allMessages), int(unseenMessages)

    def sendMail(self, toAddress, message):
        """
        içeriği belli olan hazır maillerin iletimini kolaylaştıran method

        :param toAddress: mail gönderilecek mail adresi
        :param message: mailin içeriği

        Gmail
            smtp.gmail.com
        Outlook.com/Hotmail.com
            smtp-mail.outlook.com
        Yahoo Mail
            smtp.mail.yahoo.com
        AT&T
            smpt.mail.att.net (port 465)
        Comcast
            smtp.comcast.net
        Verizon
            smtp.verizon.net (port 465)
        """
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        # bağlantı tls ile sağlanır
        server.login(self.emailAddrs, self.passwd)
        # kullanıcı giriş yapar
        text = message.as_string()
        # mesaj string haline getirilir
        server.sendmail(self.emailAddrs, toAddress, text)
        # smtplib kütüphanesinin sendmail() fonksiyonu ile mesaj gönderilir
        server.quit()

    def replyMail(self, mId, newBody="", fileNameList=None):
        """
        bu method belirli bir maile cevap vermeyi sağlar
        cevap verileceği için mailin konusu bellidir, başına Re: ekleriz
        NOTE:
            öncesinde readMail() methodunu kullanarak mail id'sini
            öğrenebiliriz

        ARGS:
            :param mId: (string) cevap verilmek istenen mailin id'si
            :param newBody: (string) maile verilecek cevap
            :param fileNameList: (list) eklenecek dosyaların yollarının listesi
            :return: yok
        """
        self.imapper.select(readonly=True)
        type, data = self.imapper.fetch(mId, '(RFC822)')
        original = email.message_from_string(data[0][1])
        # gelen mailin çekilmesi, original--> gönderilecek mail
        new = MIMEMultipart("mixed")
        body = MIMEMultipart("alternative")
        body.attach(MIMEText(newBody, "plain"))
        if fileNameList is not None:
            # varsa gönderilmek istenen dosyalar
            for f in fileNameList:
                attachment = open(f, "rb")
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', "attachment; filename= %s" % f)
                body.attach(part)
        new.attach(body)
        new["Message-ID"] = email.utils.make_msgid()
        new["In-Reply-To"] = original["Message-ID"]
        new["References"] = original["Message-ID"]
        new["Subject"] = "Re: " + original["Subject"]
        new["To"] = original["Reply-To"] or original['From']
        new["From"] = self.emailAddrs
        # yukarıda cevaplamak için mail oluşturdum
        new.attach(MIMEMessage(original))
        # cevaplamak istediğim maili yeni maile ekledim
        self.sendMail(new['To'], new)

    def sendNewMail(self, toAddress, subject="", body="", fileNameList=None):
        """
        herhangi içeriğin kullanıcı girişiyle alınıp, gönderildiği method
        :param toAddress: (string) mailin gönderileceği adres
        :param subject: (string) mailin konusu
        :param body: (string) mailin içeriği(text)
        :param fileNameList: (list) varsa eklenecek belgelerin yollarının string olarak alındığı liste
        """
        msg = MIMEMultipart()
        msg['From'] = self.emailAddrs
        msg['To'] = toAddress
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        if fileNameList is not None:
            # eğer kullanıcı belge ekleyecekse
            for f in fileNameList:  # her eklediği belge için
                attachment = open(f, "rb")  # belgenin olduğu yolla beraber --> f
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', "attachment; filename= %s" % f)
                msg.attach(part)
        self.sendMail(toAddress, msg)
        # print ("Mailiniz {} adresine başarıyla gönderilmiştir.".format(mailAddress))

    def forwardMail(self, mId, toAddress, newBody="", fileNameList=None):
        """
        Mail id'si ve kime gönderileceği bilinen bir maili
        o kişiye yönlendirmek için method
        :param mId: mailin id'si
        :param toAddress: mail kime yönlendirilecek
        :param newBody: mailin yönlendirileceği kişiye eklenecek body
        :param fileNameList: yönlendirilecek kişiye, varsa eklenecek dosyalar listesi
        :return:

        """
        self.imapper.select(readonly=True)
        type, data = self.imapper.fetch(mId, '(RFC822)')
        original = email.message_from_string(data[0][1])
        # gelen mailin çekilmesi, original--> yönlendirilecek mail
        new = MIMEMultipart("mixed")
        body = MIMEMultipart("alternative")
        body.attach(MIMEText(newBody, "plain"))
        if fileNameList is not None:
            # varsa gönderilmek istenen dosyalar
            for f in fileNameList:
                attachment = open(f,
                                  "rb")  # her eklenecek belge aynı klasörde tutulmalı ve belgelerin tutulduğu path gösterilmeli
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', "attachment; filename= %s" % f)
                body.attach(part)
        new.attach(body)
        new["Message-ID"] = email.utils.make_msgid()
        new["In-Reply-To"] = original["Message-ID"]
        new["References"] = original["Message-ID"]
        new["Subject"] = "Fwd:" and original["Subject"]
        new["To"] = toAddress
        new["From"] = self.emailAddrs
        # yukarıda yönlendirmek için mail oluşturdum
        new.attach(MIMEMessage(original))
        # yönlendirmek istediğim maili yeni maile ekledim
        self.sendMail(toAddress, new)

    def readMail(self, readOnly=True):
        """
        Gelen mailleri readOnly=False ise okundu işaretleyerek, readOnly=True ise okundu işaretlemeden
        tüm mail bilgilerini kullanıcı için yazdırır
        NOTE:
        readOnly=False --> maili okundu olarak işaretler
        readOnly=True --> maili okunmadı olarak işaretler
        Sonrasında maili yönlendireceksek veya cevaplayacaksak
        mail okunmadı işaretli olmalı
        ARGS:
        :param readOnly: (bool) True/False değer alır
        :return: okunmamış mailleri bilgileriyle döndürür
        """
        self.imapper.select('inbox', readonly=readOnly)
        # readonly True-->okunmadı işaretler,
        type, data = self.imapper.search(None, 'UNSEEN')
        # açılmamış maillerin idlerini data[0]'a  atar
        mailIds = data[0]
        idList = mailIds.split()
        for mailId in idList:
            # seçilen tüm idleri teker teker işler
            typ, data = self.imapper.fetch(mailId, '(RFC822)')
            print (mailId)
            # yönlendirmek istersek bu id'yi kullanabilelim diye
            # görmek için print ettim
            for responsePart in data:
                if isinstance(responsePart, tuple):
                    msg = email.message_from_string(responsePart[1])
                    dmsgsub, dmsgsubEncoding = header.decode_header(msg['Subject'])[0]
                    email_subject = dmsgsub.decode(
                        *([dmsgsubEncoding] if dmsgsubEncoding else [])) if isinstance(dmsgsub,
                                                                                       bytes) else dmsgsub
                    # yukarıdaki kod çok çirkin farkındayım ama işe yarıyor-->konudaki utf-8 sorununu çözüyor
                    print ('From : ' + msg['From'] + '\n')
                    print ('Date : ' + msg['Date'] + '\n')
                    print ('Subject : ' + email_subject + '\n')
                    print ('To : ' + msg['To'] + '\n')
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True)
                            print ('Body : ' + str(body) + '\n')
                            # body'de yazan texxt varsa yazdırır
                    if readOnly == False:
                        # eğer okundu işaretlenecekse mail, bir kere kişinin kendi dosyasında kayıtlı olsun
                        with open(self.fileName, "wb") as file:  # tüm okunan mailleri dosyaya yazar
                            json.dump({mailId: msg}, file)

    def getMail(self, mId):
        """
        id'sini bildiğimiz maili geri döndürür
        :param mId: mail id'si
        :return: mail içeriğini döndürür
        """
        self.imapper.select('inbox', readonly=True)
        # readonly=true --> mesaj okunmadı işaretlemek için
        type, data = self.imapper.search(None, 'ALL')
        # açılmış/açılmamış tüm maillerin idlerini string olarak  data[0]'a  atar
        mailIds = data[0]
        idList = mailIds.split()
        for mailId in idList:
            # seçilen tüm idleri teker teker işler
            if mailId == mId:
                typ, data = self.imapper.fetch(mailId, '(RFC822)')
                for responsePart in data:
                    if isinstance(responsePart, tuple):
                        msg = email.message_from_string(responsePart[1])
                        return msg

    def search(self, criteria):
        """
        spesifik bir kişiden,tarihten,konudan mail çekmek için method
         '(SENTSINCE {0})'.format(date)), '(FROM {0})'.format("someone@yahoo.com".strip())
         şeklinde aramalar yapılabilir
        :param
        criteria: hangi kritere göre arama yapacağımız(string)
        :return: uygun mail id'lerini liste olarak döndürür
        """
        self.imapper.select('inbox', readonly=True)
        result, data = self.imapper.search(None, 'X-GM-RAW', '{0}'.format(criteria))
        idList = data[0].split()
        return idList
        # start = min(len(emailIds), 1000)
        # return emailIds[-1:-(start + 1):-1]
        # Aranan kritere uyan maillerin id'sini liste halinde döndürür

    def deleteMail(self, mId):
        """
        mail id'si bilenen maili siler
        :param mId: mail id
        :return: yok
        """
        self.imapper.select('inbox', readonly=False)
        # readonly False çünkü sadece okuma işlemini yaparsa silemez
        type, data = self.imapper.search(None, 'ALL')
        # açılmış/açılmamış tüm maillerin idlerini string olarak  data[0]'a  atar
        mailIds = data[0]
        idList = mailIds.split()
        for mailId in idList:
            # seçilen tüm idleri teker teker gezer
            if mailId == mId:
                # aranan mail bulununca silindi işaretlenir
                self.imapper.store(mailId, '+FLAGS', '\\Deleted')
        # silen fonksiyon -->expunge
        print self.imapper.expunge()
        # silindiğine dair bilgilendirme
