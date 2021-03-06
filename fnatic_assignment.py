# -*- coding: utf-8 -*-
"""Fnatic_Assignment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kX2Aawpj_-OTTPdeZQEpYzZj0qJBJO7C

# Authentication
"""

consumer_key = "qrFc9MpTjevRJNI26tqv6cPI6"
consumer_secret = "EMD8tz2tDZm90EGelRJ8xQJ6hwcbXYrbdrs7P63qzaSGFkk7a5"
access_token = "1485865180047491076-PiK2P4wi6AN9t7EWomYttmP5PVMssX"
access_token_secret = "mLnAVrwUjn4AVyIaUvZsAyDEKN90WfSW8Hl3OOcuPs64n"


import os
import sys
import json
import math
from tweepy import Cursor
import tweepy
from tweepy import OAuthHandler
import datetime
import time
import numpy as np
from collections import Counter
from random import sample
import pandas as pd
from datetime import datetime


auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

screen_name = "FNATIC"

def UserStatuses(): #Extract user timeline
    fName = "{}.json".format(screen_name)
    with open(fName, 'w') as f:
        for tweet in tweepy.Cursor(api.user_timeline, screen_name).items():
                f.write(jsonpickle.encode(tweet._json, unpicklable=False) + '\n')
                #print(tweet.text + '\t' + str(tweet.created_at))
        print("\n")
        
UserStatuses()

def User_Followers(): #Extract 15,000 of user followers

    MAX_FRIENDS = 15000
    def paginate(items, n):
        """Generate n-sized chunks from items"""
        for i in range(0, len(items), n):
            yield items[i:i+n]

    print("collecting data for " + screen_name)
    max_pages = math.ceil(MAX_FRIENDS / 5000)

    fname = "{}_followers.json".format(screen_name)
    with open(fname, 'w') as f:
        for followers in Cursor(api.followers_ids, screen_name=screen_name).pages(max_pages):
            for chunk in paginate(followers, 100):
                users = api.lookup_users(user_ids=chunk)
                for user in users:                  
                    f.write(json.dumps(user._json)+"\n")                    
            if len(followers) == 5000:
                print("60 secs cooldown. Please wait while getting more data")
                time.sleep(60)
    print("Completed")
    
User_Followers()

def followerCountAbove():
    followers_file = '{}_followers.json'.format(screen_name)
    with open(followers_file) as f1:
        followers = []
        followersAbove1k = []
        for line in f1:
            profile = json.loads(line)
            followers.append([profile['screen_name'], profile['followers_count']])
            if(profile['followers_count']>=1000):
                followersAbove1k.append([profile['screen_name'], profile['followers_count']])

        percentage = (len(followersAbove1k)/len(followers))*100
        print("%.2f" % percentage,"% of followers have more than 1000 followers")

followerCountAbove()

def UserFollowerFriend(): #Get user's follower centrality
    followers_file = '{}_followers.json'.format(screen_name)
    with open(followers_file) as f1:
      followers = []
      for line in f1:
          profile = json.loads(line)
          followers.append([profile['screen_name'], profile['friends_count'], profile['followers_count'], (profile['followers_count']+profile['friends_count'])])

          new_list = sorted(followers, key=lambda x : x[3],reverse=True)[:5]
      for item in new_list:
          print("@",item[0], "\nNumber of friends:", item[1], "\nNumber of followers:", item[2], "\nCentrality of followers and friends:", item[3], "\n")

UserFollowerFriend()

def TopTweets(): #Exctract user top 5 tweets
    timeline_file1 = '{}.json'.format(screen_name)
    count = 0
    tweets = []
    with open(timeline_file1) as f1:
        for line in f1:
            tweet = json.loads(line)
            tweets.append([tweet['text'], tweet['retweet_count'], tweet['favorite_count'], (tweet['retweet_count']+tweet['favorite_count'])])
    
        tweets = sorted(tweets, key=lambda x: x[3], reverse = True)
            
        for r in tweets:
            if count < 5:
                print("Tweet no.{}".format(count+1))
                cnt = 0
                for c in r:
                    if cnt == 0:
                        print(c,end = " ")
                        cnt = cnt + 1
                    elif cnt == 1:
                        print("Retweet:", c, end = " ")
                        cnt = cnt + 1
                    elif cnt == 2:
                        print("Favorite:", c, end = " ")
                        cnt = cnt + 1
                    elif cnt == 3:
                        print("Total Engagement:", c, end = " ")
                        cnt = cnt + 1
                print('\n')
                count = count + 1

TopTweets()

def Hashtag(): #Extract user top 5 Hashtags
    def get_hashtags(tweet):
        entities = tweet.get('entities', {})
        hashtags = entities.get('hashtags', [])
        return [tag['text'].lower() for tag in hashtags]

    total=0
    fName = "{}.json".format(screen_name)
    tweets = []
    with open(fName, 'r') as f:
        for line in f:
            tweet = json.loads(line)
            if ((get_hashtags(tweet) != []) and (tweet.get('in_reply_to_status_id') is None) and (tweet.get('retweeted_status') is None)):                
                tweets.append([get_hashtags(tweet), (tweet['retweet_count'] + tweet['favorite_count'])])
        #for a in tweets:
        df = pd.DataFrame(tweets, columns = ['Hashtags', 'Total'])
        df['Hashtags'] = df['Hashtags'].astype(str).str.replace('[','')
        df['Hashtags'] = df['Hashtags'].astype(str).str.replace(']','')
        df['Hashtags'] = df['Hashtags'].astype(str).str.replace("'",'')
        df= df.groupby(['Hashtags']).sum().sort_values(by=['Total'], ascending = False)[:5]
        df = df.reset_index()
        print(df)
        
        a = df.to_numpy()

Hashtag()

def Mentions(): #Extract user top 5 mentions
    def get_mentions(tweet):
        entities = tweet.get('entities', {})
        mentions = entities.get('user_mentions', [])
        return [tag['screen_name'] for tag in mentions]

    total=0
    fName = "{}.json".format(screen_name)
    tweets = []
    with open(fName, 'r') as f:
        for line in f:
            tweet = json.loads(line)
            if ((get_mentions(tweet) != []) and (tweet.get('retweeted_status') is None)):                
                tweets.append([tweet['text'], get_mentions(tweet), (tweet['retweet_count'] + tweet['favorite_count'])])

        #for a in tweets:
        df = pd.DataFrame(tweets, columns = ['Text','Mentions', 'Total'])
        del df['Text']
        df['Mentions'] = df['Mentions'].astype(str).str.replace('[','')
        df['Mentions'] = df['Mentions'].astype(str).str.replace(']','')
        df['Mentions'] = df['Mentions'].astype(str).str.replace("'",'')
        df= df.groupby(['Mentions']).sum().sort_values(by=['Total'], ascending = False)[:5]
        print(df)

Mentions()

def Avg_Engagement(): #Get the user average engagement for every tweet
    fName = "{}.json".format(screen_name)
    total_Engagement = 0
    total_Tweets = 0
    with open(fName, 'r') as f:
        for line in f:
            tweet = json.loads(line)
            if ((tweet.get('in_reply_to_status_id') is None) and (tweet.get('retweeted_status') is None)): 
                total_Tweets = total_Tweets + 1
                total_Engagement = total_Engagement + (tweet['retweet_count'] + tweet['favorite_count'])
        print("Total Retweet:",total_Engagement)
        print("Total Favorite:",total_Tweets)
        print("Average Engagement on a tweet:",(total_Engagement/ total_Tweets))

Avg_Engagement()
