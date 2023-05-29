from modules import EmailFinder
from modules import LeadGenerater
from time import sleep
print("Select Option\n\t1.Generate Leads\n\t2.Scrape Emails and Phone Numbers")
method=int(input(": "))
with open("settings.txt", "r") as file:
    lines = file.readlines()
    linkedin_email = lines[0].replace("\n", "")
    linkedin_pass = lines[1].replace("\n", "")
if method==1:
    leads_no=int(input("How many data? : "))
    filter_url=input("Put Sales Navigator link: ")

    print("\nRunning\n")
    obj = LeadGenerater.Lead_Generator()
    obj.create_writer()
    links, existing_data = obj.get_linkedIn_data()
    obj.initialize(linkedin_email, linkedin_pass, user_dir=False)
    obj.search_result(
        filter_url,lead_no=leads_no,existing_data=existing_data
    )

elif method==2:

    print("\nRunning\n")
    obj = EmailFinder.Tool()
    obj.create_writer()

    links,existing_data = obj.get_linkedIn_data()
    print("Total with empty email and number: "+str(links))
    print(len(existing_data))
    print(len(links))

    obj.initialize(linkedin_email, linkedin_pass)
    count=0
    count_100=0
    data_count=1
    for link in links:
        obj.randomize_sleep()
        if count>10:
            obj.randomize_sleep(long=True)
            count=0
        else:
            count+=1
        if count_100>=30:

            sleep(300)

            count_100=0
        else:
            count_100+=1

        # obj.scrape_salesql(link[6])
        if link['Linkedin'] in obj.read_history():
            pass
        else:
            if obj.check_url(link['Linkedin']) == False:
                try:
                    with open("brokenLinks.txt", "a+") as file:
                        file.writelines(link['Linkedin'] + "\n")
                except:
                    with open("brokenLinks.txt", "w") as file:
                        file.writelines(link['Linkedin'] + "\n")
                link['Email'] = "404 Not Found"
                link['Phone_Number'] = "404 Not Found"
                link['Company Website'] = "404 Not Found"
                obj.write_data_v2(link)
                continue
            print("Checking with Apollo")
            print("Data Count: "+str(data_count))
            data_count+=1
            try:
                email, number = obj.scrape_apollo(link['Linkedin'])
            except:
                email,number=None
            if email == None:
                try:
                    # print("Checking with Salesql")
                    # email=obj.scrape_salesql(link[6])
                    if email == None:
                        # call kendo here
                        print("Checking with Kendo")
                        email = obj.scrape_kendo(link['Linkedin'])
                        if email == None:
                            print("Checking with Pipileads")
                            email = obj.scrape_pipileads(link['Linkedin'])
                except:
                    pass
            # write data
            if email == None:
                email = "NA"
                link['Company Website'] = "NA"
            else:
                print(email)
                try:
                    if "@gmail.com" in email or "@yahoo.com" in email or "@gmx.com" in email or "@mail.ru" in email:
                        link['Company Website'] = "NA"
                    else:
                        try:
                            link['Company Website'] = email.split("@")[1]
                        except:
                            link['Company Website'] = "NA"
                except:
                    link['Company Website'] = "NA"
            link['Email'] = email
            if number == None:
                number = "NA"
            else:
                if "+" not in number:
                    number = "+" + number

            link['Phone_Number'] = number.replace("-", "").replace("/", "").replace("\\", "").replace(")", "").replace("(",
                                                                                                          "").replace(
                " ", "")
            obj.write_data_v2(link)

print("Done")

