# -*- coding: utf-8 -*-
import datetime
import random

def get_instance_forum(db, instanceId):
    topics = db((db.forum_topic.instance==instanceId) & (db.forum_topic.available == True)).select(orderby=db.forum_topic.name)
    
    forum_info = {}
    forum_info['instance'] = db.instance[instanceId].title
    forum_info['instance_id'] = instanceId
    forum_info['topics'] = [get_topic_info(db, t.id) for t in topics]
    forum_info['topics_dict'] = {t['id'] : t for t in forum_info['topics']}
    
    return forum_info
    
def get_topic_info(db, topicId):
    topic = db.forum_topic[topicId]
    threads = db((db.forum_thread.forum_topic == topicId) & (db.forum_thread.available == True)).select()
    
    topic_info = {}
    topic_info['id'] = topicId
    topic_info['name'] = topic.name
    topic_info['count'] = len(threads)
    topic_info['threads'] = threads
    
    return topic_info
    
def get_topic_threads(db, topic_info):
    threads = []
    for th in topic_info['threads']:
        posts = db((db.forum_post.forum_thread == th.id) & (db.forum_post.available == True)).select(orderby=db.forum_post.created_on)
        
        th_info = {}
        th_info['id'] = th.id
        th_info['topic'] = topic_info['id']
        th_info['title'] = th.title
        th_info['content'] = th.content
        th_info['user'] = db.auth_user[th.the_user]
        th_info['created'] = th.created_on
        th_info['is_open'] = th.open
        th_info['count'] = len(posts)
        th_info['posts'] = posts
        th_info['last_post'] = posts[0].created_on if len(posts) > 0 else None
        th_info['has_answer'] = len([p for p in th_info['posts'] if p.best_answer]) > 0 if len(posts) > 0 else False
        threads.append(th_info)
    
    return threads
    
def get_thread_detail(db, th_info):
    th_details = th_info
    post_details = []
    for p in th_info['posts']:
        p_info = {}
        p_info['id'] = p.id
        p_info['content'] = p.content
        p_info['user'] = db.auth_user[p.the_user]
        p_info['is_best_answer'] = p.best_answer
        p_info['created'] = p.created_on
        
        post_details.append(p_info)
        
    th_details['posts'] = post_details
    
    return th_details