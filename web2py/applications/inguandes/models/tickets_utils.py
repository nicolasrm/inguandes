# -*- coding: utf-8 -*-

def get_ticket_categories(db, instanceId):
    categories = db(db.ticket_category_index.instance==instanceId).select(db.ticket_category_index.id, db.ticket_category_index.name).as_list()
    cats = [c['name'] for c in categories]
    return cats, categories
    
def get_ticket_categories_with_sub_for_user(db, instanceId):
    categories = db(db.ticket_category_index.instance==instanceId).select()
    cats = {}
    #for c in categories:
        
    cats = [c['name'] for c in categories]
    return cats, categories