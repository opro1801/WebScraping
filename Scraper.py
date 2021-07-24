#imports here
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from datetime import datetime
import re
import os
import psycopg2
from psycopg2 import sql


def get_comp_name(driver):
	head_container = driver.find_elements_by_css_selector("div[class='rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t g5gj957u d2edcug0 hpfvmrgz on77hlbc buofh1pr o8rfisnq ph5uu5jm b3onmgus ihqw7lf3 ecm0bbzt']")
	if len(head_container) > 0:
		name_container = head_container[0].find_elements_by_css_selector("div[class='bi6gxh9e aov4n071']")
	else:
		head_container = driver.find_elements_by_css_selector("div[class='rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t buofh1pr tgvbjcpo']")
		name_container = head_container[0].find_elements_by_css_selector("div[class='rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t pfnyh3mw d2edcug0 bp9cbjyn jb3vyjys']")
	return name_container[0].text
	
def get_fb_link(link):
	return link

def get_messenger(link):
	mess_pattern = 'https://www.facebook.com/messages/t/'
	fb_pattern = 'https://www.facebook.com/'
	return mess_pattern + link[len(fb_pattern):]

def get_phone_number(info):
	phone_pattern = '\+852\s[0-9]{4}\s[0-9]{4}'
	return re.fullmatch(phone_pattern, info.text)
def get_email(info):
	return '@' in info.text
def get_website(info):
	return 'http' in info.text or '.com' in info.text
def get_business_class(info):
	return len(info.find_elements_by_css_selector("a[class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p']")) > 0

def get_other_about_info(about_container, keyword):
	phone = '?'
	mail = '?'
	web = '?'
	busclass = '?'
	des = ''
	see_more_buttons = about_container.find_elements_by_css_selector("div[class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p']")
	for butt in see_more_buttons:
		if 'See more' in butt.text:
			butt.click()
	infos = about_container.find_elements_by_css_selector("div[class='j83agx80']")
	second_struct = False
	if len(infos) == 0:
		infos = about_container.find_elements_by_css_selector("div[class='rq0escxv l9j0dhe7 du4w35lb j83agx80 pfnyh3mw jifvfom9 gs1a9yip owycx6da btwxx1t3 discj3wi b5q2rw42 lq239pai mysgfdmx hddg9phg']")
		second_struct = True
		busclass = keyword
	for info in infos:
		if get_phone_number(info):
			phone = info.text
		elif get_email(info):
			mail = info.text
		elif get_website(info):
			web = info.text
		elif not second_struct and get_business_class(info):
			busclass = info.text
		else:
			des+=info.text + '\n'
	return phone, mail, web, busclass, des

def get_followers(about_container):
	num = ''
	like_follow = about_container.find_elements_by_css_selector("div[class='taijpn5t cbu4d94t j83agx80']")
	if len(like_follow) > 0:
		for text in like_follow:
			if 'follow' in text.text:
				num = text.text[:-19]
				break
		num = ''.join(num.split(','))
	else:
		ul_elem = about_container.find_elements_by_css_selector("div[class='rq0escxv l9j0dhe7 du4w35lb j83agx80 pfnyh3mw jifvfom9 gs1a9yip owycx6da btwxx1t3 jb3vyjys b5q2rw42 lq239pai mysgfdmx hddg9phg']")
		for text in ul_elem:
			if 'followers' in text.text:
				num = text.text[:-10]
				break
		if 'K' in num:
			num = float(num[:-1])*1000
	return int(num)

def get_page_created_date(driver, link):
	pcd_container = driver.find_elements_by_css_selector("span[class='ll8tlv6m j83agx80 wkznzc2l dhix69tm aov4n071']")
	pcd_pattern = 'Page created – '
	if len(pcd_container) == 0:
		about_link = link + '/about_profile_transparency'
		driver.get(about_link)
		transparent_container = driver.find_elements_by_css_selector("div[class='dati1w0a tu1s4ah4 f7vcsfb0 discj3wi']")
		list_text = transparent_container[0].text.split('\n')
		for id_text in range(len(list_text)):
			if list_text[id_text] == 'Page creation date':
				return list_text[id_text-1]
	return pcd_container[0].text[len(pcd_pattern):]

