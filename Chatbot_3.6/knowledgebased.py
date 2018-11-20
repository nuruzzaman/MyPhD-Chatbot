import mysql.connector
import collections
import colorama

colorama.init()

# Knowledge-based (KDD)Search
def kdd_search(entityList):     
    
    try:
        # Connect to MySQL Database 
        connection = mysql.connector.connect(host='localhost',
                                 database='aichatbot',
                                 user='root',
                                 password='soho123')
                                 
        if connection.is_connected():
           db_Info = connection.get_server_info()
           #print("Connected to MySQL database... MySQL Server version on ",db_Info)
           dbcursor = connection.cursor()
           #dbcursor.execute("select database();")
           #record = dbcursor.fetchone()
           #print ("Your connected to - ", record)
           
           queryResultList=[]
           row_count=0
           for entity in entityList:
               mysqlstatement = 'SELECT id, response_count, tag_id, question, response_message, keywords, message_type FROM knowledgebase WHERE question like\'%'+entity+'%\' OR keywords like\'%'+entity+'%\' OR response_message like\'%'+entity+'%\'  '
               dbcursor.execute(mysqlstatement)
               qres = dbcursor.fetchall()
               for res in qres:
                   queryResultList.append(res)                    
                   row_count = row_count + dbcursor.rowcount
                   #print(row_count)
                   
           print(colorama.Fore.YELLOW+'\n---------------- Database Query Result ----------------- '+colorama.Fore.RESET)
           i=0
           for result in queryResultList:
               i = i+1
               print('### ', i, '### ', result)
           print('----------------------------------------------------------\n ') 
           
           ans_reply = ''
           ans_id = 0 
           response_count = 0
           if (row_count ==0):
               # retrun empty for Web Search and RNN functions 
               ans_reply = '' 
           elif (row_count ==1):
               ans_id = queryResultList[0][0]
               response_count = queryResultList[0][1]
               ans_reply = queryResultList[0][4]
           else:
               # Identify records that are duplicate
               #ans_reply = [item for item, count in collections.Counter(queryResultList).items() if count > 1]
               #ans_id = ans_reply[0][0]
               #response_count = queryResultList[0][1]
               #ans_reply = ans_reply[0][4]
               
               # Remove duplicate records 
               print(colorama.Fore.YELLOW+'\n---------------- After Removing Duplicate Records ----------------- '+colorama.Fore.RESET)
               no_duplicate = set(queryResultList)
               print(set(queryResultList)) 
                
               if(len(no_duplicate) > 1):
                   print(colorama.Fore.YELLOW+'\nFound more than one records'+colorama.Fore.RESET)
                   response = sqlforMinimizeRecords(entityList, no_duplicate, dbcursor) 
                   ans_id = response[0][0]
                   response_count = response[0][1]
                   ans_reply = response[0][4]
            
               elif(len(no_duplicate) == 1):
                   # After removing duplicate, if only one record
                   ans_id = queryResultList[0][0]
                   response_count = queryResultList[0][1]
                   ans_reply = queryResultList[0][4]
               else:
                   ans_reply = ''
               
           # Update databse that how many times question being answered  
           
    
        return ans_reply
    
    except Error as e :
        print ("Error while connecting to MySQL", e)
    finally:
        # Closing database connection
        if(connection.is_connected()):
            dbcursor.close()
            connection.close()
            #print("MySQL connection is closed")


def sqlforMinimizeRecords(entityList, no_duplicate, dbcursor):
    ans_reply= []
    row_count = 0
    
    if(len(entityList) ==1):
        entityList.append(entityList[0])
    
    
    # Loop all entities through SQL 
    for entity in entityList:
        mysqlstatement = 'SELECT id, response_count, tag_id, question, response_message, keywords, message_type FROM knowledgebase WHERE question like\'%'+entity+'%\' OR keywords like\'%'+entity+'%\' OR response_message like\'%'+entity+'%\' HAVING response_message like\'%'+entityList[0]+'%\' AND response_message like\'%'+entityList[1]+'%\'  '
        dbcursor.execute(mysqlstatement)
        qres = dbcursor.fetchall()
        row_count = dbcursor.rowcount
        
    if (row_count >0):
        print(colorama.Fore.YELLOW+'---------------- SQL for Minimize Records ----------------- '+colorama.Fore.RESET)
        print(qres)
        ans_reply = qres
        print('------------------------------------------------------------\n ')
        
    return ans_reply

        
if __name__ == '__main__':
    print (kdd_search('Knowledge-based (KDD)Search'))
