# This program is written by Akash Chatterjee on 25th April 2020
#
#
#
#importing necessary libraries 
import requests as req
from lxml import html
import pandas as pd
import json
#get_captcha function
def get_captcha():
	cap=input("Enter captcha:")
	return cap
#starting a requests session
with req.Session() as s:
	f=0
	# main url to scrape data from
	url="https://parivahan.gov.in/rcdlstatus/?pur_cd=101"
	
	r=0
	while (f==0):
		# taking necessary inputs from the user
		dlNO=input("Enter Driving Licence Number:").upper()
		dob=input("Enter Date of Birth in dd-mm-yyyy format:")
		#getting the html data using requests.get() from the url
		r=s.get(url)
		#saving the cookies in the cookies variable
		cookies=r.cookies
		#parsing html data to string. r.content gives byte code from the response
		html_code=html.fromstring(r.content)
		#getting the viewstate value which is required to get the results after filling the form. Use inspect from your browser to get the requirements and the xpath
		viewstate=html_code.xpath('//*[@id="j_id1:javax.faces.ViewState:0"]')[0].value
		#getting the url of the captcha image and saving it in a folder so that we can view the image and enter the correct captcha
		url_captcha="https://parivahan.gov.in/rcdlstatus/DispplayCaptcha?txtp_cd=1&bkgp_cd=2&noise_cd=2&gimp_cd=3&txtp_length=5&pfdrid_c=true?-1947393506&pfdrid_c=true"
		captcha=s.get(url_captcha)
		f=open("captcha.png",'wb')
		f.write(captcha.content)
		f.close()
		#calling get_captcha function and storing it in a variable
		cap=get_captcha()
		#setting all the required data fields needed to get the result and posting it to the url using requests.post()
		#get this elements by inspecting the form fields in webpage headers
		login_data={
		'javax.faces.partial.ajax': 'true',
		'javax.faces.source': 'form_rcdl:j_idt46',
		'javax.faces.partial.execute': '@all',
		'javax.faces.partial.render': 'form_rcdl:pnl_show form_rcdl:pg_show form_rcdl:rcdl_pnl',
		'form_rcdl:j_idt46': 'form_rcdl:j_idt46',
		'form_rcdl': 'form_rcdl',
		'form_rcdl:tf_dlNO': dlNO,
		'form_rcdl:tf_dob_input': dob,
		'form_rcdl:j_idt34:CaptchaID': cap,
		'javax.faces.ViewState': viewstate
		}
		#posting the login data to the url
		r=s.post(url=url,data=login_data,cookies=cookies)
		#Checking if we got the results and displaying respective error messages
		if "Current Status" in r.text:
			f=1
		elif "Alert!" in r.text:
			print("ERROR!! No information found! Please try again with correct DLNO and DOB")
		else:
			print("Wrong Captcha! Please try again!")
	#f=1 we got the correct results. SO lets now scrape the data from the form	
	if f==1:
		d={'Driving Licence No':{'info':dlNO}}
		html_code=html.fromstring(r.content)
		#searching all table contents and creating a list named 'table'
		table=html_code.xpath('//tr')
		l=len(table)
		#creating the .json file by arranging and scraping the data from the table
		for i in range(5):
			d[table[i][0].text_content()[:table[i][0].text_content().index(':')]]={'info':table[i][1].text_content()}
		for i in range(5,7):
			key=table[i][0].text_content()
			l1=list(table[i][1].text_content().split(sep=':'))
			l2=list(table[i][2].text_content().split(sep=':'))
			d[key]={l1[0]:l1[1],l2[0]:l2[1]}
		d[table[7][0].text_content()[:table[7][0].text_content().index(':')]]={'info':table[7][1].text_content()}
		d[table[7][2].text_content()[:table[7][2].text_content().index(':')]]={'info':table[7][3].text_content()}
		
		for i,j in zip(table[8],table[9]):
			d[i.text_content()]={'info':j.text_content()} 
		#Creating the data.json file which has the data
		with open('data.json','w') as file:
			json.dump(d,file,indent=4)
		#Displaying the data frame using pandas in realtime ClI interface
		print("\n\n\t::The Data Table::\n\n")
		df=pd.read_json('data.json')
		df=df.T
		df.to_json("output.json")
		print(df)
		print("\n\n")
		