def get_about_container(keyword,driver):
	'''block_titles = driver.find_elements_by_css_selector("span[class='a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 r8blr3vg']")
				about_index = 0
				for index in range(len(block_titles)):
					if 'About' in block_titles[index].text or 'Intro' in block_titles[index].text:
						about_index = index
						break'''
	left_container = driver.find_elements_by_css_selector("div[class='sjgh65i0']")
	for container in left_container:
		if container.text[:5] == 'About' or container.text[:5] == 'Intro':
			about_container = container
			break
	try:
		foll = get_followers(about_container)
	except:
		foll = '-1'
	try:
		phone, mail, web, busclass, des = get_other_about_info(about_container, keyword)
	except:
		phone, mail, web, busclass, des = 'error', 'error', 'error', 'error', 'error'
	return phone, mail, web, busclass, des, foll

def get_left_info(driver, link, keyword):
	#left_containter = driver.find_elements_by_css_selector("div[class='rq0escxv l9j0dhe7 du4w35lb fhuww2h9 hpfvmrgz o387gat7 g1e6inuh g5gj957u aov4n071 oi9244e8 bi6gxh9e h676nmdw aghb5jc5 rek2kq2y']")
	#print(len(left_containter))
	#print(pcd)
	phone, mail, web, busclass, des, foll = get_about_container(keyword, driver)
	try:
		pcd = get_page_created_date(driver, link)
	except:
		pcd = 'error'
	return phone, mail, web, busclass, des, foll, pcd


def get_latest_post(right_container):
	feeds = right_container[0].find_elements_by_css_selector("div[role='feed']")
	if len(feeds) > 0:
		post_container = feeds[-1]
	else:
		post_container = right_container[0]
	posts = post_container.find_elements_by_css_selector("div[class='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0']")
	if len(posts) == 0:
		return 'No post'
	latest_post = posts[0]
	post_time = latest_post.find_elements_by_css_selector("a[class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw']")[0]
	#may change
	#print("get_latest_post")
	return post_time.text

def get_right_info(driver):
	right_container = driver.find_elements_by_css_selector("div[class='dp1hu0rb d2edcug0 taijpn5t j83agx80 gs1a9yip']")
	if len(right_container) == 0:
		right_container = driver.find_elements_by_css_selector("div[class='rq0escxv l9j0dhe7 du4w35lb fhuww2h9 hpfvmrgz gile2uim pwa15fzy g5gj957u aov4n071 oi9244e8 bi6gxh9e h676nmdw aghb5jc5']")
	latest_post = get_latest_post(right_container)
	#print("get_right_info")
	return latest_post

def transform_keyword(keyword):
	tmp_key = keyword
	if '-' in keyword:
		tmp_key = '_'.join(tmp_key.split('-'))
	if ' ' in keyword:
		tmp_key = '_'.join(tmp_key.split(' '))
	return tmp_key

