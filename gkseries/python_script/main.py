from bs4 import BeautifulSoup
import requests
import json
import os

base_url = "https://www.gkseries.com/"
r = requests.get(base_url)
print(r)

base_soup = BeautifulSoup(r.content, 'lxml')

base_div = base_soup.find_all('div', class_='col-lg-12')

total_subject = 0
for box_div in base_div[0:2]:
    subjects = box_div.find_all('div', class_='sb-list')

    for subject in subjects:
        topic_links = []
        subject_name = subject.find('h4')
        if subject_name == None:
            subject_name = subject.find('h3').text
        else:
            subject_name = subject.find('h4').text
        print(subject_name)
        if subject_name == 'PHP':
            links = subject.find('div', class_= 'list-group')('a')
            topic_links.append([links[0].get('href'), links[0].text])
            topic_links.append([links[1].get('href'), links[1].text])
            topic_links.append([links[2].get('href'), links[2].text])
            
            subject_name = subject.find_all('h4')[1].text
            print(subject_name)

        view_all_link = subject.find('h5')('a')[0].get('href')
        view_all_req = requests.get(base_url+str(view_all_link))

        if str(view_all_req) == "<Response [404]>":
            view_all_req = requests.get(str(view_all_link))
        else:
            view_all_link = base_url+str(view_all_link)

        print(view_all_req)
        subject_page = BeautifulSoup(view_all_req.content, 'lxml')

        topic_li_tag = subject_page.find_all('li', role='presentation')
        # print(t)
        if len(topic_li_tag) == 0:
            continue
        for page_li in topic_li_tag:
            topic_links.append([page_li.find('a').get('href'),page_li.find('a').text])
        
        print(len(topic_links))
        view_all_link = view_all_link.split('/')
        topic_base_url = '/'.join(view_all_link[0:len(view_all_link)-1])
        i = 0
        for topic_link in topic_links:
            # print(topic_link[0])
            topic_name = topic_link[1]
            topic_url = topic_base_url + '/' + str(topic_link[0])
            
            try:
                topic_page = requests.get(topic_url)
                print(topic_page, topic_url)
            except:
                continue

            # print(topic_page, topic_url)
            # page url
            html_content = topic_page.content

            # parsing html content
            soup = BeautifulSoup(html_content, 'lxml')

            # get all page url from pagination
            pages_url = soup.find_all('li', {'itemprop':'position'})
            print(len(pages_url), "pages")
            mcqs_ = []
            for page in pages_url[:-1]:                     # to get each page html
                try:
                    page_ = page.find('a').get('href')
                except:
                    continue
                new_url = topic_url.split('/')
                new_url = '/'.join(new_url[0:len(new_url)-1])
                page_url = new_url + '/'+ str(page_)
                print(page_url)

                # getting the html and parsing it
                r = requests.get(page_url)
                html_content = r.content
                soup = BeautifulSoup(html_content, 'lxml')

                # finding each question
                full_question = soup.find_all('div', {'class': 'mcq'})
                
                for question in full_question:              # looping across each question of the page
                    # to get question
                    question_div = question.find(class_ = 'question-content')
                    question_no = question_div.find('span').text
                    current_question = question_div.text.replace(question_no, "")
                    current_question = " ".join(current_question.split())
                    # print(question_no, current_question)

                    # to get option
                    option_div = question.find_all('div', {'itemprop': "text"})  
                    options_list = []               
                    for option in option_div[:-1]:
                        option_no = option.find('span').text
                        current_option = option.text.replace(option_no, "")
                        current_option = " ".join(current_option.split())
                        options_list.append([option_no, current_option])
                        # print(option_no, current_option)
                    
                    # for answer
                    answer = (" ".join(option_div[-1].text.split())).replace("Answer: ", "")
                    # print(answer, "\n")

                    # adding data in dictionary for json
                    op1 = options_list[0][1]
                    op2 = options_list[1][1]
                    op3 = options_list[2][1]
                    op4 = options_list[3][1]

                    if answer == 'Option [A]':
                        answer = 1
                    elif answer == 'Option [B]':
                        answer = 2
                    elif answer == 'Option [C]':
                        answer = 3
                    elif answer == 'Option [D]':
                        answer = 4
                    else:
                        continue

                    mcqs_.append({ 'question': current_question,
                                'op1': op1,
                                'op2': op2,
                                'op3': op3,
                                'op4': op4,
                                'answer:': answer})

            print(len(mcqs_), "total mcqs")
            topic_name = topic_name.replace('/', "-")
            if len(mcqs_) > 0:
                if os.path.exists(str(topic_name) + '.json'):
                    print("has file")
                    with open(str(topic_name) + '.json') as file:
                        json_file = json.load(file)
                        json_file['data'] += mcqs_ 
                    pass
                else:
                    print("no file")
                    json_dict = {
                        'topic': topic_name,
                        'Subject': subject_name,
                        'data': mcqs_
                    }
                    json_object = json.dumps(json_dict, indent=4)
                    with open(str(topic_name)+ '.json', 'w') as file:
                        file.write(json_object)
            
            # if i == 0:
            #     topic_base_url = '/'.join(view_all_link[0:len(view_all_link)-2])
            #     i +=1
        
        