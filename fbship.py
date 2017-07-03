import requests
import pandas as pd

graph_api_version = 'v2.9'
access_token = 'your token here'

# Get a generic url here, we are gonna use it a few times
url = 'https://graph.facebook.com/{}/'.format(graph_api_version)

# I happily added an input function just so you can get a search term at will
searchkey = input("enter your keyword here:")
search_url = 'search?type=page&q={}'.format(searchkey)
page_id=[]
iddict={}

r = requests.get(url+search_url, params={'access_token': access_token})
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

# Put the list in Dataframe and then preview
df = pd.Dataframe(page_id)
df.head()

#Now we get the posts for each id
for id in page_id:
    r = requests.get(url+id+'/feed', params={'access_token': access_token})
    data = r.json()
    
    # catch errors returned by the Graph API, we always try to
    if 'error' in data:
        raise Exception(data['error']['message'])
    
    #Create a list for each id
    condict = {}
        
    #Extract the message
    for msg in data['data']:
        condict['Post_id']= post_id =msg['id']   
        condict['Post']=msg['message']     
        
        #Now get stuff from the post itself
        #First we do reactions
        #Initialize some stuff
        like_count = haha_count = love_count = wow_count = sad_count = angry_count = pride_count = 0
        comment_count = 0
        r = requests.get(url+post_id+'/reactions', params={'access_token': access_token})
        while True:
            data = r.json()
    
            # catch errors returned by the Graph API, we always try to
            if 'error' in data:
                raise Exception(data['error']['message'])
   
            for react in data['data']:
                if react['type'] == 'like':
                    like_count +=1
                if react['type'] == 'love':
                    love_count +=1
                if react['type'] == 'wow':
                    wow_count +=1
                if react['type'] == 'haha':
                    haha_count +=1
                if react['type'] == 'sad':
                    sad_count +=1
                if react['type'] == 'angry':
                    angry_count +=1
                if react['type'] == 'pride':
                    pride_count +=1
            if 'paging' in data and 'next' in data['paging']:
                r = requests.get(data['paging']['next'])
            else:
                break
        reactions = {'Like':like_count,'Love':love_count,'Wow':wow_count,'Haha':haha_count,'Sad':sad_count,'Angry':angry_count,'Pride':pride_count}
        condict.update(reactions)
        
        #Then we get comments, but we'll just get the total count
        r = requests.get(url+post_id+'/reactions', params={'access_token': access_token})
        while True:
            data = r.json()            
            # catch errors returned by the Graph API, we always try to
            if 'error' in data:
                raise Exception(data['error']['message'])
            for comm in data['data']:
                comment_count +=1
            if 'paging' in data and 'next' in data['paging']:
                r = requests.get(data['paging']['next'])
            else:
                break
        condict['Comments']=comment_count
        #Last but not least, get the shares
        r = requests.get(url+post_id+'?fields=shares', params={'access_token': access_token})
        data = r.json()
        if 'error' in data:
            raise Exception(data['error']['message'])
        condict['Shares']=data['shares']['count']}
    #Append the generated information into the database
    df = df.append({'Message':'Like':like_count,'Love':love_count,'Wow':wow_count,'Haha':haha_count,'Sad':sad_count,'Angry':angry_count,'Pride':pride_count,'Comments':comment_count,'Shares':data['shares']['count']}, ignore_index=True)
    
   