def insert_to_db(scroll_num, keyword, res):
	(comp, fb, phone, mess, des, mail, web, foll, latest_post, scraping_time, pcd, busclass) = res
	tmp_key = transform_keyword(keyword)
	conn = psycopg2.connect(DATABASE_URL, sslmode='require')
	cur = conn.cursor()
	try:
		cur.execute("""SELECT Count(*) FROM _Master
	                WHERE Facebook = %s""", (fb,))
		data = cur.fetchone()[0]
		if data == 0:
			sqlite_insert_with_param = """INSERT INTO _Master
							(Company, Facebook, Phone, Messenger, Description, Email, Website, NumFollowers, LatestPost, ScrapingTime, PageCreatedDate, BusinessClassification, ScrollNumber, Keyword) 
								SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
								WHERE NOT EXISTS
								(SELECT Facebook FROM _Master
									WHERE Facebook = %s);"""
			data_tuple = (comp, fb, phone, mess, des, mail, web, foll, latest_post, scraping_time, pcd, busclass, scroll_num, keyword, fb)
			cur.execute(sqlite_insert_with_param, data_tuple)
			conn.commit()
			print("Record ", comp, phone, file=open(file_name, 'a', encoding='utf-8'))
			print("Record ", comp, phone)
			try:
				cur.execute(sql.SQL('''CREATE TABLE {}
							(Company text, Facebook text, Phone text, Messenger text, Description text, Email text, Website text, NumFollowers integer,LatestPost text, ScrapingTime text, PageCreatedDate text, BusinessClassification text, ScrollNumber integer, Keyword text)''').format(sql.Identifier(tmp_key)))
			except:
				conn.rollback()
			query = sql.SQL("""INSERT INTO {} (Company, Facebook, Phone, Messenger, Description, Email, Website, NumFollowers, LatestPost, ScrapingTime, PageCreatedDate, BusinessClassification, ScrollNumber, Keyword)
								SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s;""").format(sql.Identifier(tmp_key))
			tup = (comp, fb, phone, mess, des, mail, web, foll, latest_post, scraping_time, pcd, busclass, scroll_num, keyword,)
			cur.execute(query, tup)
		else:
			try:
				cur.execute("""SELECT Count(*) FROM _Master
							WHERE Facebook = %s AND LatestPost = %s""", (fb, latest_post,))
				data = cur.fetchone()[0]
				if data == 0:
					cur.execute("""UPDATE _Master
							SET LatestPost = %s, ScrapingTime = %s
							WHERE Facebook = %s""", (latest_post, datetime.now().strftime("%Y-%m-%d"), fb))
					print("Update ", comp, phone, file=open(file_name, 'a', encoding='utf-8'))
					print("Update ", comp, phone)
					cur.execute(sql.SQL("""UPDATE {} SET LatestPost = %s, ScrapingTime = %s
											WHERE Facebook = %s""").format(sql.Identifier(tmp_key)), (latest_post, datetime.now().strftime("%Y-%m-%d"), fb))            
				else:
					print(comp, " already exists", file=open(file_name, 'a', encoding='utf-8'))
					print(comp, " already exists")
			except:
				conn.rollback()
	except:
		print("db error")
	conn.commit()
	cur.close()
	conn.close()


def get_page_data(driver, link, keyword, scroll_num):
	#print("get_page_data")
	driver.get(link)
	time.sleep(3)
	try:
		comp = get_comp_name(driver)
	except:
		comp = 'error'
	#print(comp)
	fb = get_fb_link(link)
	mess = get_messenger(link)
	try:
		latest_post = get_right_info(driver)
	except:
		latest_post = 'error'
	phone, mail, web, busclass, des, foll, pcd = get_left_info(driver, link, keyword)
	scraping_time = datetime.now().strftime("%Y-%m-%d")
	res = (comp, fb, phone, mess, des, mail, web, foll, latest_post, scraping_time, pcd, busclass)
	#print("before insert")
	insert_to_db(scroll_num, keyword, res)
	#print("after insert")
	#print('comp: ', comp, '\nfb: ', fb, '\nphone: ', phone, '\nmess: ', mess, '\ndes: ', des, '\nmail: ', mail, '\nweb: ', web, '\nfoll: ', foll, '\nlast_pst:', latest_post, '\nscraping time: ',scraping_time, '\npcd: ', pcd, '\nclass: ', busclass)

def get_driver():
	#print("get_driver")
	options = webdriver.ChromeOptions()
	options.binary_location = os.environ["GOOGLE_CHROME_BIN"]
	options.add_argument("--headless")
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-sh-usage")
	options.add_argument("--disable-gpu")
	options.add_argument("--remote-debugging-port=9222")
	#prefs = {"profile.default_content_setting_values.notifications" : 2}
	#chrome_options.add_experimental_option("prefs",prefs)
	#specify the path to chromedriver.exe (download and save on your computer)
	driver = webdriver.Chrome(executable_path= os.environ["CHROMEDRIVER_PATH"], chrome_options=options)
	#open the webpage
	driver.get("http://www.facebook.com")

	#target username
	username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
	password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))
	
	#enter username and password
	username.clear()
	username.send_keys("xayob70017@dedatre.com")
	password.clear()
	password.send_keys("icho2019")
	
	#target the login button and click it
	button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
	return driver

