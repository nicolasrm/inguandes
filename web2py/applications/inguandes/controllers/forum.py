# -*- coding: utf-8 -*-
import datetime

@auth.requires_login()
def forum():
    if len(request.args) == 0:
        redirect(URL('default', 'index'))
    instanceId = int(request.args[0])
    
    user_role = get_user_role(db, instanceId, auth.user.id)    
    forum_info = get_instance_forum(db, instanceId)
    
    topicId = int(request.args[1]) if len(request.args) > 1 else None
    topic_info = forum_info['topics_dict'][topicId] if topicId is not None else None
    thread_list = get_topic_threads(db, topic_info) if topic_info is not None else None
    thread_detail = get_thread_detail(db, [th for th in thread_list if th['id'] == int(request.args[2])][0]) if len(request.args) > 2 else None
            
    return dict(forum_info=forum_info, topic_info=topic_info, thread_list=thread_list, thread_detail=thread_detail, user_role=user_role)
    
@auth.requires_login()
def add_topic():
    instanceId = int(request.vars.instanceid)
    if request.vars.name is not None:
        db.forum_topic.insert(  name=request.vars.name,
                                instance=instanceId)
    redirect(URL('forum', args=[instanceId]))
    
@auth.requires_login()
def add_thread():
    instanceId = int(request.vars.instanceid)
    topicId = int(request.vars.topicid)
    if request.vars.title is not None and request.vars.content is not None:
        db.forum_thread.insert( title=request.vars.title,
                                content=request.vars.content,
                                the_user=auth.user.id,
                                forum_topic=topicId)
    redirect(URL('forum', args=[instanceId, topicId]))
    
@auth.requires_login()
def add_post():
    instanceId = int(request.vars.instanceid)
    topicId = int(request.vars.topicid)
    threadId = int(request.vars.threadid)
    
    if request.vars.content is not None:
        db.forum_post.insert(   content=request.vars.content,
                                the_user=auth.user.id,
                                forum_thread=threadId)
    redirect(URL('forum', args=[instanceId, topicId, threadId]))
    
@auth.requires_login()
def best_answer():
    if len(request.args) < 4:
        redirect(URL('default', 'index'))
    instanceId = int(request.args[0])
    topicId = int(request.args[1])
    threadId = int(request.args[2])
    postId = int(request.args[3])
    
    db((db.forum_post.forum_thread == threadId) & (db.forum_post.best_answer == True)).update(best_answer=False)
    
    post = db.forum_post[postId]
    post.update_record(best_answer=True)
    
    redirect(URL('forum', args=[instanceId, topicId, threadId]))
    
@auth.requires_login()
def remove_post():
    if len(request.args) < 4:
        redirect(URL('default', 'index'))
    instanceId = int(request.args[0])
    topicId = int(request.args[1])
    threadId = int(request.args[2])
    postId = int(request.args[3])
    
    post = db.forum_post[postId]
    post.update_record(available=False)
    
    redirect(URL('forum', args=[instanceId, topicId, threadId]))
