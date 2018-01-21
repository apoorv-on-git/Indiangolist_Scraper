#importing important files
import requests, json
from bs4 import BeautifulSoup
import unicodecsv as csv

#URL of the website to start scraping data from
START_URL = "http://www.indiangoslist.com/delhi-ngos-list/1"

#Function defined to scrape URL of different NGOs from the website
def scrape_ngo_list(page_url, page_no=1):
	
	#Requesting to open the first page.
	page = requests.get(page_url)
	
	#Setting up BS Instance.
	soup = BeautifulSoup(page.content, "html.parser")
	
	#Finding 'h2' tags inside the 'div' tag of of class 'article'.
	ngo_links = soup.find("div", {'class' : "article"}).findAll('h2')

	#Finding all 'a' attributes within the 'h2' tags.
	ngo_links = [tag.findAll('a') for tag in ngo_links]

	#Extracting the 'href' from the 'a' attribute.
	ngo_links = [i[0].get('href').encode('ascii', 'ignore') for i in ngo_links]
	print ("Found {0} links on page number {1}.").format(len(ngo_links), page_no)

	#Joining the elements of ngo_links with '\n'.
	links = "\n".join(ngo_links)
	links = "\n" + links

	#Opening a text file to store the ngo links.
    	links_file = open("indiangolist_links.txt", "a")

	#Writing the ngo links.
    	links_file.write(links)
    	links_file.close()
	
	#Going to the next page.
	#Finding all span and storing the span in variable "current_page_span" whose class is 'current'.
	current_page_span = soup.findAll('span', {'class': 'current'})[0]
	#Finding the next page span and storing it's value in a variable 'next_page_a'.
	next_page_a = current_page_span.find_next('a')
	
	#Try statement to handle errors.
	try:
		next_page_link = next_page_a.get('href')
		print next_page_link
		page_no = page_no + 1
		#Recursive function that will call itself with the new page link. This will scrape the NGO's links from all the pages in the website.
		scrape_ngo_list(next_page_link, page_no)
	#Except statement to handle errors given out at the end of the procedure.
	except:
		pass

#Function defined to scrape details from a link.
def scrape_ngo_details(ngo_link):

	#Try statement to handle errors.
	try:
		print "Scraping {0}".format(ngo_link)
		
		#Requesting to open the first page.
		page = requests.get(ngo_link)

		#Setting up BS Instance.
		soup = BeautifulSoup(page.content, "html.parser")

		#Selecting the 'div' containing all the contact details.
		contact_details = soup.find(id = 'contact details').findAll('div')

		#Finding all 'span' inside the 'div' of this id.
		contact_details_span = soup.find(id = 'contact details').findAll('span')

		#Declaring a variable 'name' which will become a list of all 'h2' in the web page using .select()
		name = soup.select('h2')

		#Removing all other elements of the list created.
		name = name[0]

		#Using text to convert the variable into a string.
		name = name.text

		#Declaring a dictionary to store the useful information gathered by the scraper from the link.
		#Using str() for the value to avoid the unicode 'u'.
		details_dict = {'name' : str(name[:-13])}
		current_key = None
		current_value = None
		
		#Empty list to store the information present in a 'div' of class 'ngo_left_head'.
		ngo_left_head = []
		
		#Finding all the 'div' tags with 'class' of 'ngo_left_head'.
		all_left = soup.findAll('div', {'class' : 'ngo_left_head'})
		
		index = 0

		#Using while loops to store the filtered contents.
		while index < len(contact_details):
			counter = 0
			
			#Nested While loop for filtering the content by iterating the counter.
			while counter < len(all_left):
	
				#Storing the value of 'counter' element inside of the list 'all_left' which has all 'div' tags defined above.
				current_detail_left = all_left[counter].text.encode('ascii', 'ignore')

				#Checking if the 'current_detail' of the counter element is inside the index element of list 'contact_details'
				if current_detail_left in contact_details[index]:
					ngo_left_head.append(current_detail_left)
					break 
				else:
					counter = counter + 1
			index = index + 1
		
		#Empty list to store the information present in a 'div' of class 'ngo_right_head'.
		ngo_right_head = []

		#Finding all 'div' tags with 'class' of 'ngo_right_head'
		all_right = soup.findAll('div', {'class' : 'ngo_right_head'})

		index = 0

		#Using while loop to store the filtered content.
		while index < len(contact_details_span):

			#Condition to avoid the double value, present in third element of 'contact_details_span'
			if index != 3:

				#Extracting the text value from the index element of the 'contact_details_span' list defined above.
				text = contact_details_span[index].text.encode('ascii', 'ignore')
				ngo_right_head.append(text)
			index = index + 1

		#Extracting the website details which is in the last element of list 'contact_details'
		index = len(contact_details) - 1

		while index < len(contact_details):
			counter = 0

			#Nested while loop for filtering the content by iterating the counter.
			while counter < len(all_right):

				#Storing the value of 'counter' element inside the list 'all_right' defined above.
				current_detail_right = all_right[counter].text.encode('ascii', 'ignore')

				#Checking if the 'current_detail' of the counter element is inside the index element of the 'contact_details'
				if current_detail_right in contact_details[index]:
					ngo_right_head.append(current_detail_right)
					break
				else:
					counter = counter + 1

			#Break statement to break the outer loop.
			break

		count = 0
		#While loop to add 'current_key' from 'ngo_left_head' and 'current_value' from 'ngo_right_head' simultaneously inside the dictionary.
		while count < len(ngo_left_head):
			current_key = ngo_left_head[count]
			current_value = ngo_right_head[count]
			details_dict[str(current_key)] = str(current_value)
			count = count + 1
	
		#Returning the value of dictionary.
		return details_dict
	
	#Except statement to handle errors given out at the end of the procedure.
	except:
		print 'Failed to scrape the link.'

#Function defined to scrape details from all the links collected.	
def scrape_all_links():

	#Open the file with links.
	links_file = open('indiangolist_links.txt', 'r')
	links = links_file.read().split('\n')

	#Empty list to store details from each link.
	ngo_details = []

	#For loop to iterate over each link in the list of links
	for link in links:

		#Scraping the details from each list.
		details = scrape_ngo_details(link)
		if details:
			ngo_details.append(details)
	
	#Creating a JSON file to store the list of data.
	with open('details.txt', 'w') as json_file:
		json_file = json.dump(ngo_details, json_file)

	return json_file

#Function defined to get the final csv.
def get_final_csv():

	#Opening and reading the json file.
	json_file = open('details.txt')
	details = json.loads(json_file.read())

	#Creating a set of all the unique data of the NGO.
	keys = set()

	#Iterating over each dictionary.
	for detail in details:

		#Adding each key inside the set.
		for key in detail.keys():
			keys.add(key)

	#Creating a list of keys.
	keys = list(keys)

	#Creating a CSV file of the data collected.
	with open('indiangolist.csv', 'wb') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(details)


	#Print statement after everything is done.
	print ('Done Scraping.') 

#Calling all the functions to scrape the website.

scrape_ngo_list(START_URL)

scrape_all_links()

get_final_csv()
