import requests
import pandas as pd

graph_api_version = 'v2.9'
access_token = input("Copy and paste your Facebook access token here:")

# Get a generic url here, we are gonna use it a few times
url = 'https://graph.facebook.com/{}/'.format(graph_api_version)

# I happily added an input function just so you can get a search term at will
searchkey = input("Enter your keyword here:")
search_url = 'search?type=page&q={}'.format(searchkey)
page_id=[]
iddict={}
print ("Just so you know, the process will take a few minutes. Please be patient...")

r = requests.get(url+search_url, params={'access_token': access_token})
print ("Getting page IDs now...")
while True:
    data = r.json()

    # catch errors returned by the Graph API
    if 'error' in data:
        raise Exception(data['error']['message'])

    # Get a list of all the ids
    for id in data['data']:
        page_id.append(id['id'])

    # Get even more ids
    if 'paging' in data and 'next' in data['paging']:
        r = requests.get(data['paging']['next'])
    else:
        break

#Create a list for each id
indx_list=[]
post_id_list = []
id_ext_list=[]
msg_list = []
postlink_list=[]
like_list=[]
love_list=[]
haha_list=[]
wow_list=[]
sad_list=[]
angry_list=[]
pride_list=[]
comment_list=[]
share_list=[]
print ("Done! Moving on to individual posts per ID...")
n = 0

#Now we get the posts for each id
for id in page_id:
    n += 1
    r = requests.get(url+id+'/feed', params={'access_token': access_token})
    print ("Going through ",n," page(s) now...")
    m=1
    while True:
        data = r.json()
    
        # catch errors returned by the Graph API, we always try to
        if 'error' in data:
            raise Exception(data['error']['message'])

        #Extract the message
        for msg in data['data']:
            post_id =msg['id']
            impmsg=msg.get('message','NULL')
            print ("Going through ",m," post...")
            
            #Now get stuff from the post itself
            #First we do reactions
            #Initialize some stuff
            like_count = haha_count = love_count = wow_count = sad_count = angry_count = pride_count = 0
            comment_count = 0
            
            ra = requests.get(url+post_id+'/reactions', params={'access_token': access_token})
            while True:
                dataa = ra.json()
    
                # catch errors returned by the Graph API, we always try to
                if 'error' in dataa:
                    raise Exception(dataa['error']['message'])
                
                for react in dataa['data']:
                    if react['type'] == 'LIKE':
                        like_count +=1
                    if react['type'] == 'LOVE':
                        love_count +=1
                    if react['type'] == 'WOW':
                        wow_count +=1
                    if react['type'] == 'HAHA':
                        haha_count +=1
                    if react['type'] == 'SAD':
                        sad_count +=1
                    if react['type'] == 'ANGRY':
                        angry_count +=1
                    if react['type'] == 'PRIDE':
                        pride_count +=1
                if 'paging' in dataa and 'next' in dataa['paging']:
                    ra = requests.get(dataa['paging']['next'])
                    print ("No. of likes:",like_count)
                else:
                    break
        
            #Filter out the 'unpopular' posts
            if sum([like_count,love_count,wow_count,haha_count,sad_count,angry_count,pride_count]) <100:
                print ("One post down the drain!")
                continue
            else:
                like_list.append(like_count)
                love_list.append(love_count)
                haha_list.append(haha_count)
                wow_list.append(wow_count)
                sad_list.append(sad_count)
                angry_list.append(angry_count)
                pride_list.append(pride_count)
                post_id_list.append(post_id)
                msg_list.append(impmsg)
                postlink_list.append("http://www.facebook.com/"+post_id)
                id_ext_list.append(id)
                indx_list.append(str(n)+'-'+str(m))
        
            #Then we get comments, but we'll just get the total count
            rb = requests.get(url+post_id+'/reactions', params={'access_token': access_token})
            while True:
                datab = rb.json()            
                # catch errors returned by the Graph API, we always try to
                if 'error' in datab:
                    raise Exception(datab['error']['message'])
                print ("Counting no. of comments")
                for comm in datab['data']:
                    comment_count +=1
                if 'paging' in datab and 'next' in datab['paging']:
                    rb = requests.get(datab['paging']['next'])
                else:
                    break
            comment_list.append(comment_count)

            #Last but not least, get the shares
            rc = requests.get(url+post_id+'?fields=shares', params={'access_token': access_token})
            datac = rc.json()
            if 'error' in datac:
                raise Exception(datac['error']['message'])
            print ("Getting no. of shares")
            try:
                share_list.append(datac['shares']['count'])
            except:
                share_list.append(0)
            m += 1
        
        # Get even more posts
        if 'paging' in data and 'next' in data['paging']:
            r = requests.get(data['paging']['next'])
        
        else:
            break

#Now that we have the list of messages with all the likes, shares and comments, put them into a dictionary!
condict = {'ID':id_ext_list, 'Post ID':post_id_list, 'Message':msg_list, 'Likes':like_list, 'Love':love_list, 'Wow':wow_list, 'Haha':haha_list, 'Sad':sad_list, 'Angry':angry_list, 'Pride':pride_list, 'No. Comments':comment_list, 'No. Shares':share_list, 'Facebook link':postlink_list}
df = pd.DataFrame(condict, index=indx_list, columns=['ID','Post ID','Message','Likes','Love','Wow','Haha','Sad','Angry','Pride','No. Comments','No. Shares','Facebook link'])

print ("Saving file...")
#Last but not least, write it to a excel file
writer = pd.ExcelWriter('Search results.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name=searchkey)
writer.save()