def create_db():
	#print("create_db")
	conn = psycopg2.connect(DATABASE_URL, sslmode='require')
	cur = conn.cursor()
	try:
		cur.execute('''CREATE TABLE _Master
	                (Company text, Facebook text, Phone text, Messenger text, Description text, Email text, Website text, NumFollowers integer,LatestPost text, ScrapingTime text, PageCreatedDate text, BusinessClassification text, ScrollNumber integer, Keyword text)''')
	except:
	    conn.rollback()
	conn.commit()
	cur.close()
	conn.close()

def get_num_link(keyword):
	#print("get_num_link")
	conn = psycopg2.connect(DATABASE_URL, sslmode='require')
	cur = conn.cursor()
	cur.execute("""SELECT Count(Facebook) FROM _Master
				WHERE Keyword = %s""", (keyword,))
	num_links = cur.fetchone()[0]
	if num_links == 0:
		cur.close()
		conn.close()
		return 0, 0
	else:
		cur.execute("""SELECT ScrollNumber FROM _Master
					WHERE Keyword = %s
					ORDER BY ScrollNumber DESC""", (keyword,))
		scroll_pos= cur.fetchone()[0] + 1
		cur.close()
		conn.close()
		return num_links, scroll_pos

def check_skip(len_new_link, cur_count):
	return len_new_link == 0 and cur_count == 3

def main_func():
	create_db()
	driver1 = get_driver()
	#print(driver.page_source)
	driver2 = get_driver()
	time.sleep(3)
	
	key_list = ['Advertising', 'marketing', 'Agriculture', 'Arts', 'entertainment','Beauty', 'cosmetic', 'personal care',
	'Commercial', 'industrial', 'Education', 'Finance', 'Food', 'drink', 'Hotel', 'Legal', 'Local service',
	'Media', 'news company', 'Medical', 'health', 'Non-governmental organisation', 'Non-profit organisation',
	'Property', 'Public service', 'government service', 'Science', 'technology', 'engineering', 'Shopping', 'retail',
	'Sport', 'recreation', 'Travel', 'transport', 'Vehicle', 'aircraft', 'boat']

	filter_var = '&filters=eyJmaWx0ZXJfcGFnZXNfbG9jYXRpb246MCI6IntcIm5hbWVcIjpcImZpbHRlcl9wYWdlc19sb2NhdGlvblwiLFwiYXJnc1wiOlwiMTEzMzE3NjA1MzQ1NzUxXCJ9In0%3D'
	domain = 'https://www.facebook.com/search/pages?q='
	scroll_range = 2

	#temp_break = 0

	for keyword in key_list:
		#if temp_break == 2:
		#	break
		#temp_break+=1
		search_link = domain + keyword + filter_var
		driver1.get(search_link)
		time.sleep(3)
		#print(driver.page_source)
		cur_count = 0
		num_links, scroll_pos = get_num_link(keyword)
		#print("num_links: ", num_links)
		#print("scroll_pos: ", scroll_pos)
		for times_to_ignore in range(0, scroll_pos):
			driver1.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			#print("scroll over")
			time.sleep(2)
		for scroll_num in range(scroll_pos, scroll_pos + scroll_range):
			links = []
			#print("come here")
			result_container = driver1.find_elements_by_css_selector("a[class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p dkezsu63']")
			for index_link in range(num_links, len(result_container)):
				links.append(result_container[index_link].get_attribute('href'))
			num_links+=len(links)
			print("Page",scroll_num, "of",keyword, ":", len(links), "links recorded", file=open(file_name, 'a', encoding='utf-8'))
			print("Page",scroll_num, "of",keyword, ":", len(links), "links recorded")
			if len(links) == 0:
				cur_count+=1
				if check_skip(len(links), cur_count):
					break
			else:
				cur_count = 0
			for link in links:
				get_page_data(driver2, link, keyword, scroll_num)
				#	num_links-=1
				#	continue
			driver1.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(2)

if __name__ == '__main__':
	DATABASE_URL = os.environ['DATABASE_URL']
	file_name = datetime.now().strftime("%Y_%m_%d_%Hh_%Mm_%Ss") + '.txt'
	main_func()

